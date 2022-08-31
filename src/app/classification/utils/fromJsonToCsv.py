# Python program to convert
# JSON file to CSV
 
 
import json
import csv
 
def fromJsonToCsv(
    pathToJSON,
    pathToCSV
):
    # Opening JSON file and loading the data
    # into the variable data
    with open(pathToJSON) as json_file:
        data = json.load(json_file)
    
        
        # now we will open a file for writing
        data_file = open(pathToCSV, 'w', newline='')
        
        # create the csv writer object
        csv_writer = csv.writer(data_file)
        
        # Counter variable used for writing
        # headers to the CSV file
        count = 0
        
        for row in data:
            if count == 0:
        
                # Writing headers of CSV file
                header = row.keys()
                csv_writer.writerow(header)
                count += 1
        
            # Writing data of CSV file
            csv_writer.writerow(row.values())

        data_file.close()
        json_file.close()