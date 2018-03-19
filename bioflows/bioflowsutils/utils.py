# BioLite - Tools for processing gene sequence data and automating workflows
# Copyright (c) 2012-2014 Brown University. All rights reserved.
#
# This file is part of BioLite.
#
# BioLite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BioLite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioLite.  If not, see <http://www.gnu.org/licenses/>.

"""
Utility functions used by other BioLite modules.
"""

import argparse
import fcntl
import io
import inspect
import hashlib
import os
import re
import resource
import subprocess
import sys
import tempfile
import time
import zipfile

from itertools import groupby
from traceback import print_stack

# A simple struct object with the keyword args as attributes.
Struct = argparse.Namespace


def die(*messages):
    """
    Prints the current BioLite module and an error `message`, then aborts.
    """
    sys.stderr.write("%s.%s: " % get_caller_info(trace=True))
    sys.stderr.write(' '.join(map(str, messages)))
    sys.stderr.write('\n')
    sys.exit(1)


def info(*messages):
    """
    Prints the current BioLite module and a `message`.
    """
    sys.stderr.write("%s.%s: " % get_caller_info())
    sys.stderr.write(' '.join(map(str, messages)))
    sys.stderr.write('\n')


def table(rows, convert=True):
    """
    Outputs the given `rows` as tabulated strings, similar to the output of the
    `column -t` UNIX command.

    The input `rows` variable is a list of lists, where the sublists all have
    the same length and contain the cells of the table. The output is a
    tabulated string for each sublist (row).
    """
    if rows:
        # Convert cells to strings.
        if convert:
            for i, row in enumerate(rows):
                rows[i] = tuple(str(cell) for cell in row)
        # Find the max widths for each column.
        widths = [0] * len(rows[0])
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))
        # Use the widths to create a format string.
        fmt = ' '.join('{:<%d}' % width for width in widths)
        # Output the formatted rows.
        for row in rows:
            yield fmt.format(*row)


def safe_mkdir(path):
    """
    Creates the directory, including any missing parent directories, at the
    specified `path`.

    Aborts if the path points to an existing regular file.

    Returns the absolute path of the directory.
    """
    if os.path.isfile(path):
        die("'{0}' is a regular file: can't overwrite" % path)
    elif os.path.isdir(path):
        info("directory '%s' already exists" % path)
    else:
        info("creating directory '%s'" % path)
        try:
            os.makedirs(path)
        except OSError as e:
            die("""failed to recursively create the directory
%s
%s
  Do you have write permission to that path?
  Or does part of that path already exist as a regular file?""" % (path, e))
    return os.path.abspath(path)


def safe_remove(path):
    """
    Removes a file at the given `path` only if it exists.
    """
    if os.path.isfile(path):
        os.remove(path)


def make_pipe():
    """
    Returns the path to a newly created named pipe at a temporary location.
    """
    tmpdir = tempfile.mkdtemp(prefix="bl-pipe-")
    path = os.path.join(tmpdir, "fifo")
    os.mkfifo(path)
    return path


def cleanup_pipe(path):
    """
    Remove a named pipe created by biolite.
    """
    os.remove(path)
    os.rmdir(os.path.dirname(path))


def truncate_file(path):
    """
    Truncates a file (i.e. overwrites with 0 bytes) at the given `path`.
    """
    open(path, 'w').close()


def rusage_diff(r1, r2):
    """
    Returns an rusage object where each field is the difference of the
    corresponding fields in `r1` and `r2`.
    """
    rdiff = [(f1 - f2) for f1, f2 in zip(r1, r2)]
    return resource.struct_rusage(rdiff)


def failed_executable(executable, e):
    """
    Diagnose why a wrapped executable failed to execute, and print an
    intelligble error message for the user.
    """
    if e.errno == 2:
        die("command not found: '%s'" % executable)
    elif e.errno == 8:
        die("""executable format error '{0}'
  Does '{0}' have the correct architecture (eg. 32-bit vs 64-bit)
  for the machine you are trying to run it on?""".format(executable))
    elif e.errno == 13:
        die("""permission denied for command '%s'
  Do you need to run 'chmod 755' on it?""" % executable)
    else:
        die("unknown error when executing '%s':\n%s" % (executable, e))


def safe_call(*args, **kwargs):
    """
    Calls an executable as a subprocess and checks the return value.

    All `args` and `kwargs` are passed to a `subprocess.Popen` call, except for
    the special keywords `return_ok`, whose value is used to check the return
    value of the subprocess. By default, this is zero and any non-zero return
    is considered an error. To disable this check, set `return_ok` to
    `None`.

    Returns a 3-tuple with the return code, the elapsed walltime, and an
    rusage structure with the elapsed usertime and systime.
    """
    return_ok = kwargs.pop('return_ok', 0)
    rusage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.time()
    try:
        p = subprocess.Popen(*args, **kwargs)
        p.wait()
    except OSError as e:
        failed_executable(args[0][0], e)
    walltime = time.time() - start
    rusage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
    retcode = p.returncode
    if (return_ok is not None) and (retcode != return_ok):
        # Give some context to the non-zero return, if stderr is available.
        if 'stderr' in kwargs:
            stderr = kwargs['stderr'].name
            if stderr and os.path.isfile(stderr):
                subprocess.call(['tail', '-3', stderr])
        die("non-zero return (%d) from command:\n%s" % (retcode, ' '.join(args[0])))
    return retcode, walltime, rusage_diff(rusage_end, rusage_start)


def safe_str(s):
    """
    Returns the string `s` with only alpha-numerical characters and the special
    characters :samp:`()[]{}|:.-_` preserved. All other characters are replaced
    by :samp:`_`.
    """
    valid_chars = frozenset(r"()[]{}|:.-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return ''.join(c if c in valid_chars else '_' for c in str(s))


def safe_taxon(s):
    """
    Returns the string `s` with only alpha-numerical characters and the special
    character :samp:`_` preserved. All other characters are replaced
    by :samp:`_`.
    """
    valid_chars = frozenset(r"_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return ''.join(c if c in valid_chars else '_' for c in str(s))


def timestamp():
    """
    Returns the current time in :samp:`YYYY-MM-DD HH:MM:SS` format.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")


def safe_print(f, line):
    """
    Places an exclusive lock around the file object `f` and writes `line` to
    it as an atomic write operation.

    A line return is appended after `line`.
    """
    fcntl.lockf(f, fcntl.LOCK_EX)
    f.seek(0, io.SEEK_END)
    f.write(line + '\n')
    fcntl.lockf(f, fcntl.LOCK_UN)


def readlines_reverse(f):
    """
    Seeks to the end of the file object `f` and yields lines in reverse order.
    """
    # Seek to end of file.
    f.seek(0, 2)
    blocksize = 32 * 1024
    last_row = ''
    while f.tell() != 0:
        try:
            f.seek(-blocksize, 1)
        except IOError:
            blocksize = f.tell()
            f.seek(-blocksize, 1)
        block = f.read(blocksize)
        f.seek(-blocksize, 1)
        rows = block.split('\n')
        rows[-1] = rows[-1] + last_row
        while rows:
            last_row = rows.pop(-1)
            if rows and last_row:
                yield last_row
        yield last_row


def cat_to_file(input_path, output_path, mode='a', start=0):
    """
    Uses the :command:`cat` or :command:`awk` command to copy the contents
    at `input_path` to `output_path`, starting at line 0 of `input_path`
    and appending to `output_path` by default.
    """
    with open(output_path, mode) as f:
        if start > 0:
            ret = subprocess.call(['awk', 'NR>%d' % start, input_path], stdout=f)
        else:
            ret = subprocess.call(['cat', input_path], stdout=f)
    return ret


def head(path, n=1):
    """
    Returns a string with the first `n` lines of `path`.
    """
    return subprocess.check_output(['head', '-n', str(n), path])


def head_to_file(input_path, output_path, n=1, mode='w', gunzip=False):
    """
    Uses the :command:`head` to copy the first `n` lines of `input_path` to
    `output_path`, overwriting the contents of `output_path` by default.
    """
    with open(output_path, mode) as f:
        if gunzip:
            ret = subprocess.call(
                ["gzip -dc %s | head -n %d" % (input_path, n)],
                shell=True, stdout=f)
        else:
            ret = subprocess.call(['head', '-n', str(n), input_path], stdout=f)
    return ret


def tail(path, n=1):
    """
    Returns a string with the last `n` lines of `path`.
    """
    return subprocess.check_output(['tail', '-n', str(n), path])


def tail_to_file(input_path, output_path, n=1, mode='w'):
    """
    Uses the :command:`head` to copy the last `n` lines of `input_path` to
    `output_path`, overwriting the contents of `output_path` by default.
    """
    with open(output_path, mode) as f:
        ret = subprocess.call(['tail', '-n', str(n), input_path], stdout=f)
    return ret


def count_lines(filename):
    """
    Fast function to count lines in a file, from:
    http://stackoverflow.com/a/850962/781673
    """
    f = open(filename)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read  # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines


def get_caller_info(depth=2, trace=False):
    """
    Uses the inspect module to determine the name of the calling function and
    its module.

    Returns a 2-tuple with the module name and the function name.
    """
    try:
        frame = inspect.stack()[depth]
    except:
        die("could not access the caller's frame at stack index %d" % depth)
    if trace:
        print_stack(frame[0].f_back)
    func = frame[3]
    module = inspect.getmodule(frame[0])
    if module:
        return (module.__name__, func)
    else:
        return ('<unknown>', func)


def get_caller_locals(depth=2):
    """
    Uses the inspect module to return a dictionary of the local variables in
    the caller's frame at the given `depth`. The default `depth` of 2
    corresponds to the frame that calls this function.
    """
    try:
        frame = inspect.stack()[depth]
    except:
        die("could not access the caller's frame at stack index %d" % depth)
    return frame[0].f_locals


class AttributeDict(dict):
    """
    A mutable alternative to namedtuple that supports accessing values as
    attributes or with the dict [] operator.
    """

    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self._initialized = True

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if hasattr(self, '_initialized'):
            super(AttributeDict, self).__setitem__(name, value)
        else:
            super(AttributeDict, self).__setattr__(name, value)


def sorted_alphanum(l):
    """
    Sorts a list of strings `l` and returns a list with the elements in
    alpha-numerical order (i.e. strings starting with numbers are correctly
    ordered by numerical value).
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def memusage():
    """
    Reads the current memory usage for this process from /proc/self/status
    and returns two integer values `mem` and `vmem` which correspond to the
    VmHWM (max physical memory) and VmPeak (max virtual memory) fields.

    *Note*: only works on Linux.
    """
    mem = 0
    vmem = 0
    with open('/proc/self/status', 'r') as f:
        for line in f:
            if line[:6] == 'VmPeak':
                vmem = int(line.split()[1])
            elif line[:5] == 'VmHWM':
                mem = int(line.split()[1])
    return mem, vmem


def which(executable):
    """
    Returns the full path to `executable` by searching through all entries in the
    $PATH environment variable, and looking for an executable file with that
    name.

    Returns `None` if the executable is not found.
    """
    fpath, fname = os.path.split(executable)
    if fpath and os.path.exists(executable):
        return os.path.realpath(executable)
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            executable = os.path.join(path, fname)
            if os.path.exists(executable):
                return os.path.realpath(executable)
    return None


def basename(path):
    """
    Finds the base filename of the path, than the base of the filename
    (everything before the last .extension).
    """
    return os.path.splitext(os.path.basename(path))[0]


def zipdir(dirname):
    """
    Recursively zips all files in `dirname` into a zip archive with the name
    `dirname.zip` in the current working directory.
    """
    with zipfile.ZipFile(dirname + '.zip', 'w') as zf:
        for root, _, files in os.walk(dirname):
            for f in files:
                zf.write(os.path.join(root, f))


def number_range(numbers):
    """
    Collapse a list of numbers into a list of range strings, following
    http://stackoverflow.com/questions/9470611/how-to-do-an-inverse-range-i-
    """
    ranges = []
    for k, it in groupby(enumerate(sorted(numbers)), lambda x: x[1] - x[0]):
        rng = list(it)
        if len(rng) == 1:
            s = str(rng[0][1])
        else:
            s = "%s-%s" % (rng[0][1], rng[-1][1])
        ranges.append(s)
    return ranges


def bytes_to_gb(b):
    """
    Returns a string representing the given number of bytes as GB.
    """
    gb = float(b) / (2 ** 30)
    if gb < 1.0:
        return '%f' % gb
    else:
        return '%.1f' % gb


def mem_to_mb(mem):
    """
    Convert a memory string, like 2G or 100mb, to an integer number of
    megabytes.
    """
    factor = 1
    index = -1
    if mem.endswith('G') or mem.endswith('g'):
        factor = 1024
    elif mem.endswith('gb') or mem.endswith('Gb') or mem.endswith('GB'):
        factor = 1024
        index = -2
    elif mem.endswith('m') or mem.endswith('M'):
        pass
    elif mem.endswith('mb') or mem.endswith('Mb') or mem.endswith('MB'):
        index = -2
    else:
        die("unrecognized memory value '%s'" % mem)
    try:
        return int(mem[:index]) * factor
    except ValueError as e:
        die("can't convert memory value '%s' to an integer" % mem[:index])


def md5sum(path):
    """
    Use hashlib.md5() to calculate the MD5 hash of a file at `path`.
    """

    chunks = hashlib.md5()

    # Build hash from 64KB chunks of the binary file.
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), ""):
            chunks.update(chunk)

    return chunks.hexdigest()


def md5seed(s):
    """
    Calculate the integer MD5 hash of the string `s` to use as a random seed
    for enabling deterministic output in programs that allow setting the seed
    (e.g. RAxML).

    Return the integer as a string, to simplfy passing it as an argument to a
    program.
    """
    seed = hashlib.md5()
    seed.update(s)
    return int(seed.hexdigest(), 16)


def human_readable_size(kb, prec):
    """
    Returns a integer number of kilobytes as a string with closest matching
    size of KB, MB, GB, or TB with `prec` number of digits.
    """
    l = len(str(kb))
    try:
        fkb = float(kb)
    except ValueError:
        return '-'
    if l <= 3:
        out = '%s KB' % str(kb)
    elif l <= 6:
        out = '%.*f MB' % (prec, fkb / 1024.0)
    elif l <= 9:
        out = '%.*f GB' % (prec, fkb / 1048576.0)
    else:
        out = '%.*f TB' % (prec, fkb / 1073741824.0)
    return out


def multimap(funcs, values):
    """
    Apply each function in the list `funcs` to the corresponding argument in
    the list `args`. Both lists must have the same length.
    """
    assert len(funcs) == len(values)
    for func, value in zip(funcs, values):
        yield func(value)


def newick_to_json(newick_string):
    """
    Convert the given string in Newick format to a JSON encoded equivalent object.

    Derived from: http://pastebin.com/Pk717Uc2
    """

    def parseNode(newick_string):
        parenCount = 0

        tree = ''
        processed = ''
        index = 0
        for char in newick_string:
            if char == "(":
                parenCount += 1
                if parenCount == 1:
                    continue
            elif char == ")":
                parenCount -= 1
                if parenCount == 0:
                    if index + 2 > len(newick_string):
                        break
                    else:
                        tree = newick_string[index + 2:]
                        break

            if char == ",":
                if parenCount != 1:
                    processed += "|"
                else:
                    processed += ","
            else:
                processed += char

            index += 1

        data = processed.split(',')

        for i in range(len(data)):
            data[i] = data[i].replace('|', ',')

        t = tree.strip()
        if t.find(":") == -1:
            label = t
            distance = ""
        else:
            label = t[:t.find(":")]
            distance = t[t.find(":") + 1:]

        return (label, distance, data)

    newick_string = newick_string.replace(";", "")
    if newick_string.find('(') == -1:
        if len(newick_string.split(',')) == 1:
            if newick_string.find(":") == -1:
                label = newick_string
                distance = ""
            else:
                label = newick_string[:newick_string.find(":")]
                distance = float(newick_string[newick_string.find(":") + 1:])
            return {"label": label, "distance": distance}
        else:
            return newick_string.split(',')
    else:
        label, distance, data = parseNode(newick_string)

        dataArray = []
        for item in data:
            dataArray.append(newick_to_json(item))

        return {"label": label, "distance": distance, "tree": dataArray}


def write_fasta(f, seq, *headers):
    """
    """
    f.write('>')
    f.write(' '.join(map(str, headers)))
    f.write('\n')
    f.write(str(seq))
    f.write('\n')


def indent(n, text, space='\t'):
    """
    Re-indent `text` so that each line starts with `n` copies of `space`.
    """
    tab = space * n
    return '\n'.join(tab + line.lstrip(space) for line in text.split('\n'))


def none_to_empty(text):
    """
    Check if a text value is None, and if so return an empty string.
    """
    if text is None:
        return ""
    else:
        return text

# vim: noexpandtab ts=4 sw=4
