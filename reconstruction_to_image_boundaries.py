import json

from models.reconstruction import json_parse_reconstruction_collection

if __name__ == '__main__':
    with open('resources/reconstruction.json') as fd:
        reconstruction = json_parse_reconstruction_collection(json.load(fd))[0]
        reconstruction.shot_xy_boundaries()
