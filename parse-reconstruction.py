import json

from models.reconstruction import json_parse_reconstruction_collection

if __name__ == '__main__':
    with open('resources/reconstruction.json') as fd:
        reconstruction = json_parse_reconstruction_collection(json.load(fd))[0]
        for shot in [s for s in reconstruction.shots if
                     s.image_name in {'GOPR3101.jpeg', 'GOPR3102.jpeg', 'GOPR3103.jpeg', 'GOPR3104.jpeg',
                                      'GOPR3105.jpeg', }
                     ]:
            # s.image_name in {'GOPR3101.jpeg','GOPR3102.jpeg','GOPR3105.jpeg', 'GOPR3084.jpeg', 'GOPR3123.jpeg', }]:
            print('-------- %s ' % shot)

            in_points = [];
            for point in reconstruction.points:
                pixel = shot.camera_pixel(point.coordinates)
                if shot.camera.in_frame(pixel):
                    in_points.append(point.coordinates)

            cx = [p[0] for p in in_points]
            cx.sort()
            cx_med = cx[int(len(cx) / 2)]
            cx_min = cx[int(len(cx) * 0.02)]
            cx_max = cx[int(len(cx) * 0.98)]

            cy = [p[1] for p in in_points]
            cy.sort()
            cy_med = cy[int(len(cx) / 2)]
            cy_min = cy[int(len(cx) * 0.02)]
            cy_max = cy[int(len(cx) * 0.98)]

            cz = ([p[2] for p in in_points])
            cz.sort()
            cz_med = cz[int(len(cz) / 2)]
            cz_min = cz[int(len(cx) * 0.02)]
            cz_max = cz[int(len(cx) * 0.98)]
            print('%d points (%.2f, %.2f, %.2f) (%.2f, %.2f, %.2f) %.2f x %.2f x %.2f ' % (
                len(in_points),
                cx_med, cy_med, cz_med,
                (cx_min + cx_max) / 2, (cy_min + cy_max) / 2, (cz_min + cz_max) / 2,
                cx_max - cx_min, cy_max - cy_min, cz_max - cz_min))
            p1 = (shot.translation[0], shot.translation[1], shot.translation[2] + 3)
            print('camera_relative_coordinates at the vertical: %s' % shot.camera_relative_coordinates(p1))
            print('camera pixel at the vertical: %s' % str(shot.camera_pixel(p1)))
            cz_mid = (cz_max - cz_min) / 2
            print('camera pixel min,min: %s' % str(shot.camera_pixel((cx_min, cy_min, cz_med))))
            print('camera pixel max,nax: %s' % str(shot.camera_pixel((cx_max, cy_max, cz_med))))
            # print('min: %s' % str(coords_min))
            # print('max: %s' % str(coords_max))
