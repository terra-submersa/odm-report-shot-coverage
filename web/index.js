const marginAxes = 30;
const dimensions = {
    total: {
        width: 500,
        height: 700
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

d3.json(`${projectDir}/reconstruction_shot_points.json`)
    .then(r => {
        const rec = parseReconstruction(r);
        initScales(rec);
        setupPoints(rec);
        setupShots(rec);
    })
    .then(() =>
        d3.json(`${projectDir}/odm_orthophoto_corners.json`)
    )
    .then(corners => {
        elOrthoImage
            .attr('x', scales.x(corners.x[0]))
            .attr('y', scales.y(corners.y[0]))
            .attr('width', scales.x(corners.x[1]) - scales.x(corners.x[0]))
        //.attr('height', scales.y(corners.y[1]) - scales.y(corners.y[0]));
    })
;


function parseReconstruction(json) {
    const rec = {
        points: json.points,
        shots: json.shots,
        shotPoints: json.shotPoints,
        shots: json.shots,
    };
    const xs = _.map(rec.points, p => p[0]);
    const ys = _.map(rec.points, p => p[1]);
    const zs = _.map(rec.points, p => p[2]);

    rec.coords_domain = {
        x: [_.min(xs), _.max(xs)],
        y: [_.min(ys), _.max(ys)],
        z: [_.min(zs), _.max(zs)],
    }
    console.log('coords_domain', rec.coords_domain)

    rec.pointShots = [];
    shots = {};
    _.each(rec.shots, (s) => shots[s.imageName] = s);
    _.each(rec.shotPoints, (points, img) => {
        _.each(points, p => {
            if (!rec.pointShots[p]) {
                rec.pointShots[p] = []
            }
            rec.pointShots[p].push(shots[img]);
        })
    });
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
                    .attr('cy', p => scales.y(p[1]))
                    .on('mouseover', p => {
                        selectedShots.length = 0;
                        _.each(reconstruction.pointShots[p.id], s => selectedShots.push(s));
                        updateShots();
                        updateSelectedPoint(p);
                    });
            },
            function (update) {
                update

            }
        )
}

function setupShots(reconstruction) {
    elShots
        .selectAll('circle.shot')
        .data(reconstruction.shots)
        .join(
            function (enter) {
                enter
                    .append('circle')
                    .classed('shot', true)
                    .attr('name', s => s.imageName)
                    .attr('r', 3)
                    .attr('cx', s => scales.x(s.translation[0]))
                    .attr('cy', s => scales.y(s.translation[1]))
                    .on('mouseover', s => {
                        console.log(s)
                    });
            },
            function (update) {
                update

            }
        )
}

function updateShots(reconstruction) {
    d3.select('#point-shots-list')
        .selectAll('li')
        .data(selectedShots, s => s.imageName)
        .join(
            enter =>
                enter
                    .append('li')
                    .text(s => s.imageName),
            update => update,
            exit => exit.remove()
        )
}

function updateSelectedPoint(p) {
    const el = d3.select('#selected-point');
    el.select('.id').text(p.id);
    el.select('.coordinates').text(`${p[0].toFixed(4)}, ${p[1].toFixed(4)}, ${p[2].toFixed(4)}`);

}

svg.insert('defs')
    .insert('clipPath')
    .attr('id', 'mapClipping')
    .insert('rect')
    .attr('width', dimensions.map.width)
    .attr('height', dimensions.map.height);

const elMapContainer = svg
    .insert('g')
    .classed('map', true)
    .attr('transform', `translate(${marginAxes},0)`)
    .style('clip-path', 'url(#mapClipping)');

const elMap =
    elMapContainer.insert('g');

const elOrthoImage = elMap.insert('image')
    .attr('href', `${projectDir}/odm_orthophoto.png`);

const elPoints = elMap
    .insert('g')
    .classed('points', true);

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
elMapContainer.call(zoom);

function handleZoom() {
    elMapContainer.attr('transform', d3.event.transform);
    elAxes.x.call(axes.x.scale(d3.event.transform.rescaleX(scales.x)));
    elAxes.y.call(axes.y.scale(d3.event.transform.rescaleY(scales.y)));
}

function initScales(reconstruction) {
    function ratio(l, domain) {
        return l / (domain[1] - domain[0])
    }

    const xd = ratio(dimensions.map.width - 20, reconstruction.coords_domain.x);
    const yd = ratio(dimensions.map.height - 20, reconstruction.coords_domain.y);
    let xDomain = reconstruction.coords_domain.x;
    let yDomain = reconstruction.coords_domain.y;
    if (yd < xd) {
        const padding = (xd / yd - 1) * (reconstruction.coords_domain.x[1] - reconstruction.coords_domain.x[0]) / 2;
        console.log('x padding', padding)
        xDomain = [reconstruction.coords_domain.x[0] - padding, reconstruction.coords_domain.x[1] + padding]
    } else {
        const padding = (yd / xd - 1) * (reconstruction.coords_domain.y[1] - reconstruction.coords_domain.y[0]) / 2
        yDomain = [reconstruction.coords_domain.y[0] - padding, reconstruction.coords_domain.y[1] + padding]
    }

    scales.x.domain(xDomain);
    scales.y.domain(yDomain);

    axes.x = d3.axisBottom(scales.x);
    axes.y = d3.axisLeft(scales.y);
    elAxes.x.call(axes.x);
    elAxes.y.call(axes.y);
}
