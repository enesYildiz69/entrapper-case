import requests
import json
import os
from tasks import save_startup_data
from langchain_community.document_loaders import JSONLoader
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from uuid import uuid4
import asyncio

app = FastAPI()

load_dotenv() 
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# The URL of the GraphQL endpoint
url = 'https://ranking.glassdollar.com/graphql'

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ranking.glassdollar.com',
    'Referer': 'https://ranking.glassdollar.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
}

payload_base = {
    "operationName": "TopRankedCorporates",
    "variables": {},
    "query": "query TopRankedCorporates {\n  topRankedCorporates {\n    id\n    name\n    logo_url\n    industry\n    hq_city\n    startup_partners {\n      company_name\n      logo_url: logo\n      __typename\n    }\n    startup_friendly_badge\n    __typename\n  }\n}\n"
}
payload_enterprise = {"variables":{"id":{}},"query":"query ($id: String!) {\n  corporate(id: $id) {\n    id\n    name\n    description\n    logo_url\n    hq_city\n    hq_country\n    website_url\n    linkedin_url\n    twitter_url\n    startup_partners_count\n    startup_partners {\n      master_startup_id\n      company_name\n      logo_url: logo\n      city\n      website\n      country\n      theme_gd\n      __typename\n    }\n    startup_themes\n    startup_friendly_badge\n    __typename\n  }\n}\n"}

def fetch_data():
    print("Fetching data from the GraphQL endpoint...")
    if not os.path.exists('data.json'):
        # Making the POST request to the GraphQL endpoint
        response = requests.post(url, json=payload_base, headers=headers)

        if response.status_code == 200:
            data = response.json()
            file_path = 'data.json'
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Content saved to {file_path}")
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
    else:
        print("Data already exists, skipping the data retrieval process.")

def fetch_data_for_enterprises():
    
    print("Fetching data for each enterprise...")
    with open('data.json') as file:
        data = json.load(file)
    ids = [corp["id"] for corp in data["data"]["topRankedCorporates"]]
    for id in ids:
        payload_enterprise["variables"]["id"] = id
        response = requests.post(url, json=payload_enterprise, headers=headers)
        if response.status_code == 200:
            data = response.json()
            startup_partners = data['data']['corporate']['startup_partners']
            for startup_partner in startup_partners:
                save_startup_data.delay(startup_partner)
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")

    print("All data has been fetched and saved.")

def combine_company_data():
    print("Compiling all companies data into a single file...")
    directory_path = 'companies'
    all_companies_data = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            # Construct the full file path
            file_path = os.path.join(directory_path, filename)
            
            # Open and read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                all_companies_data.append(data)
    # Write the compiled list to a new JSON file
    with open('all_companies_data.json', 'w') as outfile:
        json.dump(all_companies_data, outfile, indent=4)
    print("All data has been compiled into a single file.")

def get_continent(country_name):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Which continent is {country_name} in? Just answer the question with one word. Choose between Africa, Antarctica, Asia, Europe, North America, Australia, and South America."}
        ],
        max_tokens=60,
        temperature=0.7
    )
    answer = response.choices[0].message.content
    return answer.strip()

def get_continent_description(continent_name):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Provide a brief description for the continent {continent_name}."}
        ],
        max_tokens=60,
        temperature=0.7
    )
    description = response.choices[0].message.content
    return description

def classify_companies_by_continent(file_path):
    print("Beginnging llm process")
    with open(file_path, 'r') as file:
        companies = json.load(file)
    
    continents_data = {}
    
    for company in companies:
        country = company['country']
        continent = get_continent(country)
        print(f"{company['company_name']} is in {continent}")
        
        if continent not in continents_data:
            description = get_continent_description(continent)
            continents_data[continent] = {
                "description": description,
                "companies": []
            }
        continents_data[continent]["companies"].append(company['company_name'])
    
    # Save the classified data into a single JSON file
    with open('companies_by_continent.json', 'w') as file:
        json.dump(continents_data, file, indent=4)

operations_status = {}

async def async_wrapper_of_your_script():
    loop = asyncio.get_event_loop()
    # Execute blocking operations in a thread pool
    await loop.run_in_executor(None, fetch_data)
    await loop.run_in_executor(None, fetch_data_for_enterprises)
    await loop.run_in_executor(None, combine_company_data)
    await loop.run_in_executor(None, classify_companies_by_continent, 'all_companies_data.json')


@app.post("/start-operation/")
async def start_operation(background_tasks: BackgroundTasks):
    operation_id = str(uuid4())
    operations_status[operation_id] = "In Progress, come back later"
    
    # Offload the operation to be executed in the background
    background_tasks.add_task(execute_operation, operation_id)
    
    return {"message": "Operation started. Check progress with the operation ID.", "operation_id": operation_id}

async def execute_operation(operation_id: str):
    try:
        # Your script's logic here, adapted to async if possible
        # For demonstration, let's assume this function wraps your script's functionalities
        await async_wrapper_of_your_script()
        operations_status[operation_id] = "Completed"
    except Exception as e:
        operations_status[operation_id] = f"Failed: {str(e)}"

@app.get("/list-operations/")
async def list_operations():
    print(operations_status)
    return operations_status
