import ee

import calculateExtraBands

dataset = "LANDSAT/LE07/C02/T1_L2"
NIR = "SR_B5_mean"
Red = "SR_B4_mean"
SWIR = "SR_B6_mean"

def provideDataset(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.ImageCollection:
    imageCollection = ee.ImageCollection(dataset).filterDate(startDate, endDate).filterBounds(aoi.geometry().bounds()).map(bandsScaleFactor)
    return imageCollection

def bandsScaleFactor(
    image: ee.Image
) -> ee.Image:
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B6').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

def ref(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image:
    imageCollection = provideDataset(aoi, startDate, endDate)
    size = str(imageCollection.size().getInfo())
    print('##### - LE07_C02_T1_L2 | Imagery dataset size : ' + size)
    image = imageCollection.reduce('mean').clip(aoi)
    calculated = calculateExtraBands.calculateExtraBands(image, NIR, Red, SWIR)
    return { "image": calculated, "collectionSize": size }