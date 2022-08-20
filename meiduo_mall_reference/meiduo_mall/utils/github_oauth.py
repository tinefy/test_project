import json
from urllib.parse import urlencode
from requests import get, post


class OAuthGitHub(object):
    def __init__(
            self, client_id=None, client_secret=None, redirect_uri=None, state=None, login=None, scope=None,
            allow_signup=None, code=None, accept=None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.login = login
        self.scope = scope
        self.state = state
        self.allow_signup = allow_signup
        self.code = code
        self.accept = accept

        self.url = ''
        self.access_token = ''

    def parameters(self, *args):
        params_dict = {}
        if not args:
            for key, value in vars(self).items():
                if value:
                    params_dict[key] = value
        else:
            for item in args:
                if hasattr(self, item):
                    params_dict[item] = getattr(self, item)
                else:
                    print(f'OAuthGitHub中没有{item}属性，已忽略')
        return params_dict

    def get_github_url(self, *args):
        data = self.parameters(*args)
        self.url = 'https://github.com/login/oauth/authorize?' + urlencode(data)
        return self.url

    def get_github_access_token(self, accept='json', *args):
        data = self.parameters(*args)
        headers = {}
        if accept != 'json':
            print('返回数据"Accept"目前只支持"application/json"')
        headers['Accept'] = 'application/json'
        self.url = 'https://github.com/login/oauth/access_token'
        response = post(self.url, data=data, headers=headers)
        content = json.loads(response.content.decode())
        self.access_token = content['access_token']
        return self.access_token

    def get_github_user_info(self, token=None):
        if token:
            self.access_token = token
        headers = {'Authorization': f'token {self.access_token}'}
        url = 'https://api.github.com/user'
        response = get(url, headers=headers)
        content = json.loads(response.content.decode())
        return content
