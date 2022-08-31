# FROM https://developers.google.com/earth-engine/tutorials/community/landsat-etm-to-oli-harmonization

import ee
import datetime
import calculateExtraBands

NIR = "NIR_mean"
Red = "Red_mean"
SWIR = "SWIR1_mean"

# Define coefficients supplied by Roy et al. (2016) for translating ETM+ \
# surface reflectance to OLI surface reflectance.
ee.Initialize()
coefficients = {
  'itcps': ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]).multiply(10000),
  'slopes': ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
}

# Define function to get and rename bands of interest from OLI.
def renameOli(img):
  return img.select(
      ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
      ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])

# Define function to get and rename bands of interest from ETM+.
def renameEtm(img):
  return img.select(
      ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
      ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])

# Define function to apply harmonization transformation.
def etmToOli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
      .multiply(coefficients['slopes']) \
      .add(coefficients['itcps']) \
      .round() \
      .toShort() \
      .addBands(img.select('pixel_qa'))

# Define function to mask out clouds and cloud shadows.
def fmask(img):
  cloudShadowBitMask = 1 << 3
  cloudsBitMask = 1 << 5
  qa = img.select('pixel_qa')
  mask = qa.bitwiseAnd(cloudShadowBitMask) \
                  .eq(0) \
                  .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
  return img.updateMask(mask)

# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = renameOli(img)
#   img = fmask(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# Define function to prepare ETM+ images.
def prepEtm(img):
  orig = img
  img = renameEtm(img)
#   img = fmask(img)
  img = etmToOli(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

# date format
format = '%Y-%m-%d'

# thresholds
date_2012 = datetime.datetime.strptime('2011-12-31', format)
date_2013 = datetime.datetime.strptime('2012-12-31', format)

def getHarmonizedCollection(
  aoi: ee.FeatureCollection,
  startDate: str,
  endDate: str
) -> ee.ImageCollection :

  startDoy = ee.Date(startDate).getRelative('day', 'year')
  endDoy = ee.Date(endDate).getRelative('day', 'year')
  # Define a collection filter.
  colFilter = ee.Filter.And(
      # ee.Filter.bounds(aoi), ee.Filter.calendarRange(startDoy, endDoy, 'day_of_year'),
      # ee.Filter.lt('CLOUD_COVER', 50), ee.Filter.lt('GEOMETRIC_RMSE_MODEL', 10),
      # ee.Filter.Or(
      #     ee.Filter.eq('IMAGE_QUALITY', 9),
      #     ee.Filter.eq('IMAGE_QUALITY_OLI', 9))

      ee.Filter.bounds(aoi), ee.Filter.calendarRange(startDoy, endDoy, 'day_of_year')
    )

  dateStart = datetime.datetime.strptime(startDate, format)
  dateEnd = datetime.datetime.strptime(endDate, format)

  if dateEnd <= date_2012 :
    # L5
    col = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR').filter(colFilter).map(prepEtm)
  elif (dateEnd <= date_2013) & (dateStart >= date_2012) :
    # L7
    col = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR').filter(colFilter).map(prepEtm)
  elif dateStart > date_2013 :
    # L8
    col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filter(colFilter).map(prepOli)

  # # Get Landsat surface reflectance collections for OLI, ETM+ and TM sensors.
  # oliCol = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  # etmCol = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
  # tmCol = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')

  # # Filter collections and prepare them for merging.
  # oliCol = oliCol.filter(colFilter).map(prepOli)
  # etmCol = etmCol.filter(colFilter).map(prepEtm)
  # tmCol = tmCol.filter(colFilter).map(prepEtm)

  # Merge the collections.
  # col = oliCol.merge(etmCol).merge(tmCol)
  # col = oliCol
  # col = tmCol
  # print('##### - Imagery dataset size: ' + str(col.size().getInfo()))

  # Filter the collection
  filtered = col.filterDate(startDate, endDate).filterBounds(aoi.geometry().bounds())

  return filtered

def ref(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image:
    imageCollection = getHarmonizedCollection(aoi, startDate, endDate)
    size = str(imageCollection.size().getInfo())
    print('##### - Harmonization | Imagery dataset size : ' + size)
    image = imageCollection.reduce('mean').clip(aoi)
    calculated = calculateExtraBands.calculateExtraBands(image, NIR, Red, SWIR)
    return { "image": calculated, "collectionSize": size }