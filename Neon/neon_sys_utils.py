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

import logging
import dependencies
from neon_base import __call
logging.basicConfig(level=logging.DEBUG)

def update_sys():
    # Pretty much just `yum -y update`
    yum = ['/usr/bin/yum', '-e1', '-y']
    __call(yum, ['update'],
            fail_message="Unable to update system. Check your internet connection")

def install_deps():
    # Pretty much just `yum -y install <dependencies>`
    yum = ['/usr/bin/yum', '-e1', '-y', 'install']
    __call(yum, dependencies.get_dependencies(),
            fail_message="Unable to install required packages.")
