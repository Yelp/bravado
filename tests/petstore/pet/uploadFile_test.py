# -*- coding: utf-8 -*-
from __future__ import print_function


def test_success(petstore):
    contents = "this is supposed to be a file"
    print(len(contents))
    status, result = petstore.pet.uploadFile(
        petId=1,
        file=contents,
        additionalMetadata="testing file upload").result()
    print(status)
    print(result)
