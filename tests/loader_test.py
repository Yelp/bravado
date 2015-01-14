import unittest

import pytest

import swaggerpy
from swaggerpy.swagger_model import load_file


class TestProcessor(swaggerpy.swagger_model.SwaggerProcessor):
    def process_resource_listing(self, resources, context):
        resources['processed'] = True


class LoaderTest(unittest.TestCase):
    def test_simple(self):
        uut = load_file('test-data/1.2/simple/resources.json')
        self.assertEqual('1.2', uut['swaggerVersion'])
        decl = uut['apis'][0]['api_declaration']
        self.assertEqual(1, len(decl['models']))
        self.assertEqual(1, len(decl['models']['Simple']['properties']))

    def test_missing(self):
        with pytest.raises(IOError):
            load_file('test-data/1.2/missing_resource/resources.json')


if __name__ == '__main__':
    unittest.main()
