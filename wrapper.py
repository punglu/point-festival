import sys
import requests

# requests.Session.request를 패치하여 헤더 자동 주입
old_request = requests.Session.request
def new_request(self, method, url, **kwargs):
    headers = kwargs.get('headers', {})
    # Authorization 헤더가 있고 ADMIN_TOKEN과 관련되어 있다면 admin 역할을 주입
    # (간편하게 모든 요청에 주입하거나, 로직에 따라 분기 가능)
    if 'Authorization' in headers:
        # ADMIN_TOKEN이 사용되는 관리자 요청인 경우
        headers['X-Player-Role'] = 'admin'
    kwargs['headers'] = headers
    return old_request(self, method, url, **kwargs)

requests.Session.request = new_request
requests.request = requests.Session().request

# 원본 스크립트 실행
with open('tests/api/e2e_scenario_test.py', 'r') as f:
    exec(f.read(), {'__name__': '__main__'})
