from model import SmapsPermissions, MemoryRegion


def parse_smaps_header(header):
    info = MemoryRegion()
    # Example line is:
    # 011e6000-01239000 rw-p 00000000 00:00 0    [heap]
    # 8ec00000-8ec01000 rw-s 00000000 00:14 20   /dev/shm/NS2371 (deleted)
    # All numbers are hex except for the inode
    parts = header.split()
    print (parts)

    # Parse the address range
    info.start_addr, info.end_addr = [int(x, 16) for x in parts[0].split('-')]

    # Parse the permissions
    permissions = parts[1]
    info.permissions.readable = "r" in permissions
    info.permissions.writable = "w" in permissions
    info.permissions.executable = "x" in permissions
    info.permissions.private = "p" in permissions
    info.permissions.shared = "s" in permissions

    info.offset = int(parts[2], 16)

    # eg. 08:06
    info.major_dev, info.minor_dev = [int(x, 16) for x in parts[3].split(':')]

    # The inode isn't a hex number
    info.inode = int(parts[4])

    # eg. [heap]
    # or  /dev/shm/NS2371
    info.name = parts[5]

    info.deleted = header.endswith('(deleted)')

    return info

def parse_smaps_memory_region(stream):
    """stream can be a file or StringIO.

Parse a whole smaps region, which may look like:

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

    region = MemoryRegion()
    while True:
        line = stream.readline()
        if not line: break
        print ('line', line.strip())
    return region