import argparse
import json
import re
from collections import Counter

LINE = re.compile(r'^(?P<start>\d+(?:\.\d+)?)\s+(?P<end>\d+(?:\.\d+)?)\s+(?P<text>.*)$')
SRT_TIME = re.compile(
    r'^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2},\d{3})$'
)


def _srt_seconds(value):
    hh, mm, rest = value.split(':')
    ss, ms = rest.split(',')
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def _parse_srt_blocks(text):
    blocks = []
    current = []
    for line in text.splitlines():
        if line.strip():
            current.append(line.rstrip('\n'))
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    parsed = []
    issues = []
    for block in blocks:
        timing_index = 1 if block[0].strip().isdigit() and len(block) > 1 else 0
        line_no = None
        m = SRT_TIME.match(block[timing_index].strip()) if timing_index < len(block) else None
        if block[0].strip().isdigit():
            line_no = int(block[0].strip())
        if not m:
            issues.append({'line': line_no or len(parsed) + 1, 'type': 'parse_error', 'message': 'expected SRT timestamp line'})
            continue
        parsed.append(
            {
                'line': line_no or len(parsed) + 1,
                'start': _srt_seconds(m.group('start')),
                'end': _srt_seconds(m.group('end')),
                'text': ' '.join(part.strip() for part in block[timing_index + 1 :]).strip(),
            }
        )
    return parsed, issues


def _parse_plain_segments(text):
    segments = []
    issues = []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        m = LINE.match(line.strip())
        if not m:
            issues.append({'line': i, 'type': 'parse_error', 'message': 'expected: start end text'})
            continue
        segments.append(
            {
                'line': i,
                'start': float(m.group('start')),
                'end': float(m.group('end')),
                'text': m.group('text').strip(),
            }
        )
    return segments, issues


def _looks_like_srt(text):
    return '-->' in text and any(SRT_TIME.match(line.strip()) for line in text.splitlines())


def _validate_segments(segments, issues, max_seconds):
    last_end = -1
    for segment in segments:
        s = segment['start']
        e = segment['end']
        body = segment['text']
        line = segment['line']
        if e <= s:
            issues.append({'line': line, 'type': 'bad_time_order', 'message': 'end must be greater than start'})
        if s < last_end:
            issues.append({'line': line, 'type': 'overlap', 'message': 'segment overlaps previous'})
        if e - s > max_seconds:
            issues.append({'line': line, 'type': 'too_long', 'message': f'segment exceeds {max_seconds:g}s'})
        if len(body) < 2:
            issues.append({'line': line, 'type': 'empty_text', 'message': 'segment text is empty or tiny'})
        last_end = max(last_end, e)
    return issues


def check(text, max_seconds=12, input_format='auto'):
    if input_format == 'auto':
        input_format = 'srt' if _looks_like_srt(text) else 'plain'
    if input_format == 'srt':
        segments, issues = _parse_srt_blocks(text)
    else:
        segments, issues = _parse_plain_segments(text)
    issues = _validate_segments(segments, issues, max_seconds)
    by_type = dict(sorted(Counter(issue['type'] for issue in issues).items()))
    return {
        'format': input_format,
        'segments': len(segments),
        'issues': issues,
        'issue_counts': by_type,
        'passed': not issues,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description='QA timestamped local transcript segments')
    p.add_argument('file')
    p.add_argument('--max-seconds', type=float, default=12)
    p.add_argument('--input-format', choices=['auto', 'plain', 'srt'], default='auto', help='transcript format to parse')
    p.add_argument('--json', action='store_true')
    p.add_argument('--summary', action='store_true', help='print issue counts by type')
    p.add_argument('--fail-on-issues', action='store_true', help='exit 1 when transcript issues are found')
    a = p.parse_args(argv)
    with open(a.file, encoding='utf-8') as f:
        r = check(f.read(), a.max_seconds, a.input_format)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"Segments: {r['segments']}  Format: {r['format']}  Status: {'PASS' if r['passed'] else 'FAIL'}")
        if a.summary and r['issue_counts']:
            print('Issue summary: ' + ', '.join(f"{k}={v}" for k, v in r['issue_counts'].items()))
        for x in r['issues']:
            print(f"line {x['line']}: {x['type']} - {x['message']}")
    if a.fail_on_issues and not r['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
