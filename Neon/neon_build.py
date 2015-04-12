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
import shutil
import tempfile
from neon_base import __call

logging.basicConfig(level=logging.DEBUG)

def install_shairport():
    build_dir = tempfile.mkdtemp()
    fmsg = 'something went wrong in build'
    __call(['/usr/bin/git'],
            ['clone', 'http://github.com/abrasive/shairport.git', build_dir],
            fail_message=fmsg)

    os.chdir(build_dir)
    __call([build_dir + '/configure'], fail_message=fmsg)
    __call(['/usr/bin/make'], fail_message=fmsg)
    __call(['/usr/bin/make', 'install'], fail_message=fmsg)

    shutil.copyfile(build_dir + '/scripts/systemd/shairport.service',
            '/etc/systemd/system/shairport.service')

    __call(['/usr/bin/systemctl'], ['enable', 'shairport.service'],
            fail_message=fmsg)
