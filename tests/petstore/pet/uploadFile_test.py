import pytest


@pytest.xfail.mark(reason="Get in:formData and type:file working")
def test_success(petstore):
    result = petstore.pet.uploadFile().result()
    print result