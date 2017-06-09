# -*- coding: utf-8 -*-
from __future__ import print_function


def test_text_file_upload(petstore):
    contents = "this is supposed to be a file"
    print(len(contents))
    result = petstore.pet.uploadFile(
        petId=1,
        file=contents,
        additionalMetadata="testing text file upload"
    ).result()
    assert result.code == 200
    assert "File uploaded to ./file, 29 bytes" in result.message


def test_binary_file_upload(petstore):
    with open("test-data/images/cat.png", "rb") as image:
        contents = image.read()
        print(len(contents))
        result = petstore.pet.uploadFile(
            petId=1,
            file=contents,
            additionalMetadata="testing binary file upload"
        ).result()

        assert result.code == 200
        assert "File uploaded to ./file, 284973 bytes" in result.message
