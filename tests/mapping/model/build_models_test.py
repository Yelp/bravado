from bravado.mapping.model import build_models


def test_empty():
    assert {} == build_models({})


def test_not_empty(definitions_spec):
    models = build_models(definitions_spec)
    for model_name in definitions_spec.keys():
        model_type = models.get(model_name)
        assert model_name == model_type.__name__
        assert isinstance(model_type, type)
