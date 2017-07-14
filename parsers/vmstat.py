from util import LOGGER
from model import SystemStats
import parser

_interesting_vmstat_vars = [
    'nr_free_pages',
    'pgpgin',
    'pgpgout',
    'pswpin',
    'pswpout',
    'pgalloc_normal',
    'pgfree',
    'pgactivate',
    'pgdeactivate',
    'pgfault',
    'pgmajfault',
    'pageoutrun',
    'allocstall',
]

class Parser_vmstat(parser.Parser):
    def parse(self, data, out):
        if not out.has_key('stats'):
            out['stats'] = SystemStats()

        # Parse data from /proc/vmstat.
        for line in data.split('\n'):
            parts = line.split()
            if len(parts) and parts[0] in _interesting_vmstat_vars:
                out['stats'].vmstats[parts[0]] = int(parts[1])
        return out
