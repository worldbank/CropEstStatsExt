import sys
sys.path.append('./utils/')

from datetime import datetime
import ee

import sampleRegions

def trainClassifier(
    referenceImage: ee.Image,
    bandNames: list,
    trainingDataset: ee.FeatureCollection,
    property: str = "class"
) -> ee.Classifier:

    training = sampleRegions.sampleRegions(referenceImage, bandNames, trainingDataset)
    classifier = ee.Classifier.smileRandomForest(100)
    trained = classifier.train(training, property, bandNames)
    
    return trained