import requests
import base64
from bson.json_util import dumps, loads

class Client:

    def __init__(self, server):
        self._server = server
        self._credentials = None
        self._verify_url = True

    def get_server(self):
        return self._server

    def set_server(self, server):
        self._server = server

    def set_credentials(self, user, pwd):
        self._credentials = (user, pwd)

    def get_verify_url(self):
        return self._verify_url

    def set_verify_url(self, verify):
        self._verify_url = verify

    def filter_items(self, filter):
        filter = dumps(filter)
        r = requests.post(self._server+'/ext/items',
                          data=dict(filter=filter),
                          headers=self._get_headers(),
                          allow_redirects=False,
                          verify=self._verify_url)
        r.raise_for_status()
        data = r.json()
        if not data.get('ok'):
            raise RuntimeError("server replied with an error: '%s'" % data.get('message'))
        return data.get('serials')

    def get_item(self, serial):
        r = requests.get(self._server+'/ext/items/'+serial,
                         headers=self._get_headers(),
                         allow_redirects=False,
                         verify=self._verify_url)
        r.raise_for_status()
        return loads(r.text)  # use BSON-aware implementation

    def update_item(self, serial, setdata=None, updatedata=None, pushdata=None, status=None, comment=None):
        data = dict()
        if setdata:
            data['set'] = dumps(setdata)
        if updatedata:
            data['update'] = dumps(updatedata)
        if pushdata:
            data['push'] = dumps(pushdata)
        if status:
            data['status'] = status
        if comment:
            data['comment'] = comment
        r = requests.post(self._server+'/ext/items/update/'+serial,
                          data=data,
                          headers=self._get_headers(),
                          allow_redirects=False,
                          verify=self._verify_url)
        r.raise_for_status()
        data = r.json()
        ok = data.get('ok')
        if not ok:
            raise RuntimeError("server replied with an error: '%s'" % data.get('message'))

    def _get_headers(self):
        if not self._credentials:
            return dict()
        loginstr = self._credentials[0].encode('utf-8') + b':' + self._credentials[1].encode('utf-8')
        return {'Authorization': b'Basic ' + base64.b64encode(loginstr)}




