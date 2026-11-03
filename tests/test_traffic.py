"""Traffic archive merge and report tests; no network required."""
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/traffic'))
import collect
import report


def day(date, count, uniques):
    return {'date': date, 'count': count, 'uniques': uniques}


class TrafficArchive(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def test_daily_merge_keeps_history_and_updates_partial_day(self):
        path = self.dir / 'views.csv'
        collect.merge_daily(path, [day('2026-10-01', 5, 2), day('2026-10-02', 1, 1)])
        collect.merge_daily(path, [day('2026-10-02', 9, 4), day('2026-10-03', 3, 3)])
        rows = collect.read_rows(path)
        self.assertEqual([r['date'] for r in rows], ['2026-10-01', '2026-10-02', '2026-10-03'])
        self.assertEqual(rows[1]['count'], '9')

    def test_snapshot_rerun_on_same_day_replaces_it(self):
        path = self.dir / 'referrers.csv'
        fields = collect.REFERRER_FIELDS
        key = lambda r: r['referrer']
        collect.replace_snapshot(path, fields, '2026-10-01', [{'referrer': 'old', 'count': 1, 'uniques': 1}], key)
        collect.replace_snapshot(path, fields, '2026-10-02', [{'referrer': 'gone', 'count': 1, 'uniques': 1}], key)
        collect.replace_snapshot(path, fields, '2026-10-02', [{'referrer': 'Google', 'count': 7, 'uniques': 5}], key)
        self.assertEqual([(r['snapshot'], r['referrer']) for r in collect.read_rows(path)],
                         [('2026-10-01', 'old'), ('2026-10-02', 'Google')])

    def test_report_builds_readme_and_valid_svgs(self):
        days = [day(f'2026-10-{d:02d}', d * 10, d) for d in range(1, 16)]
        collect.merge_daily(self.dir / 'views.csv', days)
        collect.merge_daily(self.dir / 'clones.csv', days)
        collect.write_rows(self.dir / 'stars.csv', collect.STAR_FIELDS,
                           [{'date': '2026-09-30', 'new': '3', 'total': '3'}])
        report.build(self.dir, 'owner/repo', '2026-10-15')
        readme = (self.dir / 'README.md').read_text(encoding='utf-8')
        # Oct 8-14 vs Oct 1-7, leaving out the unfinished Oct 15.
        self.assertIn('| Views | 770 | 280 | +175% | 1,200 |', readme)
        for name in ('views', 'clones', 'stars'):
            ET.fromstring((self.dir / 'charts' / f'{name}.svg').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
