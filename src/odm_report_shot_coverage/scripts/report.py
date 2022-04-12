import json
import os
import argparse
from shutil import copy, SameFileError

from PIL import Image
from pathlib import Path

from odm_report_shot_coverage.models.reconstruction import parse_reconstruction


def _copy_orthophoto(src_dir: str, target_dir: str):
    im = Image.open('%s/odm_orthophoto/odm_orthophoto.tif' % src_dir)
    im.save('%s/odm_orthophoto.png' % target_dir)

    with open('%s/odm_orthophoto/odm_orthophoto_corners.txt' % src_dir) as fd_in:
        vs = fd_in.readline().split(' ')
        corners = {
            'x': [float(vs[0]), float(vs[2])],
            'y': [float(vs[1]), float(vs[3])],
        }
        with open('%s/odm_orthophoto_corners.json' % target_dir, 'w') as fd_out:
            json.dump(corners, fd_out)


def _copy_images(src_dir: str, target_dir: str):
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    target_size = 400
    for file_name in os.listdir(src_dir):
        im = Image.open('%s/%s' % (src_dir, file_name))
        width, height = im.size
        max_size = max(width, height)
        new_size = (int(width * target_size / max_size), int(height * target_size / max_size))
        im = im.resize(new_size)
        im.save('%s/%s' % (target_dir, file_name))


def _copy_web_app(target_dir: str):
    web_dir = os.path.dirname(__file__) + '/web'
    for file_name in os.listdir(web_dir):
        if file_name not in {'data', 'images'}:
            try:
                copy(web_dir + '/' + file_name, target_dir)
            except SameFileError:
                pass


def main():
    parser = argparse.ArgumentParser(description='Build an OpenDroneMap shot coverage report')
    parser.add_argument("project", help="the ODM project root folder",
                        type=str)
    args = parser.parse_args()
    project_dir = args.project

    out_dir = project_dir + '/odm_report/shot_coverage'
    Path(out_dir + '/data').mkdir(parents=True, exist_ok=True)

    _copy_web_app(out_dir)
    _copy_images(project_dir + '/images', out_dir + '/images')
    _copy_orthophoto(project_dir, out_dir + '/data')

    reconstruction = parse_reconstruction(project_dir)

    reconstruction.compute_shot_boundaries()

    with open('%s/data/reconstruction_shots.json' % out_dir, 'w') as fd_out:
        json.dump(reconstruction.to_json(), fd_out)

    print('Shot coverage completed')
    print('To open the results page, launch:')
    print('python -m http.server --directory %s 8001' % out_dir)
    print('And open http://localhost:8001 (or change port value if already taken)')


if __name__ == '__main__':
    main()
