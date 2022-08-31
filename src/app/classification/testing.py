import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')
import run


#years = ['2015', '2017', '2019', '2021']
# years = ['1985', '1990', '1995', '2000', '2005', '2010', '2015', '2017', '2019', '2021']
# years = ['1995']
years = ["2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
# years = ["2013","2014","2015","2016","2017","2018","2019","2020","2021"]
# years = ["2021"]

## Bands used for both classification and values retrieval. Make sure it matches the imagery provided
# bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
bands = ['Blue_mean', 'Green_mean', 'Red_mean', 'NIR_mean', 'SWIR1_mean', 'SWIR2_mean', 'NDVI', 'NDWI', 'SAVI']

## AoI : path (rel. to main.py) to the geojson file containing the polygon geometries on which we want to run the extraction
aoi = './testing/NER_tillaberi_niamey_dosso/input/intersection_say.geojson'

## subNameField : foreign identifier for aoi geometries (used to aggregate the resulting chunked aoi geometry parts)
subNameField = 'adm_03'

## Extent : path (rel. to main.py) to the geojson file containing the extent polygon geometry
extent = './testing/NER_tillaberi_niamey_dosso/input/extent.geojson'



## Training data : path to the geojson file containing the training points (must be located within the provided extent)
### Should be points,
### with a "class" attribute of type integer,
### the value used for classify croplands is the following : 0
trainingDataset = './data/input/NER/NER_Training_Test_2.geojson'





############# OPTIONAL Parameters

# OPTIONAL outputMode : int (1 - values, 2 - values + images, 3 - values + images + vectors)
### Default :
outputMode = 1

# outputMode = 3

## OPTIONAL classificationImage_startDate : month + day, string formatted as MM-DD
### Default :
classificationImage_startDate = '01-01'

## OPTIONAL classificationImage_endDate : month + day, string formatted as MM-DD
### Default :
classificationImage_endDate = '12-31'

## OPTIONAL nameProp : unique identifier for aoi geometries
### Default :
nameProp = 'uid'

## OPTIONAL referenceImage_startDate (to train the classifier on)
### Default :
referenceImage_startDate = '2020-01-01'

## OPTIONAL referenceImage_endDate (to train the classifier on)
### Default :
referenceImage_endDate = '2020-12-31'


for x in years:
    ## Define the dates range for selecting images (to be classified with our classifier previously trained)
    ## classificationImage_year : year, string formatted as YYYY
    classificationImage_year = x

    ## outputFolder : location path for the generated values file outputs
    outputFolder = './testing/NER_tillaberi_niamey_dosso/output/TESTING_NER_Say_18' + '_' + classificationImage_year +'/'
    ## OPTIONAL outputFolder_Images : location path for the generated images file outputs
    ### Default :
    outputFolder_images = outputFolder + 'images/'

    ## OPTIONAL outputFolder_Vectors : location path for the generated vectors file outputs
    ### Default :
    outputFolder_vectors = outputFolder + 'vectors/'
    run.run(
        bands,
        aoi,
        subNameField,
        extent,
        outputFolder,
        trainingDataset,
        classificationImage_year,
        outputMode,
        classificationImage_startDate,
        classificationImage_endDate,
        nameProp,
        referenceImage_startDate,
        referenceImage_endDate,
        outputFolder_images,
        outputFolder_vectors
    )
