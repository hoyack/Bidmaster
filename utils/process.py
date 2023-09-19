import os
import requests
import csv
import json
import argparse
from dotenv import load_dotenv

# Argument parsing setup
parser = argparse.ArgumentParser(description="Process API data and save to CSV.")
parser.add_argument('-o', '--output', help="Name of the output CSV file.", default="output.csv")
args = parser.parse_args()

# Define the default output directory and filename
output_directory = os.path.join(os.path.dirname(__file__), '..', 'sources')
output_path = os.path.join(output_directory, args.output)

load_dotenv()

# Load the endpoint from .env file
ENDPOINT = os.getenv("ENDPOINT")

# Set static parameters
id_param = 741
action_param = 7

# Build the complete endpoint with parameters
complete_endpoint = f"{ENDPOINT}?id={id_param}&action={action_param}"

# Make the API call
response = requests.get(complete_endpoint)

if response.status_code == 200:
    response_data = response.json()

    if response_data and isinstance(response_data, list):

        # Load structure.json from the relative path
        structure_path = os.path.join(os.path.dirname(__file__), '..', 'maps', 'structure.json')
        with open(structure_path, "r") as f:
            structure = json.load(f)

        headers = structure[0].keys()  # Headers based on the structure

        # Create a CSV file at the specified output path
        with open(output_path, "w", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            
            # Loop through the API response data
            for item in response_data:
                if "data" in item:
                    row_data = {}
                    for key in headers:
                        # Handle special cases for the 'Main Company Phone' field
                        if key == "Main Company Phone" and isinstance(item["data"].get(key, []), list) and len(item["data"].get(key, [])) > 0:
                            row_data[key] = item["data"].get(key, [])[0]
                        else:
                            row_data[key] = item["data"].get(key, None)
                    writer.writerow(row_data)
            print(f"CSV file generated successfully at {output_path}.")
    else:
        print("Response data is not in the expected format.")
else:
    print(f"Failed to fetch data from {complete_endpoint}. Status code: {response.status_code}")
