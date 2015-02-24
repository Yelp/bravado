from bravado.mapping.model import create_model_docstring


def test_pet(petstore_spec):
    model_spec = petstore_spec.spec_dict['definitions']['Pet']

    expected = \
        "Attributes:\n\n" \
        "\tcategory: Category\n" \
        "\tid: integer\n" \
        "\tname: string\n" \
        "\tphotoUrls: list of string\n" \
        "\tstatus: string - pet status in the store\n" \
        "\ttags: list of Tag\n" \
        "\t"

    docstring = create_model_docstring(model_spec)
    assert expected == docstring
