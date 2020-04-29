import os
import csv

def importCredentialsToEnvironment(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        fileReader = csv.reader(csvfile, delimiter='=')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                #key=val
                if len(row)==2:
                    os.environ[row[0]] = row[1]
