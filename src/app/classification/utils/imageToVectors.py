import ee

def imageToVectors(
    image: ee.Image,
    reducingFeature: ee.Feature,
    scale: int = 30,
) -> ee.FeatureCollection:
  vectors = image.reduceToVectors(
    None,
    # ee.FeatureCollection(reducingFeature),
    reducingFeature.geometry(),
    scale,
    'polygon',
    False,
    'label',
    image.projection(),
    None,
    True
  )
  return vectors
