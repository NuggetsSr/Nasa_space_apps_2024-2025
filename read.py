import json

# Open the JSON file
with open('big_ahh_json.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)

# Print the data
print(data)