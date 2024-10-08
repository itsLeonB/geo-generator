import random
from shapely.geometry import Polygon, Point, shape
import json


def generate_random_points_in_polygon(polygon, num_points):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < num_points:
        random_point = Point(random.uniform(minx, maxx),
                             random.uniform(miny, maxy))
        if polygon.contains(random_point):
            print("Generated:", random_point)
            points.append([random_point.x, random_point.y])
    return points


def main():
    data_points = {}
    with open('data/jakarta.geo.json', 'r') as file:
        data = json.load(file)
        for geojson_polygon in data['features']:
            print(
                f"Generating coordinates in{geojson_polygon['properties']['name']}")
            polygon_coords = geojson_polygon['geometry']['coordinates'][0]
            polygon = Polygon(polygon_coords)
            points = generate_random_points_in_polygon(polygon, 30000)
            data_points[geojson_polygon['properties']['name'].strip()] = points

    with open('data/bogor.geo.json', 'r') as file:
        name = "BOGOR"
        data = json.load(file)
        polygon = shape(data['features'][0]['geometry'])
        print(f"Generating coordinates in {name}")
        points = generate_random_points_in_polygon(polygon, 150000)
        data_points[name] = points

    files = ['depok.geo.json', 'tangerang.geo.json', 'bekasi.geo.json']
    for file in files:
        name = file.split('.')[0].upper()
        with open('data/' + file, 'r') as geojson_file:
            data = json.load(geojson_file)
            print(f"Generating coordinates in {name}")
            polygon_coords = data['coordinates'][0][0]
            polygon = Polygon(polygon_coords)
            points = generate_random_points_in_polygon(polygon, 150000)
            data_points[name] = points

    with open('data_points.json', 'w') as file:
        json.dump(data_points, file, indent=2)


if __name__ == '__main__':
    main()
