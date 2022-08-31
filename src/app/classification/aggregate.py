import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

import pandas as pd
import json
# import numpy as np
# https://github.com/jsvine/weightedcalcs
import weightedcalcs as wc
import csv
import fromJsonToCsv

year = "2020"
path = './testing/NER_tillaberi_niamey_dosso/output/TESTING_NER_Say_14_' + year + '/VALUES.csv'
joinAttribute = "subregion"
outputFolder = './testing/NER_tillaberi_niamey_dosso/aggregation_say_chirps_14/'

df = pd.read_csv(path)
unique = pd.unique(df[joinAttribute])

values = []

for x in unique:
    # filtered = df[(df[joinAttribute] == x) & df['area_sqm_crops'] != 0]
    filtered = df[(df[joinAttribute] == x)]
    length = len(filtered)
    if length > 0:
        records = filtered.to_dict('records')
        refRow = records[0]
        props = {
            'period': refRow['period'],
            'subregion': refRow['subregion'],
            'obs_classification': refRow['obs'],
            'obs_chirps': refRow['obs_chirps']
        }
        props['area_sqm_crops'] = int(filtered['area_sqm_crops'].sum())
        props['area_sqm_non_crops'] = int(filtered['area_sqm_non_crops'].sum())

        # CROPS
        filteredMin = filtered[filtered['crops_ndvi_min'] > 0]
        if filteredMin.empty:
            min = -999
        else:
            min = float(filteredMin['crops_ndvi_min'].min())
        props['crops_ndvi_min'] = min
        props['crops_ndvi_mean'] = float(wc.Calculator('area_sqm_crops').mean(filtered, 'crops_ndvi_mean'))
        props['crops_ndvi_median'] = float(wc.Calculator('area_sqm_crops').median(filtered, 'crops_ndvi_median'))
        props['crops_ndvi_max'] = float(filtered['crops_ndvi_max'].max())
        props['crops_ndvi_stddev'] = float(wc.Calculator('area_sqm_crops').std(filtered, 'crops_ndvi_stddev'))

        filteredMinChirps = filtered[filtered['crops_chirps_min'] > 0]
        if filteredMinChirps.empty:
            minChirps = -999
        else:
            minChirps = float(filteredMinChirps['crops_chirps_min'].min())
        props['crops_chirps_min'] = minChirps
        props['crops_chirps_mean'] = float(wc.Calculator('area_sqm_crops').mean(filtered, 'crops_chirps_mean'))
        props['crops_chirps_median'] = float(wc.Calculator('area_sqm_crops').median(filtered, 'crops_chirps_median'))
        props['crops_chirps_max'] = float(filtered['crops_chirps_max'].max())
        props['crops_chirps_stddev'] = float(wc.Calculator('area_sqm_crops').std(filtered, 'crops_chirps_stddev'))

        # NON-CROPS
        filteredMin = filtered[filtered['non_crops_ndvi_min'] > 0]
        if filteredMin.empty:
            min = -999
        else:
            min = float(filteredMin['non_crops_ndvi_min'].min())
        props['non_crops_ndvi_min'] = min
        props['non_crops_ndvi_mean'] = float(wc.Calculator('area_sqm_non_crops').mean(filtered, 'non_crops_ndvi_mean'))
        props['non_crops_ndvi_median'] = float(wc.Calculator('area_sqm_non_crops').median(filtered, 'non_crops_ndvi_median'))
        props['non_crops_ndvi_max'] = float(filtered['non_crops_ndvi_max'].max())
        props['non_crops_ndvi_stddev'] = float(wc.Calculator('area_sqm_non_crops').std(filtered, 'non_crops_ndvi_stddev'))

        filteredMinChirps = filtered[filtered['non_crops_chirps_min'] > 0]
        if filteredMinChirps.empty:
            minChirps = -999
        else:
            minChirps = float(filteredMinChirps['crops_chirps_min'].min())
        props['non_crops_chirps_min'] = minChirps
        props['non_crops_chirps_mean'] = float(wc.Calculator('area_sqm_non_crops').mean(filtered, 'non_crops_chirps_mean'))
        props['non_crops_chirps_median'] = float(wc.Calculator('area_sqm_non_crops').median(filtered, 'non_crops_chirps_median'))
        props['non_crops_chirps_max'] = float(filtered['non_crops_chirps_max'].max())
        props['non_crops_chirps_stddev'] = float(wc.Calculator('area_sqm_non_crops').std(filtered, 'non_crops_chirps_stddev'))

        values.append(props)

with open(outputFolder + 'aggregate_' + year + '.json', 'w') as all_valuesFile:
    json.dump(values, all_valuesFile)
    all_valuesFile.close()

fromJsonToCsv.fromJsonToCsv(outputFolder + 'aggregate_' + year + '.json', outputFolder + 'aggregate_' + year + '.csv')