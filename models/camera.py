class Camera:
    name: str
    width: int
    height: int
    focal: float
    k1: float
    k2: float

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

    @staticmethod
    def in_frame(pixel: (float, float)) -> bool:
        return -0.5 <= pixel[0] <= 0.5 and -0.5 <= pixel[1] <= 0.5


def json_parse_camera(name: str, el: dict) -> Camera:
    camera = Camera()
    camera.name = name
    camera.width = el['width']
    camera.height = el['height']
    if 'focal' in el:
        camera.focal = el['focal']
    else:
        if el['focal_x'] != el['focal_y']:
            raise Exception('Cannot survive different focal x/y %f/%f' % (el['focal_x'], el['focal_y']))
        camera.focal = el['focal_x']
    camera.k1 = el['k1']
    camera.k2 = el['k2']
    return camera
