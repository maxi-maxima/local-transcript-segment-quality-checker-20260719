from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.main import check, main


class TranscriptQualityCheckerTests(unittest.TestCase):
    def test_check(self):
        r = check('0 2 hello\n1 20 long overlap\n')
        self.assertFalse(r['passed'])
        self.assertGreaterEqual(len(r['issues']), 2)
        self.assertEqual(r['issue_counts']['overlap'], 1)
        self.assertEqual(r['format'], 'plain')

    def test_srt_input_is_supported(self):
        srt = '''1
00:00:00,000 --> 00:00:02,000
hello world

2
00:00:01,500 --> 00:00:16,000
overlapping long segment
'''
        r = check(srt, max_seconds=10, input_format='auto')
        self.assertEqual(r['format'], 'srt')
        self.assertEqual(r['segments'], 2)
        self.assertEqual(r['issue_counts']['overlap'], 1)
        self.assertEqual(r['issue_counts']['too_long'], 1)

    def test_fail_on_issues_exits(self):
        path = Path('examples/transcript.txt')
        with self.assertRaises(SystemExit) as raised:
            main([str(path), '--max-seconds', '10', '--fail-on-issues'])
        self.assertEqual(raised.exception.code, 1)

    def test_ci_workflow_exists(self):
        self.assertTrue(Path('.github/workflows/ci.yml').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
