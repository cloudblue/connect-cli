def assert_request_headers(headers):
    assert 'Authorization' in headers
    assert headers['Authorization'] == 'ApiKey XXXX:YYYY'
    assert 'User-Agent' in headers
    assert headers['User-Agent'].startswith('connect-cli/')