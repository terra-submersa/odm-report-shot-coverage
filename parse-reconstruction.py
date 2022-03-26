import json

from models.reconstruction import json_parse_reconstruction_collection

if __name__ == '__main__':
    with open('resources/reconstruction.json') as fd:
        reconstruction = json_parse_reconstruction_collection(json.load(fd))[0]
        for point in reconstruction.points:
            for shot in reconstruction.shots:
                pixel = shot.camera_pixel(point.coordinates)
                if shot.camera.in_frame(pixel):
                    print('%s/%s\t%s\t(%s, %s)' % (point.name, shot.image_name, pixel, point.coordinates[0], point.coordinates[1]))
