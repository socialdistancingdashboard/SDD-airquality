import csv

def mappingLankreisNameToKey():
    mapping = {}
    with open('0_config/schluessel_nuts_ags_kreise.csv', newline='', encoding='utf-8') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=';', quotechar='|')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                #nuts;ags;bez_nuts;schluessel_ags
                ags = row[1]
                bez_nuts = row[2]
                mapping[bez_nuts] = ags
    return mapping
