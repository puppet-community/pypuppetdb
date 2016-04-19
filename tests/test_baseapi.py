import base64
import json
import mock
import httpretty
import pytest
import requests
import pypuppetdb


def stub_request(url, data=None, **kwargs):
    if data is None:
        body = '[]'
    else:
        with open(data, 'r') as d:
            body = json.load(d.read())
    return httpretty.register_uri(httpretty.GET, url, body=body, status=200,
                                  **kwargs)


class TestBaseAPIVersion(object):
    def test_init_defaults(self):
        v4 = pypuppetdb.api.BaseAPI()
        assert v4.api_version == 'v4'


class TestBaseAPIInitOptions(object):
    def test_defaults(self, baseapi):
        assert baseapi.host == 'localhost'
        assert baseapi.port == 8080
        assert baseapi.ssl_verify is True
        assert baseapi.ssl_key is None
        assert baseapi.ssl_cert is None
        assert baseapi.timeout == 10
        assert baseapi.protocol == 'http'
        assert baseapi.url_path == ''
        assert baseapi.username is None
        assert baseapi.password is None

    def test_host(self):
        api = pypuppetdb.api.BaseAPI(host='127.0.0.1')
        assert api.host == '127.0.0.1'

    def test_port(self):
        api = pypuppetdb.api.BaseAPI(port=8081)
        assert api.port == 8081

    def test_ssl_verify(self):
        api = pypuppetdb.api.BaseAPI(ssl_verify=False)
        assert api.ssl_verify is False
        assert api.protocol == 'http'

    def test_ssl_key(self):
        api = pypuppetdb.api.BaseAPI(ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.protocol == 'http'

    def test_ssl_cert(self):
        api = pypuppetdb.api.BaseAPI(ssl_cert='/d/e/f.pem')
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'http'

    def test_ssl_key_and_cert(self):
        api = pypuppetdb.api.BaseAPI(ssl_cert='/d/e/f.pem',
                                     ssl_key='/a/b/c.pem')
        assert api.ssl_key == '/a/b/c.pem'
        assert api.ssl_cert == '/d/e/f.pem'
        assert api.protocol == 'https'

    def test_timeout(self):
        api = pypuppetdb.api.BaseAPI(timeout=20)
        assert api.timeout == 20

    def test_protocol(self):
        api = pypuppetdb.api.BaseAPI(protocol='https')
        assert api.protocol == 'https'

    def test_uppercase_protocol(self):
        api = pypuppetdb.api.BaseAPI(protocol='HTTP')
        assert api.protocol == 'http'

    def test_override_protocol(self):
        api = pypuppetdb.api.BaseAPI(protocol='http',
                                     ssl_cert='/d/e/f.pem',
                                     ssl_key='/a/b/c.pem')
        assert api.protocol == 'http'

    def test_invalid_protocol(self):
        with pytest.raises(ValueError):
            api = pypuppetdb.api.BaseAPI(protocol='ftp')

    def test_url_path(self):
        api = pypuppetdb.api.BaseAPI(url_path='puppetdb')
        assert api.url_path == '/puppetdb'

    def test_url_path_leading_slash(self):
        api = pypuppetdb.api.BaseAPI(url_path='/puppetdb')
        assert api.url_path == '/puppetdb'

    def test_url_path_trailing_slash(self):
        api = pypuppetdb.api.BaseAPI(url_path='puppetdb/')
        assert api.url_path == '/puppetdb'

    def test_url_path_longer_with_both_slashes(self):
        api = pypuppetdb.api.BaseAPI(url_path='/puppet/db/')
        assert api.url_path == '/puppet/db'

    def test_username(self):
        api = pypuppetdb.api.BaseAPI(username='puppetdb')
        assert api.username is None
        assert api.password is None

    def test_password(self):
        api = pypuppetdb.api.BaseAPI(password='password123')
        assert api.username is None
        assert api.password is None

    def test_username_and_password(self):
        api = pypuppetdb.api.BaseAPI(username='puppetdb',
                                     password='password123')
        assert api.username == 'puppetdb'
        assert api.password == 'password123'


class TestBaseAPIProperties(object):
    def test_version(self, baseapi):
        assert baseapi.version == 'v4'

    def test_base_url(self, baseapi):
        assert baseapi.base_url == 'http://localhost:8080'

    def test_base_url_ssl(self, baseapi):
        baseapi.protocol = 'https'  # slightly evil
        assert baseapi.base_url == 'https://localhost:8080'

    def test_total(self, baseapi):
        baseapi.last_total = 10  # slightly evil
        assert baseapi.total == 10


class TestBaseAPIURL(object):
    def test_without_path(self, baseapi):
        assert baseapi._url('nodes') == \
            'http://localhost:8080/pdb/query/v4/nodes'

    def test_with_invalid_endpoint(self, baseapi):
        with pytest.raises(pypuppetdb.errors.APIError):
            baseapi._url('this_will-Never+Ex1s7')

    def test_with_path(self, baseapi):
        url = baseapi._url('nodes', path='node1.example.com')
        assert url == \
            'http://localhost:8080/pdb/query/v4/nodes/node1.example.com'


class TesteAPIQuery(object):
    @mock.patch.object(requests.Session, 'request')
    def test_timeout(self, get, baseapi):
        get.side_effect = requests.exceptions.Timeout
        with pytest.raises(requests.exceptions.Timeout):
            baseapi._query('nodes')

    @mock.patch.object(requests.Session, 'request')
    def test_connectionerror(self, get, baseapi):
        get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            baseapi._query('nodes')

    @mock.patch.object(requests.Session, 'request')
    def test_httperror(self, get, baseapi):
        get.side_effect = requests.exceptions.HTTPError(
            response=requests.Response())
        with pytest.raises(requests.exceptions.HTTPError):
            baseapi._query('nodes')

    def test_setting_headers(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes')  # need to query some endpoint
        request_headers = dict(httpretty.last_request().headers)
        assert request_headers['Accept'] == 'application/json'
        assert request_headers['Content-Type'] == 'application/json'
        assert request_headers['Accept-Charset'] == 'utf-8'
        assert request_headers['Host'] == 'localhost:8080'
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_with_path(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes/node1')
        baseapi._query('nodes', path='node1')
        assert httpretty.last_request().path == '/pdb/query/v4/nodes/node1'
        httpretty.disable()
        httpretty.reset()

    def test_with_url_path(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/puppetdb/pdb/query/v4/nodes')
        baseapi.url_path = '/puppetdb'
        baseapi._query('nodes')
        assert httpretty.last_request().path == '/puppetdb/pdb/query/v4/nodes'
        httpretty.disable()
        httpretty.reset()

    def test_with_authorization(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi.username = 'puppetdb'
        baseapi.password = 'password123'
        baseapi._query('nodes')
        assert httpretty.last_request().path == '/pdb/query/v4/nodes'
        encoded_cred = 'puppetdb:password123'.encode('utf-8')
        bs_authheader = base64.b64encode(encoded_cred).decode('utf-8')
        assert httpretty.last_request().headers['Authorization'] == \
            'Basic {0}'.format(bs_authheader)
        httpretty.disable()
        httpretty.reset()

    def test_with_query(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', query='["certname", "=", "node1"]')
        assert httpretty.last_request().querystring == {
            'query': ['["certname", "=", "node1"]']}
        httpretty.disable()
        httpretty.reset()

    def test_with_order(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', order_by='ted')
        assert httpretty.last_request().querystring == {
            'order_by': ['ted']}
        httpretty.disable()
        httpretty.reset()

    def test_with_limit(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', limit=1)
        assert httpretty.last_request().querystring == {
            'limit': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_include_total(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', include_total=True)
        assert httpretty.last_request().querystring == {
            'include_total': ['true']}
        httpretty.disable()
        httpretty.reset()

    def test_with_offset(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', offset=1)
        assert httpretty.last_request().querystring == {
            'offset': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_summarize_by(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', summarize_by=1)
        assert httpretty.last_request().querystring == {
            'summarize_by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_by(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', count_by=1)
        assert httpretty.last_request().querystring == {
            'count_by': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_with_count_filter(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        baseapi._query('nodes', count_filter=1)
        assert httpretty.last_request().querystring == {
            'counts_filter': ['1']}
        httpretty.disable()
        httpretty.reset()

    def test_response_empty(self, baseapi):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080/pdb/query/v4/nodes',
                               body=json.dumps(None))
        with pytest.raises(pypuppetdb.errors.EmptyResponseError):
            baseapi._query('nodes')

    def test_response_x_records(self, baseapi):
        httpretty.enable()
        httpretty.register_uri(httpretty.GET,
                               'http://localhost:8080/pdb/query/v4/nodes',
                               adding_headers={
                                   'X-Records': 256},
                               body='[]',
                               )
        baseapi._query('nodes', include_total=True)
        assert baseapi.total == 256

    def test_query_bad_request_type(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/nodes')
        with pytest.raises(pypuppetdb.errors.APIError):
            baseapi._query('nodes',
                           query='["certname", "=", "node1"]',
                           request_method='DELETE')
        httpretty.disable()
        httpretty.reset()


class TestAPIMethods(object):
    def test_metric(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/metrics/v1/mbeans/test')
        baseapi.metric('test')
        assert httpretty.last_request().path == '/metrics/v1/mbeans/test'
        httpretty.disable()
        httpretty.reset()

    def test_fact_names(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/fact-names')
        baseapi.fact_names()
        assert httpretty.last_request().path == '/pdb/query/v4/fact-names'
        httpretty.disable()
        httpretty.reset()

    def test_normalize_resource_type(self, baseapi):
        assert baseapi._normalize_resource_type('sysctl::value') == \
            'Sysctl::Value'
        assert baseapi._normalize_resource_type('user') == 'User'

    def test_environments(self, baseapi):
        httpretty.enable()
        stub_request('http://localhost:8080/pdb/query/v4/environments')
        baseapi.environments()
        assert httpretty.last_request().path == '/pdb/query/v4/environments'
        httpretty.disable()
        httpretty.reset()
