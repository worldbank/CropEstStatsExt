import ee

import LANDSAT_LC08_C02_T1_L2
import LANDSAT_LC08_C01_T1_SR
import LANDSAT_LE07_C02_T1_L2
import LANDSAT_LE07_C01_T1_SR
import LANDSAT_LT05_C02_T1_L2
import LANDSAT_LT05_C01_T1_SR
import harmonization

def get(
    # aoi: ee.FeatureCollection,
    aoi, # ee.FeatureCollection or ee.Feature
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image :
    # return LANDSAT_LC08_C02_T1_L2.ref(aoi, startDate, endDate)
    # return LANDSAT_LC08_C01_T1_SR.ref(aoi, startDate, endDate)
    # return LANDSAT_LE07_C01_T1_SR.ref(aoi, startDate, endDate)
    # return LANDSAT_LT05_C01_T1_SR.ref(aoi, startDate, endDate)
    # return LANDSAT_LT05_C02_T1_L2.ref(aoi, startDate, endDate)
    
    return harmonization.ref(aoi, startDate, endDate)
