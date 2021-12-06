# GeoJson Analyzer

## Intro
This demo looks at a set of building footprints, and generates a list of what buildings are within 5 meters of each other.

This script takes a geojson as input and for each polygon:

* calculates the polygon centroid (the "point_average")
* calculates if the centroid is within 5 meters of any other points (the "overlap")

This is done using shapely and geopandas. To calulate the overlap, a buffer of 2.5 meters is made for each centroid, and the buffers are overlaid on themselves. If any buffer_ids come out as unique id's between the two features, we know that these two points are within 5 meters of each other.


## Installation

### Windows
I have found that installing geospatial libraries in general is much easier on windows machines using `pipwin`

If on windows, please install using the following commands:

```
pip install wheel
pip install halo
pip install pipwin

pipwin install -r requirements.txt
```

### Not Windows

For anything not windows, you should be able to install using `pip install -r requirements.txt`

## Run

To run this script from the root diretory of this project run:

`python -m run --input=path_to_input.geojson --output=path_to_output.geojson`

For example, with `challenge_footprints.geojson` in the root directory:

`python -m run --input=challenge_footprints.geojson --output=output.geojson`

The `--input` flag is required to ensure we are working with the correct input data. The `--output` flag is optional and will default to `./output.geojson`

| flag      | info |
|-----------|------|
| `--input` | **Required** The path to the input file. Must be .json or .geojson|
| `--output`| **Optional** The path to the output file. Must be .json or .geojson. Defaults to `output.geojson`

An output file should be populated in the root directory with your output GeoJSON!
