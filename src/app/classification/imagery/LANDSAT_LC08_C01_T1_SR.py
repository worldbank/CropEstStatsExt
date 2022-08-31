import ee

import calculateExtraBands

dataset = "LANDSAT/LC08/C01/T1_SR"
NIR = "NIR_mean"
Red = "Red_mean"
SWIR = "SWIR1_mean"

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

# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = renameOli(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))

def provideDataset(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.ImageCollection:
    imageCollection = ee.ImageCollection(dataset).filterDate(startDate, endDate).filterBounds(aoi.geometry().bounds()).map(prepOli)
    return imageCollection

def ref(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image:
    imageCollection = provideDataset(aoi, startDate, endDate)
    size = str(imageCollection.size().getInfo())
    print('##### - LC08_C01_T1_SR | Imagery dataset size : ' + size)
    image = imageCollection.reduce('mean').clip(aoi)
    calculated = calculateExtraBands.calculateExtraBands(image, NIR, Red, SWIR)
    return { "image": calculated, "collectionSize": size }