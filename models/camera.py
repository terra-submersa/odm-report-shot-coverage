class Camera:
    width: int
    height: int
    focal: float
    k1: float
    k2: float


def json_parse_camera(el: dict) -> Camera:
    camera = Camera()
    camera.width = el['width']
    camera.height = el['height']
    if el['focal_x'] != el['focal_y']:
        raise Exception('Cannot survive different focal x/y %f/%f' % (el['focal_x'], el['focal_y']))
    camera.focal = el['focal_x']
    camera.k1 = el['k1']
    camera.k2 = el['k2']
    return camera
