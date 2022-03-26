class Point:
    name: str
    coordinates: list[float]


def json_parse_point(name: str, el: dict) -> Point:
    point = Point()
    point.name = name
    point.coordinates = el['coordinates']
