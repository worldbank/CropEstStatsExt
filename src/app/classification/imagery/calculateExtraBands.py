import ee

def calculateExtraBands(
    image: ee.Image,
    NIR: str, # band name
    Red: str, # band name
    SWIR: str, # band name
) -> ee.Image:
  # NDVI (Normalized Difference Vegetation Index) calc. source : https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
  NDVI = image.expression('(NIR - Red) / (NIR + Red)', {
    'NIR': image.select(NIR),
    'Red': image.select(Red)
  })
  # NDWI (Normalized Difference Water Index) calc. source : https://en.wikipedia.org/wiki/Normalized_difference_water_index
  NDWI = image.expression('(NIR - SWIR) / (NIR + SWIR)', {
    'NIR': image.select(NIR),
    'SWIR': image.select(SWIR)
  })
  # SAVI (Soil Adjusted Vegetation Index) calc. source : https://giscrack.com/list-of-spectral-indices-for-sentinel-and-landsat/
  SAVI = image.expression('(NIR - Red) / (NIR + Red + 0.428) * (1.428)', {
    'NIR': image.select(NIR),
    'Red': image.select(Red)
  })
  return image.addBands(NDVI.rename('NDVI')).addBands(NDWI.rename('NDWI')).addBands(SAVI.rename('SAVI'))