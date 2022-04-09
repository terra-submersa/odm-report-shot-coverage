import re

import numpy as np

from models.shot import Boundaries


class Wavefront25D:
    points: list[(float, float, float)] = []
    facets: list[(int, int, int)] = []
    boundaries: Boundaries
    paving_dimensions: (int, int)
    paving_facets: list[list[list[int]]]

    def to_json(self) -> dict:
        return {
            'points': self.points,
            'facets': self.facets,
            'boundaries': self.boundaries.to_json(),
            'paving_dimensions': self.paving_dimensions,
            'paving_facets': self.paving_facets,
        }

    def _compute_boundaries(self):
        self.boundaries = Boundaries(
            x_min=min([pc[0] for pc in self.points]),
            x_max=max([pc[0] for pc in self.points]),
            y_min=min([pc[1] for pc in self.points]),
            y_max=max([pc[1] for pc in self.points])
        )

    def _paving_indices(self, x: float, y: float) -> (int, int):
        return int(
            (x - self.boundaries.x_min) / (self.boundaries.x_max - self.boundaries.x_min * self.paving_dimensions[0])), \
               int((y - self.boundaries.y_min) / (
                       self.boundaries.y_max - self.boundaries.y_min * self.paving_dimensions[1]))

    def _compute_paving_facets(self):
        self.paving_facets = [[[None] * self.paving_dimensions[1]] * self.paving_dimensions[0]]
        for i_facet, facet in enumerate(self.facets):
            idx = set()
            for p in [self.points[i] for i in facet]:
                (i, j) = self._paving_indices(p[0], p[1])
                idx.add((i, j))
            for k in idx:
                if self.paving_facets[k[0]][k[1]] is None:
                    self.paving_facets[k[0]][k[1]] = []
                self.paving_facets[k[0]][k[1]].append(i_facet)


_facet_pattern = re.compile("""f (\d+)/\d+/\d+ (\d+)/\d+/\d+ (\d+)/\d+/\d+""")


def _parse_facet_vertices(facet_str: str):
    """Extract facet indices from line (but returns starting from 0)"""
    m = _facet_pattern.fullmatch(facet_str)
    if m is None:
        raise Exception('Cannot parse facet "%s"' % facet_str)
    return int(m.group(1)) - 1, int(m.group(2)) - 1, int(m.group(3)) - 1


def _paving_sizes(boundaries: Boundaries, min_blocks: int) -> (int, int):
    """number of block dimensions to cover the boundaries, the most square possible"""
    width = boundaries.x_max - boundaries.x_min
    height = boundaries.y_max - boundaries.y_min
    r = width / height
    nb_y = np.ceil(np.sqrt(min_blocks / r))
    nb_x = np.ceil(nb_y * r)
    return int(nb_x), int(nb_y)


def parse_wavefront_25d_obj(filename):
    wf = Wavefront25D()
    with open(filename) as fd:
        for line in [l for l in fd.readlines() if l.startswith('v ')]:
            v = line.replace('v ', '').split(' ')
            (x, y, z) = float(v[0]), float(v[1]), float(v[2])
            wf.points.append((x, y, z))

    with open(filename) as fd:
        for line in [l for l in fd.readlines() if l.startswith('f ')]:
            wf.facets.append(_parse_facet_vertices(line.strip()))

    wf._compute_boundaries()
    wf.paving_dimensions = _paving_sizes(wf.boundaries, len(wf.points))
    wf._compute_paving_facets()

    return wf


if __name__ == '__main__':
    project_dir = '/Users/alex/terra-submersa/tools/odm/datasets/lambayana-pavements-20210810/code'
    filename = '%s/odm_texturing_25d/odm_textured_model_geo.obj' % project_dir
    wf25d = parse_wavefront_25d_obj(filename)
    print(wf25d.boundaries)

    exit(0)
