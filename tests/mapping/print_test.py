import os
import json

import pytest
import jsonref
from swagger_spec_validator import validator20

from bravado.mapping.model import tag_models, fix_malformed_model_refs
from bravado.swagger_type import is_dict_like, is_list_like


@pytest.fixture
def jsonref_petstore_dict():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    fpath = os.path.join(my_dir, '../../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        petstore = json.loads(f.read())
        tag_models(petstore)
        fix_malformed_model_refs(petstore)
        unrefed_petstore = jsonref.JsonRef.replace_refs(petstore)
        validator20.validate_spec(unrefed_petstore)
        return unrefed_petstore


@pytest.mark.xfail(reason='This is not a test. Remove later')
def test_print(jsonref_petstore_dict):
    assert False
    print '\n'
    print_spec(jsonref_petstore_dict)


def print_spec(spec, level=0):
    indent = '\t' * level
    if is_dict_like(spec):
        for k, v in spec.iteritems():
            print indent + k + ':',
            if is_dict_like(v):
                print '{'
                print_spec(v, level + 1)
                print indent + '}'
            elif is_list_like(v):
                print ' ['
                print_spec(v, level + 1)
                print indent + ']'
            else:
                print str(v) + ', '
    elif is_list_like(spec):
        for element in spec:
            if is_list_like(element):
                print ' ['
                print_spec(element, level + 1)
                print indent + ']'
            elif is_dict_like(element):
                print indent + '{'
                print_spec(element, level + 1)
                print indent + '},'
            else:
                print_spec(element, level + 1)
    else:
        print indent + str(spec) + ', '
