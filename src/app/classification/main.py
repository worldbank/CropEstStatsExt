import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

from datetime import datetime
import json
import numpy
import geemap
import ee
import traceback

ee.Initialize()

import imagery
import imageToVectors
import fromJsonToCsv
import getPolygonData
import trainClassifier

def main (
  bands: list,
  aoiPath: str,
  subNameField: str,
  extentPath: str,
  outputFolder: str,
  outputMode: int,
  trainingDatasetPath: str,
  classificationStart: str,
  classificationEnd: str,
  timeRef: str, # the time reference to output as a string in the final result
  nameProp: str,
  referenceStart: str,
  referenceEnd: str,
  outputFolder_images: str,
  outputFolder_vectors: str,
):

  print ('EE Data extraction - starting')
  time_start = datetime.now()

  # chunks = chunkFeatureSource.chunkFeatureSource('./data/input/grid_test_4326.geojson')
  # chunks = chunkFeatureSource.chunkFeatureSource2('./data/input/GMB/GMB_intersection.geojson')

  # bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
  extent = geemap.geojson_to_ee(extentPath)
  # nameProp = 'uid'
  # subNameField = 'rowcacode1'
  trainingDataset = geemap.geojson_to_ee(trainingDatasetPath)

  # Get the reference image for the reference year to train the classifier with.
  referenceImageData = imagery.get(extent, referenceStart, referenceEnd)
  print('##### Reference Image (Classifier) - bands : ' + ' '.join(referenceImageData["image"].bandNames().getInfo()))
  # print('##### Reference Image (Classifier) - size : ' + str(referenceImage.size().getInfo()))
  trained = trainClassifier.trainClassifier(referenceImageData["image"], bands, trainingDataset)

  # Provide an image to be classified.
  imageData = imagery.get(extent, classificationStart, classificationEnd)
  # print('##### Image for classification - bands : ' + ' '.join(imageData["image"].bandNames().getInfo()))
  if int(imageData["collectionSize"]) > 0:
    # print('##### Image for classification - size : ' + str(image.size().getInfo()))
    classified = imageData["image"].select(bands).classify(trained)
    croplands_classification = classified.eq(0).selfMask()
    # non_croplands_classification = classified.gt(0).selfMask()

    obs = imageData["collectionSize"]

    table = geemap.geojson_to_ee(aoiPath)
    count = 0
    values = []
    time_init = datetime.now()
    duration_init = time_init - time_start
    print ('Script initialized in ' + str(duration_init))
    length = 0
    featureIndex = 0
    uid = 0

    with open(aoiPath, 'r') as file:
      data = json.load(file)
      length = len(data['features'])
      print('##### Processing ' + str(length) + ' features')
      file.close()

    with open(outputFolder + 'batch.json', 'r') as batchRefFile:
      fileRef = json.load(batchRefFile)
      featureIndex = fileRef['nextFeatureIndex']
      batchRefFile.close()

    def loopThroughAoI(currentIndex):

      # for i in length:
      i = 0
      while i < length:
      # for x in data['features']:
        if i == currentIndex:
          x = data['features'][i]
          time_feature_start = datetime.now()
          # Get the current feature ID to filter out the featureCollection 
          uid = str(x['properties'][nameProp])
          filtered = table.filter(nameProp + " == " + uid)

          subName = x['properties'][subNameField]
          count = i + 1
          print('##### ' + str(count) + '/' + str(length) + ' - feature id: ' + str(uid) + ' (' + str(subName) + ')')

          time_image_start = datetime.now()
          # Export the classified image clipped with the featureCollection geometry
          singleImage_croplands = croplands_classification.clip(filtered.geometry())
          # singleImage_noncroplands = non_croplands_classification.clip(filtered.geometry())
          # singleImage_noncroplands = imageData["image"].clip(filtered.geometry())
          
          
          if (outputMode > 1):
            # Download classified croplands images
            geemap.ee_export_image(singleImage_croplands, outputFolder_images + str(uid) + '.tif', 30)
            print('##### ' + outputFolder_images + str(uid) + '_croplands.tif' + ' exported')

            geemap.ee_export_image(singleImage_noncroplands, outputFolder_images + str(uid) + '.tif', 30)
            print('##### ' + outputFolder_images + str(uid) + '_non_croplands.tif' + ' exported')
          
          time_image_end = datetime.now()
          duration_image = time_image_end - time_image_start
          print('##### feature id: ' + str(uid) + ' (' + str(subName) + ')' + ' Image processed successfully in ' + str(duration_image))

          # Export the croplands geometry and the calculated values
          time_vector_start = datetime.now()
          subCroplands_Classification = imageToVectors.imageToVectors(singleImage_croplands, filtered.first())
          # non_subCroplands_Classification = imageToVectors.imageToVectors(singleImage_noncroplands, filtered.first())
          non_subCroplands_Classification = imageToVectors.imageToVectors(singleImage_croplands, filtered.first())
          # non_subCroplands_Classification = subCroplands_Classification
          
          props = {
            'id': uid,
            'period': timeRef,
            'subregion': subName,
            'obs': obs
          }
          time_values_start = datetime.now()


          
          if subCroplands_Classification.size().getInfo() > 0:
            # EXTRA STATISTICS
            ## CHIRPS
            chirpsSource = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filter(ee.Filter.date(referenceStart, referenceEnd)).filterBounds(subCroplands_Classification.geometry().bounds())
            obs_chirps = str(chirpsSource.size().getInfo())
            chirpsImage = chirpsSource.reduce('mean').clip(subCroplands_Classification)
            props['obs_chirps'] = obs_chirps
            if (outputMode > 2):
              # Download classified croplands vectors
              geemap.ee_export_geojson(subCroplands_Classification, outputFolder_vectors + str(uid) + '_crops.geojson')
              print('##### ' + outputFolder_vectors + str(uid) + '_crops.geojson' + ' exported')

              geemap.ee_export_geojson(non_subCroplands_Classification, outputFolder_vectors + str(uid) + '_non_crops.geojson')
              print('##### ' + outputFolder_vectors + str(uid) + '_non_crops.geojson' + ' exported')

            time_vector_end = datetime.now()
            duration_vector = time_vector_end - time_vector_start
            print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' Vectors processed successfully in ' + str(duration_vector))

            time_values_start = datetime.now()
            geom_croplands = subCroplands_Classification.geometry()
            # area_Classification_sqM = geemap.ee_num_round(geom_croplands.area(1), 0)
            area_Classification_sqM = geom_croplands.area(1)
            imageForValues = imageData["image"].select(['NDVI']).clip(geom_croplands)
            indicators = getPolygonData.getPolygonData(imageForValues, 'NDVI', geom_croplands, 4)
            props['area_sqm_crops'] = area_Classification_sqM.getInfo()
            props['crops_ndvi_min'] = indicators['min'].getInfo()
            props['crops_ndvi_mean'] = indicators['mean'].getInfo()
            props['crops_ndvi_median'] = indicators['median'].getInfo()
            props['crops_ndvi_max'] = indicators['max'].getInfo()
            props['crops_ndvi_stddev'] = indicators['stdDev'].getInfo()
            
            # CHIRPS
            imageForValuesChirps = chirpsImage.select(['precipitation_mean']).clip(geom_croplands)
            indicatorsChirps = getPolygonData.getPolygonData(imageForValuesChirps, 'precipitation_mean', geom_croplands, 4)
            props['crops_chirps_min'] = indicatorsChirps['min'].getInfo()
            props['crops_chirps_mean'] = indicatorsChirps['mean'].getInfo()
            props['crops_chirps_median'] = indicatorsChirps['median'].getInfo()
            props['crops_chirps_max'] = indicatorsChirps['max'].getInfo()
            props['crops_chirps_stddev'] = indicatorsChirps['stdDev'].getInfo()

          else:
            duration_vector = 0
            time_values_start = datetime.now()
            props['area_sqm_crops'] = 0
            props['crops_ndvi_min'] = -999
            props['crops_ndvi_mean'] = -999
            props['crops_ndvi_median'] = -999
            props['crops_ndvi_max'] = -999
            props['crops_ndvi_stddev'] = -999
            props['crops_chirps_min'] = -999
            props['crops_chirps_mean'] = -999
            props['crops_chirps_median'] = -999
            props['crops_chirps_max'] = -999
            props['crops_chirps_stddev'] = -999

          # if non_subCroplands_Classification.size().getInfo() > 0:
          # EXTRA STATISTICS
          ## CHIRPS
          chirpsImage = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filter(ee.Filter.date(referenceStart, referenceEnd)).filterBounds(non_subCroplands_Classification.geometry().bounds()).reduce('mean').clip(non_subCroplands_Classification)

          geom_noncroplands = non_subCroplands_Classification.geometry()
          area_Classification_sqM_nonCrops = geemap.ee_num_round(geom_noncroplands.area(1), 0)
          imageForValues = imageData["image"].select(['NDVI']).clip(geom_noncroplands)
          indicatorsNonCroplands = getPolygonData.getPolygonData(imageForValues, 'NDVI', geom_noncroplands, 4)
          props['area_sqm_non_crops'] = area_Classification_sqM_nonCrops.getInfo()
          props['non_crops_ndvi_min'] = indicatorsNonCroplands['min'].getInfo()
          props['non_crops_ndvi_mean'] = indicatorsNonCroplands['mean'].getInfo()
          props['non_crops_ndvi_median'] = indicatorsNonCroplands['median'].getInfo()
          props['non_crops_ndvi_max'] = indicatorsNonCroplands['max'].getInfo()
          props['non_crops_ndvi_stddev'] = indicatorsNonCroplands['stdDev'].getInfo()
          
          # CHIRPS
          imageForValuesChirpsNonCroplands = chirpsImage.select(['precipitation_mean']).clip(geom_noncroplands)
          indicatorsChirpsNonCroplands = getPolygonData.getPolygonData(imageForValuesChirpsNonCroplands, 'precipitation_mean', geom_croplands, 4)
          props['non_crops_chirps_min'] = indicatorsChirpsNonCroplands['min'].getInfo()
          props['non_crops_chirps_mean'] = indicatorsChirpsNonCroplands['mean'].getInfo()
          props['non_crops_chirps_median'] = indicatorsChirpsNonCroplands['median'].getInfo()
          props['non_crops_chirps_max'] = indicatorsChirpsNonCroplands['max'].getInfo()
          props['non_crops_chirps_stddev'] = indicatorsChirpsNonCroplands['stdDev'].getInfo()

        # else:
          duration_vector = 0
          time_values_start = datetime.now()
          props['area_sqm_non_crops'] = 0
          props['non_crops_ndvi_min'] = -999
          props['non_crops_ndvi_mean'] = -999
          props['non_crops_ndvi_median'] = -999
          props['non_crops_ndvi_max'] = -999
          props['non_crops_ndvi_stddev'] = -999
          props['non_crops_chirps_min'] = -999
          props['non_crops_chirps_mean'] = -999
          props['non_crops_chirps_median'] = -999
          props['non_crops_chirps_max'] = -999
          props['non_crops_chirps_stddev'] = -999

          time_values_end = datetime.now()
          duration_values = time_values_end - time_values_start

          props['duration_image'] = str(duration_image)
          props['duration_vector'] = str(duration_vector)
          props['duration_values'] = str(duration_values)

          time_feature_end = datetime.now()
          duration_feature = time_feature_end - time_feature_start

          props['duration_total'] = str(duration_feature)
          
          print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' Values retrieved successfully in ' + str(duration_values))

          print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' done in ' + str(duration_feature))
          values.append(props)
          # single_valueFile = open('./data/output/GMB_values/' + str(uid) + '.json', 'w')
          with open(outputFolder + str(uid) + '.json', 'w') as single_valueFile:
            json.dump(props, single_valueFile)
            single_valueFile.close()
            print('##### ' + outputFolder + str(uid) + '.json' + ' exported')

          with open(outputFolder + 'batch.json', 'r') as batchRefFile:
            followUpData = json.load(batchRefFile)
            followUpData['nextFeatureIndex'] = followUpData['nextFeatureIndex'] + 1
            batchRefFile.close()

          with open(outputFolder + 'batch.json', 'w') as batchRefFile:
            batchRefFile.write(json.dumps(followUpData))
            batchRefFile.close()

          # with open(outputFolder + 'batch.json', 'w+') as batchRefFile:
          #   fileRef = json.load(batchRefFile)
          #   fileRef['nextFeatureIndex'] = currentIndex
          #   json.load(fileRef, batchRefFile)
          #   batchRefFile.close()
        i += 1
      # all_valuesFile = open('./data/output/GMB_values/' + 'VALUES' + '.json', 'w')
      with open(outputFolder + 'VALUES' + '.json', 'w') as all_valuesFile:
        json.dump(values, all_valuesFile)
        all_valuesFile.close()
      
      fromJsonToCsv.fromJsonToCsv(outputFolder + 'VALUES' + '.json', outputFolder + 'VALUES' + '.csv')




    # loopThroughAoI(featureIndex)

    while featureIndex < length:
      try:
        loopThroughAoI(featureIndex)
        featureIndex += 1
        with open(outputFolder + 'batch.json', 'r') as batchRefFile:
          ref = json.load(batchRefFile)
        with open(outputFolder + 'batch.json', 'w') as batchRefFile:
          ref['attempts'] = 0
          batchRefFile.write(json.dumps(ref))
          batchRefFile.close()
      except Exception as e:
        print('##### Exception')
        print(e)
        print('##### Traceback')
        traceback.print_tb(e.__traceback__)
        with open(outputFolder + 'batch.json', 'r') as batchRefFile:
          fileRef = json.load(batchRefFile)
          if fileRef['attempts'] > 1:
            fileRef['attempts'] = 0
            featureIndex = featureIndex + 1
            if featureIndex < length:
              print('Extraction failed 5 times for featureIndex ' + str(featureIndex) + ', going for the next one')
              batchRefFile.close()
              with open(outputFolder + 'batch.json', 'w') as batchRefFile2:
                fileRef['nextFeatureIndex'] = featureIndex
                batchRefFile2.write(json.dumps(fileRef))
                batchRefFile2.close()
            else:
              print('Extraction completed - Failed on the last feature')
              break
          else:
            stringError = ''.join(traceback.format_exception(None, e, e.__traceback__))
            errorReport = {
              'elementID': uid,
              'error': stringError
            }
            fileRef['errors'].append(errorReport)
            fileRef['attempts'] = fileRef['attempts'] + 1
            batchRefFile.close()
            with open(outputFolder + 'batch.json', 'w') as batchRefFile3:
              batchRefFile3.write(json.dumps(fileRef))
              batchRefFile3.close()

  time_end = datetime.now()
  duration_all = time_end - time_start
  print('##### Extraction completed in ' + str(duration_all))

  # while True:
  #   if featureIndex < length:
  #     try:
  #       print('try')
  #       loopThroughAoI(featureIndex)
  #     except:
  #       print('except')
  #       # with open(outputFolder + 'batch.json', 'r') as batchRefFile:
  #       #   fileRef = json.load(batchRefFile)
  #       #   if fileRef['attempts'] > 4:
  #       #     fileRef['nextFeatureIndex'] = fileRef['nextFeatureIndex'] + 1
  #       #     if fileRef['nextFeatureIndex'] < length:
  #       #       print('Extraction failed 5 times for featureIndex ' + str(fileRef['nextFeatureIndex'] - 1) + ', going for the next one')
  #       #       batchRefFile.close()
  #       #       with open(outputFolder + 'batch.json', 'w') as batchRefFile2:
  #       #         batchRefFile2.write(json.dumps(fileRef))
  #       #         batchRefFile2.close()
  #       #       loopThroughAoI(featureIndex)
  #       #     else:
  #       #       print('Extraction completed - Failed on the last feature')
  #       #   else:
  #       #     fileRef['attempts'] = fileRef['attempts'] + 1
  #       #     batchRefFile.close()
  #       #     with open(outputFolder + 'batch.json', 'w') as batchRefFile3:
  #       #       batchRefFile3.write(json.dumps(fileRef))
  #       #       batchRefFile3.close()
  #       #       loopThroughAoI(featureIndex)
  #   else:




