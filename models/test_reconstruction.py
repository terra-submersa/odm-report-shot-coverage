import json
from unittest import TestCase

from models.reconstruction import json_parse_reconstruction_collection, json_parse_reconstruction


class Test(TestCase):
    obj_reconstruction_collection: any
    with open('resources/reconstruction.json') as fd:
        obj_reconstruction_collection = json.load(fd)

    def test_json_parse_reconstruction_collection(self):
        got = json_parse_reconstruction_collection(self.obj_reconstruction_collection)
        self.assertEqual(1, len(got), 'nb reconstructions')

    def test_json_parse_reconstruction(self):
        got = json_parse_reconstruction(self.obj_reconstruction_collection[0])

        self.assertEqual(2, len(got.cameras), 'cameras')
        self.assertEqual(60, len(got.shots), 'shots')
        self.assertEqual(51524, len(got.points), 'points')
