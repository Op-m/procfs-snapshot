from model import SmapsPermissions, MemoryRegion
import util
import re

def parse_smaps_header(header):
    info = MemoryRegion(free=False)
    # Example line is:
    # 011e6000-01239000 rw-p 00000000 00:00 0    [heap]
    # 8ec00000-8ec01000 rw-s 00000000 00:14 20   /dev/shm/NS2371 (deleted)
    # All numbers are hex except for the inode
    parts = header.split()
    util.LOGGER.debug('Parsing smaps header %s' % header)

    # Parse the address range
    info.start_addr, info.end_addr = [long(x, 16) for x in parts[0].split('-')]

    # Parse the permissions
    permissions = parts[1]
    info.permissions.readable = "r" in permissions
    info.permissions.writable = "w" in permissions
    info.permissions.executable = "x" in permissions
    info.permissions.private = "p" in permissions
    info.permissions.shared = "s" in permissions

    info.offset = long(parts[2], 16)

    # eg. 08:06
    info.major_dev, info.minor_dev = [int(x, 16) for x in parts[3].split(':')]

    # The inode isn't a hex number
    info.inode = int(parts[4])

    # eg. [heap]
    # or  /dev/shm/NS2371
    if len(parts) > 5:
        info.name = parts[5]

    info.deleted = header.endswith('(deleted)')

    return info

_header_re = re.compile('^[0-9a-zA-Z]+-[0-9a-zA-Z]+ .*')

def is_memory_region_header(line):
    return re.match(_header_re, line)

def parse_smaps_memory_region(pid, lines, has_header=True):
    """Parse a whole smaps region, which may look like:

7f5c8550e000-7f5c85554000 r--p 00000000 08:06 1309629   /fonts/Arial_Bold.ttf
Size:                280 kB
Rss:                 152 kB
Pss:                  86 kB
Shared_Clean:        132 kB
Shared_Dirty:         12 kB
Private_Clean:        20 kB
Private_Dirty:         1 kB
Referenced:          152 kB
Anonymous:             2 kB
AnonHugePages:         3 kB
Shared_Hugetlb:        4 kB
Private_Hugetlb:       5 kB
Swap:                  6 kB
SwapPss:               7 kB
KernelPageSize:        8 kB
MMUPageSize:           9 kB
Locked:               10 kB
VmFlags: rd mr mw me sd"""

    has_header = is_memory_region_header(lines[0])

    if has_header:
        region = parse_smaps_header(lines[0])
        if region.name == '[vsyscall]':
            return None
        lines = lines[1:]
    else:
        region = MemoryRegion(free=False)

    region.pid = pid

    global _smaps_string_mappings
    for line in lines:
        util.LOGGER.debug('Parsing line: %s' % line)
        parts = re.split('[ :]+', line.strip())
        if len(parts) < 2:
            util.LOGGER.debug('Skipping smaps line that is too short: %s' % line)
        elif 'Size' == parts[0]:
            # We calculate the size from the address ranges instead.
            pass
        elif 'VmFlags' == parts[0]:
            region.vm_flags = parts[1:]
        else:
            # All other lines should be an amount of some type of memory.
            try:
                region.__dict__[util.camel_case_to_underscore(parts[0])] = int(parts[1]) * 1024
            except KeyError:
                util.LOGGER.warn("Line not recognised: '%s'" % line)
    return region
