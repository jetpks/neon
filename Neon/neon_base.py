#!/usr/bin/env python

""" License
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
"""

""" Neon Installer Library

"""

import os
import logging
import shlex
from neon_exceptions import NeonInstallFail
from subprocess import call, check_output, CalledProcessError

logging.basicConfig(level=logging.DEBUG)

def __call(base, args=[], fail_message='', parser=False):
    """ parser is a function that will parse the output of whatever command
    command you're passing via base and args. Leave it false if you just want
    raw data back.
    fail_message is what we pass to NeonInstallFail
    args is an array (or a string if you trust shlex) of args that get passed
    to base.
    base is the command/args you want to run. e.g. ['/usr/bin/yum', '-e1', '-y']
    """
    # shlex it real good (separarate strings into lists based on shell
    # semantics) e.g. '-a -b -c' gets turned into ['-a', '-b', '-c']
    if isinstance(base, basestring):
        base = shlex.split(base)
    if isinstance(args, basestring):
        args = shlex.split(args)

    raw_out = ''
    logging.debug('running ' + str(base + args))
    try:
        raw_out = check_output(base + args)
    except(CalledProcessError) as e:
        logging.error("Problem running: %s" % e.cmd)
        logging.error("Exit Status: %s" % e.returncode)
        logging.error("Output: %s" % e.output)
        raise NeonInstallFail(fail_message)

    if parser:
        return parser(raw_out)
    return raw_out
