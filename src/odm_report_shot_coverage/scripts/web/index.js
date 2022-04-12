function loadData() {
    const marginAxes = 50;
    const dimensions = {
        total: {
            width: 500,
            height: window.innerHeight - 100
        }
    }

    const scales = {};
    const axes = {};

    const selectedShots = [];

    const elSvgContainer = d3.select('#svg-container');
    const svg = d3.select('svg')
        .attr('width', elSvgContainer.node().clientWidth)
        .attr('height', dimensions.total.height)

    setupDimensions(elSvgContainer.node().clientWidth, dimensions.total.height)

    const projectDir = './data'

    d3.json(`${projectDir}/reconstruction_shots.json`)
        .then(r => {
            const rec = parseReconstruction(r);
            initScales(rec);
            //setupPoints(rec);
            refreshShots(rec);
        })
        .then(() =>
            d3.json(`${projectDir}/odm_orthophoto_corners.json`)
        )
        .then(corners => {
            elOrthoImage
                .attr('x', scales.x(corners.x[0]))
                .attr('y', scales.y(corners.y[1]))
                .attr('width', scales.x(corners.x[1]) - scales.x(corners.x[0]))
            //.attr('height', scales.y(corners.y[1]) - scales.y(corners.y[0]));
        });


    function parseReconstruction(json) {
        const rec = {
            points: json.points,
            shots: json.shots,
            cameras: json.cameras,
            boundaries: json.boundaries,
        };
        rec.shots.forEach(s => s.camera = rec.cameras[s.camera]);

        rec.shots.forEach(s => s.isSelected = false);
        rec.coordsDomain = {
            x: [rec.boundaries.xMin, rec.boundaries.xMax],
            y: [rec.boundaries.yMin, rec.boundaries.yMax],
        }
        return rec;
    }

    function setupDimensions(width, height) {
        dimensions.total.width = width;
        dimensions.total.height = height;
        dimensions.map = {
            width: dimensions.total.width - marginAxes,
            height: dimensions.total.height - marginAxes
        }
        scales.x = d3.scaleLinear()
            .range([10, dimensions.map.width - 10]);

        scales.y = d3.scaleLinear()
            .range([10, dimensions.map.height - 10]);
    }

    function setupPoints(reconstruction) {
        elPoints
            .selectAll('circle.point')
            .data(reconstruction.points)
            .join(
                function (enter) {
                    enter
                        .append('circle')
                        .classed('point', true)
                        .attr('r', 0.3)
                        .attr('cx', p => scales.x(p[0]))
                        .attr('cy', p => scales.y(p[1]));
                },
                function (update) {
                    update

                }
            )
    }

    function toggleShot(shot, reconstruction) {
        shot.isSelected = !shot.isSelected;
        refreshShots(reconstruction)
    }

    function refreshShots(reconstruction) {

        const line = d3.line()
            .x(function (d, i) {
                return scales.x(d[0]);
            })
            .y(function (d) {
                return scales.y(d[1]);
            })
        elShotCoverage
            .selectAll('path.shot-coverage')
            .data(reconstruction.shots)
            .join(
                function (enter) {
                    enter
                        .append('path')
                        .classed('shot-coverage', true)
                        .attr('name', s => s.imageName)
                        .attr('d', s => {
                            const p = [...s.boundaries.path];
                            p.push(s.boundaries.path[0]);
                            return line(p);
                        });
                },
                function (update) {
                    update
                        .classed('is-selected', s => s.isSelected);
                }
            );
        elShots
            .selectAll('circle.shot')
            .data(reconstruction.shots)
            .join(
                function (enter) {
                    enter
                        .append('circle')
                        .classed('shot', true)
                        .attr('name', s => s.imageName)
                        .attr('r', 7)
                        .attr('cx', s => scales.x(s.translation[0]))
                        .attr('cy', s => scales.y(s.translation[1]))
                        .on('mouseover', s => {
                            showShot(s);
                        })
                        .on('click', s => toggleShot(s, reconstruction));
                },
                function (update) {
                    update
                        .classed('is-selected', s => s.isSelected)
                }
            )
    }

    function showShot(shot) {
        const el = d3.select('#selected-camera');
        el.style('display', 'inherit');
        el.select('.image-name').text(shot.imageName);
        el.select('img.snapshot').attr('src', 'images/' + shot.imageName);
        el.select('.coordinates').text(`${shot.translation[0].toFixed(2)}, ${shot.translation[1].toFixed(2)}, ${shot.translation[1].toFixed(2)}`);
        const euler = shot.rotationEulerXYZ.map(x => (x * 180 / Math.PI).toFixed(2))
        el.select('.rotation').text(`${euler[0]}°, ${euler[1]}°, ${euler[2]}°`);

        const elWidth = el.node().clientWidth * 0.9;
        const {width, height} = shot.originalDimensions
        const alpha = Math.sqrt(width * width + height * height) / elWidth;
        const widthImage = width / alpha;
        const heightImage = height / alpha;
        el.select('.rotator')
            .style('width', `${elWidth}px`)
            .style('height', `${elWidth}px`);
        el.select('img.snapshot')
            .style('transform', `translate(${elWidth / 2 - widthImage / 2}px, ${elWidth / 2 - heightImage / 2}px) rotate(-${euler[2]}deg)`)
            .style('width', `${widthImage}px`)
            .style('height', `${heightImage}px`);

    }

    svg.insert('defs')
        .insert('clipPath')
        .attr('id', 'mapClipping')
        .insert('rect')
        .attr('x', 3)
        .attr('y', 3)
        .attr('width', dimensions.map.width - 6)
        .attr('height', dimensions.map.height - 6);

    const elMapContainer = svg
        .insert('g')
        .attr('transform', `translate(${marginAxes},0)`)
        .attr('id', 'map-container')
        .style('clip-path', 'url(#mapClipping)')

    elMapContainer.insert('rect')
        .attr('width', dimensions.map.width)
        .attr('height', dimensions.map.height)

    const elMap =
        elMapContainer.insert('g')
            .attr('id', 'map');

    const elOrthoImage = elMap.insert('image')
        .attr('href', `${projectDir}/odm_orthophoto.png`);

    const elPoints = elMap
        .insert('g')
        .classed('points', true);

    const elShotCoverage = elMap
        .insert('g')
        .classed('shot-coverage', true);

    const elShots = elMap
        .insert('g')
        .classed('shots', true);

    const elAxes = {};

    elAxes.x = svg
        .insert('g')
        .attr("class", "axis axis--x")
        .attr('transform', `translate(${marginAxes}, ${dimensions.map.height})`);
    elAxes.y = svg
        .insert('g')
        .attr("class", "axis axis--y")
        .attr('transform', `translate(${marginAxes}, 0)`);

    const zoom = d3.zoom()
        .on('zoom', handleZoom);
    elMap.call(zoom);

    function handleZoom() {
        elMap.attr('transform', d3.event.transform);
        elAxes.x.call(axes.x.scale(d3.event.transform.rescaleX(scales.x)));
        elAxes.y.call(axes.y.scale(d3.event.transform.rescaleY(scales.y)));
    }

    function initScales(reconstruction) {
        function ratio(l, domain) {
            return l / (domain[1] - domain[0])
        }

        const xd = ratio(dimensions.map.width - 20, reconstruction.coordsDomain.x);
        const yd = ratio(dimensions.map.height - 20, reconstruction.coordsDomain.y);
        let xDomain = reconstruction.coordsDomain.x;
        let yDomain = reconstruction.coordsDomain.y;
        if (yd < xd) {
            const padding = (xd / yd - 1) * (reconstruction.coordsDomain.x[1] - reconstruction.coordsDomain.x[0]) / 2;
            xDomain = [reconstruction.coordsDomain.x[0] - padding, reconstruction.coordsDomain.x[1] + padding]
        } else {
            const padding = (yd / xd - 1) * (reconstruction.coordsDomain.y[1] - reconstruction.coordsDomain.y[0]) / 2
            yDomain = [reconstruction.coordsDomain.y[0] - padding, reconstruction.coordsDomain.y[1] + padding]
        }

        scales.x.domain(xDomain);
        scales.y.domain([yDomain[1], yDomain[0]]);

        axes.x = d3.axisBottom(scales.x);
        axes.y = d3.axisLeft(scales.y);
        elAxes.x.call(axes.x);
        elAxes.y.call(axes.y);
    }
}

loadData();
