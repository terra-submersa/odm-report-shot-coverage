class Point:
    id: int
    coordinates: (float, float, float)


def json_parse_point(name: str, el: dict) -> Point:
    point = Point()
    point.id = int(name)
    point.coordinates = el['coordinates']
    return point
