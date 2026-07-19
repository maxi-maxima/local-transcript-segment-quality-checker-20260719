import argparse, json, re
LINE=re.compile(r'^(?P<start>\d+(?:\.\d+)?)\s+(?P<end>\d+(?:\.\d+)?)\s+(?P<text>.*)$')
def check(text, max_seconds=12):
    issues=[]; last_end=-1; count=0
    for i,line in enumerate(text.splitlines(),1):
        if not line.strip(): continue
        m=LINE.match(line.strip())
        if not m: issues.append({'line':i,'type':'parse_error','message':'expected: start end text'}); continue
        count+=1; s=float(m.group('start')); e=float(m.group('end')); body=m.group('text').strip()
        if e<=s: issues.append({'line':i,'type':'bad_time_order','message':'end must be greater than start'})
        if s<last_end: issues.append({'line':i,'type':'overlap','message':'segment overlaps previous'})
        if e-s>max_seconds: issues.append({'line':i,'type':'too_long','message':f'segment exceeds {max_seconds}s'})
        if len(body)<2: issues.append({'line':i,'type':'empty_text','message':'segment text is empty or tiny'})
        last_end=max(last_end,e)
    return {'segments':count,'issues':issues,'passed':not issues}
def main(argv=None):
    p=argparse.ArgumentParser(description='QA timestamped local transcript segments')
    p.add_argument('file'); p.add_argument('--max-seconds',type=float,default=12); p.add_argument('--json',action='store_true'); p.add_argument('--fail-on-issues',action='store_true',help='exit 1 when transcript issues are found')
    a=p.parse_args(argv); r=check(open(a.file,encoding='utf-8').read(),a.max_seconds)
    if a.json: print(json.dumps(r,indent=2))
    else:
        print(f"Segments: {r['segments']}  Status: {'PASS' if r['passed'] else 'FAIL'}")
        for x in r['issues']: print(f"line {x['line']}: {x['type']} - {x['message']}")
    if a.fail_on_issues and not r['passed']: raise SystemExit(1)
if __name__=='__main__': main()
