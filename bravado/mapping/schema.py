def has_default(schema_object_spec):
    return 'default' in schema_object_spec


def get_default(schema_object_spec):
    return schema_object_spec.get('default', None)


def is_required(schema_object_spec):
    return 'required' in schema_object_spec


def has_format(schema_object_spec):
    return 'format' in schema_object_spec


def get_format(schema_object_spec):
    return schema_object_spec.get('format', None)
