import csv
# import pandas as pd

# Open and read a CSV file

file = open('habitable exoplanets list.txt', 'r')
content = file.read()


with open('PSCompPars_2024.10.05_07.42.51.csv', mode='r') as f:
    csv_reader = csv.reader(f)
    # Iterate over rows in the CSV
    for row in csv_reader:
        if row[0] in content:
            print(row[0])
    


# df = pd.read_csv('PS_2024.10.05_06.28.35.csv')


