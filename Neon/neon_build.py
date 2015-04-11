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
import shutil
import logging
import shlex
import tempfile
from neon_base import __call

logging.basicConfig(level=logging.DEBUG)

def install_shairport():
    build_dir = tempfile.mkdtemp()
    if call('/usr/bin/git clone https://github.com/abrasive/shairport.git ' + build_dir) != 0:
        # TODO add debug logging
        raise NeonInstallFailure("Could not find sources for shairport.")
    os.chdir(build_dir)
    if call(build_dir + '/configure') != 0:
        raise NeonInstallFailure("Could not run ./configure for shairport.")
    if call('/usr/bin/make') != 0:
        raise NeonInstallFailure("Could not run make for shairport.")
    if call('/usr/bin/make install') != 0:
        raise NeonInstallFailure("Could not run make install for shairport.")
    shutil.copyfile(build_dir + '/scripts/systemd/shairport.service',
            '/etc/systemd/system/shairport.service')
    if call('/usr/bin/systemctl enable shairport.service') != 0:
        logging.warn('could not mark shairport for auto-start on boot')

