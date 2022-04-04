import json
from PIL import Image
from pathlib import Path

from models.reconstruction import json_parse_reconstruction_collection


def copy_orthophoto(project_dir: str, out_dir: str):
    im = Image.open('%s/odm_orthophoto/odm_orthophoto.tif' % project_dir)
    # rgb_im = im.convert('RGB')
    im.save('%s/odm_orthophoto.png' % out_dir)

    with open('%s/odm_orthophoto/odm_orthophoto_corners.txt' % project_dir) as fd_in:
        vs = fd_in.readline().split(' ')
        corners = {
            'x': [float(vs[0]), float(vs[2])],
            'y': [float(vs[1]), float(vs[3])],
        }
        with open('%s/odm_orthophoto_corners.json' % out_dir, 'w') as fd_out:
            json.dump(corners, fd_out)


if __name__ == '__main__':
    project_dir = '/Users/alex/terra-submersa/tools/odm/datasets/lambayana-pavements-20210810/code'
    out_dir = 'web/data'
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    copy_orthophoto(project_dir, out_dir)

    with open('%s/opensfm/reconstruction.json' % project_dir) as fd:
        reconstruction = json_parse_reconstruction_collection(json.load(fd))[0]

        reconstruction.compute_shot_point_coverage()

        with open('%s/reconstruction_shot_points.json' % out_dir, 'w') as fd_out:
            json.dump(reconstruction.to_json(), fd_out)
