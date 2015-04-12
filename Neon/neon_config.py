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
import re
import logging
from neon_base import __call
from neon_exceptions import NeonInstallFail

logging.basicConfig(level=logging.DEBUG)


def config_shairport():
    if not os.path.lexists('/etc/conf.d/'):
        os.mkdir('/etc/conf.d/')
    with open('/etc/conf.d/shairport', 'w') as conf:
        # Todo: get name from user
        conf.write('SHAIRPORT_ARGS="--name=Neon \
            --log=/var/log/shairport.log --pidfile=/var/run/shairport"')

def config_alsa():
    with open('/usr/share/alsa/alsa.conf', 'r+') as f:
        config = f.read()
        f.seek(0,0)
        f.write(re.sub(r'^pcm.front cards.pcm.front', 'pcm.front cards.pcm.default', config))
        f.truncate()

    __call(['/usr/bin/amixer'], ['cset', 'numid=3', '1'],
            fail_message="couldn't run amixer.")
    __call(['/usr/bin/amixer'], ['set', 'PCM', '1.00dB'],
            fail_message="couldn't run amixer.")
