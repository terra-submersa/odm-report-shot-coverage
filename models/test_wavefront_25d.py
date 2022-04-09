from unittest import TestCase

from models.shot import Boundaries
from models.wavefront_25d import _parse_facet_vertices, _paving_sizes


class Test(TestCase):
    def test_parse_facet_vertices(self):
        str = 'f 34922/4/34922 34921/7/34921 35192/2/35192'

        got = _parse_facet_vertices(str)

        self.assertEquals((34921, 34920, 35191), got)

    def test_paving_sizes(self):
        b = Boundaries(x_min=-50, x_max=150, y_min=25, y_max=125)

        got = _paving_sizes(b, 30)

        self.assertEquals((8, 4), got)
