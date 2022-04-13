# OpenDroneMap - A shot coverage report

From an [OpenDroneMap](https://www.opendronemap.org/) reconstruction, our goal is to see which part of the orthophoto is
covered by each shot.

We propose a web app with the orthophoto and camera positions displayed. Clicking on photo displays the covered area.

![](doc/snapshot-coverage.png)

## How to run it?

### How to install
You need Python >= 3.8

```
pip install odm-report-shot-coverage
```

### Processing

```
odm-report-shot-coverage PATH_TO_ODM_PROJECT
```

And follow the instructions to open the local web page. (Execution time is ~15 seconds for 60 images on a macbook pro)

## How does it work?

From an OpenDroneMap reconstruction (odm by default), the reports needs access to the files stored in the project
directory:

````
cameras.json
images/*
odm_report/shots.geojson
odm_report/stats.json
odm_orthophoto/odm_orthophoto.tif
odm_orthophoto/odm_orthophoto_corners.txt
odm_texturing_25d/odm_textured_model_geo.obj
````

The reporting tool `odm-report-shot-coverage.py` creates a directory `odm_report/shot_coverage` with a web
page (`index.html`) containing the interactive report.

### Browsing through the results

Open the `odm_report/shot_coverage/index.html` file and mouse over the shot position (blue dots) to see the image. Click
on one or more shot to display the ground boundaries.

### Limitations

#### No ray tracing

The shot boundaries are estimated based on the shot position and rotation, and the 2.5d model, but without ray tracing.
Therefore, The extent of the shot boundaries is projected behind a higher structure.

Our purpose was at first to tackle rather flat area, shot from above. Therefore, this limitation is not a big deal in
such situations.

#### Perspective projection

To map x,y,z points from the 2.5d model onto camera pixels, we use the
[*perspective* model](https://opensfm.readthedocs.io/en/latest/geometry.html#camera-models), as I have not found the
information for other projections (such as the *Brown*, used by the GoPro).

## Code Architecture

Two main components:
  * Python to reconstruct the shot boundaries, resize original images and set up the web app directory
  * A JavaScript + D3.js for the front end

### Python Processing

The code is in `src/` and the entry point [`odm_report_shot_coverage/scripts/report.py`](src/odm_report_shot_coverage/scripts/report.py).

Beside copying (and resizing) original images, setting up the web app, the main purpose is to recompute the shot boundaries:
  1. parse the 2.5d model from the `odm_texturing_25d` wavefront object file (only vertices are used)
  2. parse camera specs from `cameras.json`
  3. Extract the *native* coordinates system from `stats.json` 
  4. Get shot position + rotation from `shot.geojson`; shot positions are shifted from native to the 25d model/ortho photo 
  5. Convert and get the ortho photo boundaries
  6. For each vertex, see if they appear in the camera image (with the limitation of the perspective projective + absence of ray tracing described above)
  7. For each shot, compute the boundaries around the subset of vertices within each frame

### JavaScript

Base on the web app asset + files computed by the Python processing, the code uses some d3.js 

### CI/CD

Being hosted on Github, we use actions for the CI/CD:
 * testing the Python code (pytest)
 * linting and security check
 * deployment on Azure static web app

## Author

Alexandre Masselot (alexandre.masselot@gmail.com), with the help of the vibrant ODM community.

## License

MIT

