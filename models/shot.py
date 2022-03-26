from models.camera import Camera


class Shot:
    image_name: str
    rotation: list[float]
    translation: list[float]
    camera: Camera


def json_parse_shot(image_name: str, el: dict, cameras: dict[str, Camera]) -> Shot:
    shot = Shot()
    shot.image_name = image_name
    shot.rotation = el['rotation']
    shot.translation=el['translation']
    shot.camera = cameras[el['camera']]

