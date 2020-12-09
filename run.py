import sys
import geopandas as gpd
import json
from halo import Halo


def run(fp):
    """Main Function that finds polygon centroids, buffers them to 2.5 meter radius, and checks for overlaps

    Args:
        fp (str): file path point to the geojson to transform. For an example of the geojson format please reference https://tools.ietf.org/html/rfc7946#section-1.5

    Returns:
        [dict]: the output geojson to be written, including the centroid and overlap boolean in the properties.
    """

    crs = json.load(open(fp, 'r')).get('crs', {}).get('properties', {}).get('name') # get crs from geojson directly to force crs later on
    footprints = gpd.read_file(fp) # read geojson as a geopandas GeoDataFrame
    
    if crs:
        footprints = footprints.set_crs(crs, allow_override=True)   # geopandas wanted to read the data in the wrong coordinate system, so I pulled the crs from 
                                                                    # the geojson and forced it into the correct coordinate system

    point_average = footprints[['geometry']].centroid # take the shapely geometries centroid
    buffer = gpd.GeoDataFrame(point_average.buffer(2.5), columns=['geometry']) # buffer of 2.5 meter radius

    buffer['id'] = buffer.index # keep the buffers index to easly sort overlap booleans later
    with Halo(text='overlaying buffered points, this will take a minute...'): # Overlay takes a bit so added a spinner
        overlay = gpd.overlay(buffer, buffer, how='union') # overlay shapes. Any shapes that form a union are within each other's radiuses (2.5m radius + 2.5m radius = 5m)
    print('overlay complete!')

    overlay.dropna(inplace=True) # drop any null ids 
    overlap_idxs = overlay[overlay[['id_1']].values != overlay[['id_2']].values].loc[:, 'id_1'] # this keeps any overlaps where the ids of the buffers are not equal (i.e. unique shapes overlap)
    overlap_idxs = sorted(list(set(overlap_idxs.astype('int')))) # converts overlap ids to a list
    print(f'{len(overlap_idxs)} unique buffered points overlap each other!')

    footprints['overlaps'] = False #set all overlap values to false
    footprints.loc[overlap_idxs, 'overlaps'] = True # sets any index of an overlap id to true, else it stays false
    footprints['point_average'] = point_average.apply(lambda point: list(point.coords)) # converts shapley Point to xy coords

    return json.loads(footprints.to_json()) # returns geojson


if __name__ == '__main__':

    args = {k: v for k, v in [i.split('=') for i in sys.argv[1:] if '=' in i]}

    fp = args.get('--input')
    if not fp:
        print("the --input flage is required. Please specify as --input=path_to_input.geojson")
        sys.exit(0)

    if not any([fp.endswith('.geojson'), fp.endswith('.json')]):
        print("input format must be a .geojson or a .json")
        sys.exit(0)

    output_fp = args.get('--output') if args.get('--output') else 'output.geojson'
    if not any([output_fp.endswith('.geojson'), output_fp.endswith('.json')]):
        print("output format must be a .geojson or a .json")
        sys.exit(0)
  
    print('starting analysis...')
    geojson = run(fp)
    print('analysis completed! Writing out output file...')
    
    json.dump(geojson, open(output_fp, 'w'), indent=4)
    print(f'writing completed! Output can be found at: {output_fp}')