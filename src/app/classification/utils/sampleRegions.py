import ee

def sampleRegions(
    image: ee.Image,
    bandNames: list,
    trainingDataset: ee.FeatureCollection,
    scale: int = 30,
    property: str = "class"
) -> ee.FeatureCollection:
    output_collection = image.select(bandNames).sampleRegions(trainingDataset, [property], scale, None, 1, True)
    return output_collection