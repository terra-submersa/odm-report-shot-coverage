import json
import os
import argparse
from shutil import copy, SameFileError
import logging
from tqdm import tqdm

from PIL import Image
from pathlib import Path

from odm_report_shot_coverage.models.reconstruction import parse_reconstruction
from odm_report_shot_coverage.models.shot import Boundaries

Image.MAX_IMAGE_PIXELS = 1000000000


def _copy_orthophoto(src_dir: str, target_dir: str) -> Boundaries:
    logging.info('Copying orthophoto')
    im = Image.open('%s/odm_orthophoto/odm_orthophoto.tif' % src_dir)
    im.save('%s/odm_orthophoto.png' % target_dir)


def _copy_images(src_dir: str, target_dir: str):
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    target_size = 400
    image_files = os.listdir(src_dir)
    for file_name in tqdm(image_files, desc='Resizing images'):
        im = Image.open('%s/%s' % (src_dir, file_name))
        width, height = im.size
        max_size = max(width, height)
        new_size = (int(width * target_size / max_size), int(height * target_size / max_size))
        im = im.resize(new_size)
        im.save('%s/%s' % (target_dir, file_name))


def _copy_web_app(target_dir: str):
    logging.info('Copying web app')
    web_dir = os.path.dirname(__file__) + '/web'
    for file_name in os.listdir(web_dir):
        if file_name not in {'data', 'images'}:
            try:
                copy(web_dir + '/' + file_name, target_dir)
            except SameFileError:
                pass


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Build an OpenDroneMap shot coverage report')
    parser.add_argument("project", help="the ODM project root folder",
                        type=str)
    args = parser.parse_args()
    project_dir = args.project

    out_dir = project_dir + '/odm_report/shot_coverage'
    Path(out_dir + '/data').mkdir(parents=True, exist_ok=True)

    _copy_web_app(out_dir)
    _copy_images(project_dir + '/images', out_dir + '/images')
    orthophoto_boundaries = _copy_orthophoto(project_dir, out_dir + '/data')

    logging.info('Parsing reconstruction')
    reconstruction = parse_reconstruction(project_dir)

    logging.info('Computing shot boundaries')
    reconstruction.compute_shot_boundaries()

    logging.info('Saving reconstruction_shots.json')
    with open('%s/data/reconstruction_shots.json' % out_dir, 'w') as fd_out:
        json.dump(reconstruction.to_json(), fd_out)

    print('Shot coverage completed')
    print('To open the results page, launch:')
    print('python -m http.server --directory %s 8001' % out_dir)
    print('And open http://localhost:8001 (or change port value if already taken)')


if __name__ == '__main__':
    main()
