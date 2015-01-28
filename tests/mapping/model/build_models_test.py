from bravado.mapping.model import build_models


def test_empty():
    assert {} == build_models({})


def test_not_empty(definitions_dict):
    models = build_models(definitions_dict)
    for model_name in definitions_dict.keys():
        model_type = models.get(model_name)
        assert model_name == model_type.__name__
        assert isinstance(model_type, type)
