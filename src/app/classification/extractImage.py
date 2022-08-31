import json
import ee
ee.Initialize()

import geemap

geojsonPath = './eval/EVAL_data4/init_aoi_intersection.geojson'
uid = 'uid'
outputFolder = './eval/EVAL_data4/temp/'

dataset_ESA_WorldCover_v100 = ee.ImageCollection("ESA/WorldCover/v100").filterDate('2020-01-01', '2020-12-31')
def ESA_WorldCover_v100 (
    aoi: ee.FeatureCollection
) -> ee.Image:
  bounds = aoi.geometry().bounds()
  filteredDataset = dataset_ESA_WorldCover_v100.filterBounds(bounds).first()
  clipped_dataset = filteredDataset.clip(aoi.geometry())
  croplands = clipped_dataset
  return croplands

# tableSource = ee.FeatureCollection('users/andreasrey/NER_adm3')
# table = tableSource.filter("adm_03 == 'Say'")

# table = geemap.geojson_to_ee('./data/input/test_square84.geojson')
# image = ESA_WorldCover_v100(table)
# geemap.ee_export_image(image, './data/output/image6.tif', 10)

table = geemap.geojson_to_ee(geojsonPath)

count = 0
with open(geojsonPath, 'r') as file:
    data = json.load(file)
    print(len(data['features']))
    for x in data['features']:
        id = str(x['properties'][str(uid)])
        filtered = table.filter(str(uid) + " == " + str(id))
        # filePath = './data/output/filter_geojson_' + str(count) + '.geojson'
        # print(filePath)
        # geemap.ee_export_geojson(filtered, filePath)
        image = ESA_WorldCover_v100(filtered)
        geemap.ee_export_image(image, outputFolder + 'image_' + str(count) + '.tif', 10)
        
        count += count + 1
        print(count)