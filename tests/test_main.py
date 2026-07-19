from src.main import check
def test_check():
    r=check('0 2 hello\n1 20 long overlap\n'); assert not r['passed']; assert len(r['issues'])>=2
if __name__=='__main__': test_check(); print('ok')
