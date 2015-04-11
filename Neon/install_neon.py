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
import sys
import shlex
import shutil
import string
import logging
import tempfile
import dependencies
from subprocess import call, check_output, CalledProcessError
#from ask import ask
from neon_exceptions import NeonInstallFail

logging.basicConfig(level=logging.DEBUG)

def __call_parted(fail_message, command, raw=False):
    """raw=True will return raw unparsed parted output.
    """
    parted = ['/usr/sbin/parted', '-ms', '--']
    cmd = list()
    raw_output = ''
    if isinstance(command, basestring):
        cmd = shlex.split(command)
    else:
        cmd = command
    try:
        logging.debug('running ' + str(parted + cmd))
        raw_output = check_output(parted + cmd)
    except(CalledProcessError) as e:
        logging.error("Problem running: %s" % e.cmd)
        logging.error("Exit Status: %s" % e.returncode)
        logging.error("Output: %s" % e.output)
        raise NeonInstallFail(fail_message)
    if raw:
        return raw_output
    return __parse_parted(raw_output)

def __parse_parted(raw):
    """ Sample parted output:
        [root@bed ~]# parted -ms -- /dev/mmcblk0 unit s print
        BYT;
        /dev/mmcblk0:62333952s:sd/mmc:512:512:msdos:SD SL32G:;
        1:2048s:1001471s:999424s:fat16::lba;
        2:1001472s:1251327s:249856s:linux-swap(v1)::;
        3:1251328s:62333951s:61082624s:ext4::;
    """
    out = list()
    for line in raw.split(';'):
        chopped = line.strip().split(':')
        if len(chopped) <= 1:
            continue
        out.append(chopped)
    return out

def __call_resizefs(fail_message, command):
    resizefs = ['/usr/sbin/resize2fs']
    cmd = list()
    raw_output = ''
    if isinstance(command, basestring):
        cmd = shlex.split(command)
    else:
        cmd = command

    # TODO: XFS
    try:
        check_output(resizefs + cmd)
    except(CalledProcessError) as e:
        logging.error("Problem running: %s" % e.cmd)
        logging.error("Exit Status: %s" % e.returncode)
        logging.error("Output: %s" % e.output)
        raise NeonInstallFail(fail_message)

def extend_fs():
    logging.info("extending partition")
    loc = "/dev/"
    (root, sep, part) = __split_device_part(__find_root_device())
    if not root:
        logging.warn("can not find root device; unrecoverable")
        raise NeonInstallFail("can not find root device; unrecoverable")
    disk = loc + root
    partition = loc + root + sep + part

    # Start doing actions on disks
    part_data = __call_parted("Could not print partition data",
                [disk, 'unit', 's', 'print'])

    logging.debug('received part data: ' + str(part_data))
    if part_data[-1][0] != part:
        raise NeonInstallFail("root partition must be last partition on \
                disk. rootpart: %s, lastpart: %s" \
                % (part, part_data[-1][0]))

    start_sector = part_data[-1][1]

    """ XXX DANGER ZONE XXX
    We're about to start mangling partition data.
    https://www.youtube.com/watch?v=siwpn14IE7E
    """
    __call_parted("could not delete root partition map.", [disk, 'rm', part])

    # Create new partition map to fill all available space
    dire_warning = '''CRITICAL DATA LOSS IMMINENT! ROOT PARTITION MAPPING HAS
        BEEN DELETED FROM MASTER BOOT RECORD, AND WE ARE UNABLE TO CREATE A
        NEW MAP.
        ALL DATA WILL BE LOST ON THIS DEVICE UNLESS YOU CAN FIX THE PART MAP.
        DUMPING ORIGINAL PARTITION MAP:'''

    __call_parted(dire_warning, [disk, 'mkpart', 'primary', start_sector,
            '-1s'])

    # Online extend partition.
    __call_resizefs("could not resize fs. Luckily not the end of the world.",
            [partition])

    # Just for safety, let's flush all of our buffers before reboot
    call(['/usr/bin/sync'])

    logging.info('Rebooting for root fs remount')
    call(['/usr/bin/systemctl', 'reboot'])
    sys.exit(0)


def __find_root_device():
    device_id = os.lstat("/").st_dev
    major = os.major(device_id)
    minor = os.minor(device_id)
    logging.debug("found root device: %s %s" % (major, minor))
    regex = re.compile(string.join((str(major), str(minor), "\d+", "(\w+)"), "\s+"))
    with open("/proc/partitions") as parts:
        for line in parts:
            if regex.search(line):
                dev = regex.search(line).group(1)
                logging.info("found root device: " + dev)
                return dev
        return False

def __split_device_part(device):
    """ Returns a triple of root device, partition separator, and partition
    number. Examples:
        (sda, '', 4) # root device 4th partition of sda, or sda4
        (mmcblk0, 'p', 2) # root device is 2nd partition os mmcblk0, or mmcblk0p2
    """
    if device == False:
        return (device, device, device)
    pre = "/dev/"
    part = device[-1]
    # 99% of use cases covered here, but this will break with double digit
    # partitions.
    if os.path.lexists(pre + device[:-1]):
        logging.debug("no part separator. returning: %s %s %s"
                % (device[:-1], '', device[-1]))
        return (device[:-1], '', device[-1])
    if os.path.lexists(pre + device[:-2]):
        logging.debug("part separator found. returning: %s %s %s"
                % (device[:-2], device[-2], device[-1]))
        return (device[:-2], device[-2], device[-1])

def __call_yum(fail_message, *args):
    yum = '/usr/bin/yum -e1 -y '
    try:
        check_output(yum + args.join(' '))
    except(CalledProcessError) as e:
        logging.error("Problem running: %s" % e.cmd)
        logging.error("Exit Status: %s" % e.returncode)
        logging.error("Output: %s" % e.output)
        raise NeonInstallFail(fail_message)


def update_sys():
    # Pretty much just `yum -y update`
    __call_yum("Unable to update system. Check your internet connection",
                'update')

def install_deps():
    # Pretty much just `yum -y install <dependencies>`
    __call_yum("Unable to install required packages.", install,
            dependencies.get_dependencies().join(' '))

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


def config_shairport():
    if not os.path.lexists('/etc/conf.d/'):
        os.mkdir('/etc/conf.d/')
    with open('/etc/conf.d/shairport', 'w') as conf:
        # Todo: get name from user 
        conf.write('SHAIRPORT_ARGS="--name=Neon \
                --log=/var/log/shairport.log --pidfile=/var/run/shairport')

def config_alsa():
    config = ''
    with open('/usr/share/alsa/alsa.conf', 'rw') as f:
        config = f.read()
        f.seek(0,0)
        f.write(re.sub(r'^pcm.front cards.pcm.front$', 'pcm.front cards.pcm.default', config))
        f.truncate()

    if call('amixer cset numid=3 1') != 0:# todo get output from user
        logging.warn("can not set analog as default output")

    if call('amixer set PCM 1.00dB') != 0:
        logging.warn("could not reset gain on DAC")

