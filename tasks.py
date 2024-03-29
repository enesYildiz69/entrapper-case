import json
import os
from celeryconfig import app

@app.task
def save_startup_data(startup_data):
    directory = "companies"
    filename = f"{startup_data['company_name']}.json"
    filepath = os.path.join(directory, filename)

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Check if the file already exists
    if os.path.isfile(filepath):
        print(f"File {filename} already exists. Skipping...")
    else:
        with open(filepath, 'w') as f:
            json.dump(startup_data, f)
            print(f"File {filename} has been created.")

