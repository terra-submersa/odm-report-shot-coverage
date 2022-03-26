import json
from unittest import TestCase

from models.reconstruction import json_parse_reconstruction_collection, json_parse_reconstruction


class Test(TestCase):
    obj_reconstruction_collection: any
    with open('resources/reconstruction.json') as fd:
        obj_reconstruction_collection = json.load(fd)

    def test_json_parse_reconstruction_collection(self):
        got = json_parse_reconstruction_collection(self.obj_reconstruction_collection)

        self.assertEqual(1, len(got))

    def test_json_parse_reconstruction(self):
        got = json_parse_reconstruction(self.obj_reconstruction_collection[0])

        self.assertEqual(1, len(got.cameras))
        self.assertEqual(49, len(got.shots))
        self.assertEqual(5848, len(got.points))
