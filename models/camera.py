class Camera:
    name: str
    projection_type: str = None
    _width: int = None
    _height: int = None
    _width_rel_max = None
    _height_rel_max = None
    focal: float
    c_x: float = 0
    c_y: float = 0
    k1: float = 0
    k2: float = 0
    k3: float = 0
    p_1: float = 0
    p_2: float = 0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @width.setter
    def width(self, new_width: int):
        self._width = new_width
        self.__compute_ref_max()

    @height.setter
    def height(self, new_height: int):
        self._height = new_height
        self.__compute_ref_max()

    def __compute_ref_max(self):
        if self._width is None or self._height is None:
            return
        if self._width >= self.height:
            self._width_rel_max = 0.5
            self._height_rel_max = 0.5 * self._height / self._width
        else:
            self._height_rel_max = 0.5
            self._width_rel_max = 0.5 / self._height * self._width

    def perspective_pixel(self, rel_coords: (float, float, float)) -> (float, float):
        """
        Turns a relative coordinates coordinates [x,y,z] into a [u,v] camera coordinates
        https://opensfm.readthedocs.io/en/latest/geometry.html
        :param rel_coords: a three fload array
        :type rel_coords: list[float]
        :return:
        :rtype:
        """
        [x, y, z] = rel_coords
        x_n = x / z
        y_n = y / z
        r_2 = x_n * x_n + y_n * y_n
        d = 1 + r_2 * self.k1 + r_2 * r_2 * self.k2
        return self.focal * d * x_n, self.focal * d * y_n

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'focal': self.focal,
            'k1': self.k1,
            'k2': self.k2,
        }

    def in_frame(self, pixel: (float, float)) -> bool:
        return -self._width_rel_max <= pixel[0] <= self._width_rel_max and \
               -self._height_rel_max <= pixel[1] <= self._height_rel_max


def json_parse_camera(name: str, el: dict) -> Camera:
    camera = Camera()
    camera.name = name
    for k in ['width', 'height', 'projection_type', 'c_x', 'c_Y', 'k1', 'k2', 'k3', 'p1', 'p2']:
        camera.__setattr__(k, el.get(k, 0))
    if 'focal' in el:
        camera.focal = el['focal']
    else:
        if el['focal_x'] != el['focal_y']:
            raise Exception('Cannot survive different focal x/y %f/%f' % (el['focal_x'], el['focal_y']))
        camera.focal = el['focal_x']

    return camera
