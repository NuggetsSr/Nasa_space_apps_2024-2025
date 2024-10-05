import csv

# Open and read a CSV file
with open('PS_2024.10.05_06.28.35.csv', mode='r') as file:
    csv_reader = csv.reader(file)
    # Iterate over rows in the CSV
    for row in csv_reader:
        print(row[0])
        print()