import pytest

from bravado.mapping.docstring import create_operation_docstring
from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec




def test_simple(operation_dict):
    spec = Spec({})
    operation = Operation(spec, '/pet', 'get', operation_dict)
    docstring = create_operation_docstring(operation)
    print docstring