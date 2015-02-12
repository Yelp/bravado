from bravado.mapping.param import add_param_to_req


def test_url_path_parameter_with_spaces_quoted_correctly():
    param_spec = {
        "name": "review_id",
        "description": "ID of review that needs to be updated",
        "required": True,
        "type": "string",
        "in": "path",
    }
    param_value = "${n} review"
    request = {'url': 'http://foo.com/{review_id}'}
    add_param_to_req(param_spec, param_value, request)
    assert u"http://foo.com/%24%7Bn%7D%20review" == request['url']
