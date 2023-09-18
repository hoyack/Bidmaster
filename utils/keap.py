import argparse
import csv
import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def send_request(id_value, action_values):
    endpoint = os.getenv("ENDPOINT")
    if not endpoint:
        print("Error: ENDPOINT not found in .env file.")
        return
    params = {
        "id": id_value,
        "action": action_values
    }
    response = requests.get(endpoint, params=params)
    return response

def process_csv(csv_path, wait_time, action_values):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        if "Id" not in reader.fieldnames:
            print("Error: 'Id' column not found in the CSV.")
            return

        for row in reader:
            id_value = row["Id"]
            response = send_request(id_value, action_values)
            if response:
                print(f"Sent request for ID {id_value}. Response status: {response.status_code}")
            time.sleep(wait_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send GET requests for each ID in a CSV file.")
    parser.add_argument('-csv', required=True, help='Path to the CSV file within the sources directory.')
    parser.add_argument('--wait', default=5, type=int, help='Wait time in seconds between requests. Default is 5 seconds.')
    parser.add_argument('--action', required=True, help='Action values separated by comma. For example: 1,2,3')
    
    args = parser.parse_args()
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'sources', args.csv)
    process_csv(csv_path, args.wait, args.action)