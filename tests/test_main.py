from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.main import check, main
def test_check():
    r=check('0 2 hello\n1 20 long overlap\n'); assert not r['passed']; assert len(r['issues'])>=2
def test_fail_on_issues_exits():
    path=Path('examples/transcript.txt')
    try:
        main([str(path),'--max-seconds','10','--fail-on-issues'])
    except SystemExit as e:
        assert e.code==1
    else:
        raise AssertionError('expected transcript issues to exit')
def test_ci_workflow_exists():
    assert Path('.github/workflows/ci.yml').exists()
if __name__=='__main__':
    test_check(); test_fail_on_issues_exits(); test_ci_workflow_exists(); print('ok')
