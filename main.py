from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, json
from bs4 import BeautifulSoup
from lxml import etree
from pymongo import MongoClient
import os
import subprocess
import threading
import sys
import re

password = os.environ.get('MONGO_PASSWORD')
uri = f'mongodb+srv://ezkirsh:{password}@genius.riaazno.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(uri)
db = client['music-genius']
artists_collection = db['artists']
active_scrapers_collection = db['active-scrapers']
app = FastAPI()
BASE_URL = "https://api.genius.com"
CLIENT_ACCESS_TOKEN = "uFcrDVB7L-4RswcUSzhO_yz6bldyQZ2dBbJQZCceXjrio6JJ4nBR5RVXuWA9G2c-"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_string(string):
    # convert string to lowercase
    string = string.lower()

    # remove special characters from string
    string = string.replace(' ', '').replace('-', '')
    string = string.lstrip()
    string = string.replace('\u200b', '')
    string = re.sub(r'^\s*', '', string)

    return string

def _get(path, params=None, headers=None):

    # generate request URL
    requrl = '/'.join([BASE_URL, path])
    token = "Bearer {}".format(CLIENT_ACCESS_TOKEN)
    if headers:
        headers['Authorization'] = token
    else:
        headers = {"Authorization": token}
    try:
        response = requests.get(url=requrl, params=params, headers=headers)
        response.raise_for_status()
    except:
        sleep(2)
        print('error with your request')
        _get(path, params, headers)

    return response.json()


def run_scraper(artist, artist_id):
    cmd = ['python3', 'GeniusMetaData.py', artist]
    try:
        subprocess.run(cmd, check=True)
        print('Scanning Complete')
        active_scraper = active_scrapers_collection.find_one({"_id": artist_id})
        active_scraper["status"] = "complete"
        active_scrapers_collection.replace_one({"_id": artist_id}, active_scraper)
    except subprocess.CalledProcessError as e:
        active_scraper = active_scrapers_collection.find_one({"_id": artist_id})
        active_scraper["status"] = "error"
        active_scrapers_collection.replace_one({"_id": artist_id}, active_scraper)
        print('Scanning Error')


def scrape_artist(artist_name):
    find_id = _get("search", {'q': artist_name})
    artist_id = ""
    for hit in find_id["response"]["hits"]:
        original_name = hit["result"]["primary_artist"]["name"]
        formatted_name = format_string(original_name)
        print(formatted_name)
        print(format_string(artist_name))
        if formatted_name == format_string(artist_name):
            artist_id = hit["result"]["primary_artist"]["id"]
            print(artist_id)
            break
    filter_dict = {"_id": artist_id}
    count = active_scrapers_collection.count_documents(filter_dict)
    if count > 0:
        return artist_id
    else:
        active_scrapers_collection.insert_one({"name": artist_name, "status": "active", "_id": artist_id})
        scraper_thread = threading.Thread(target=run_scraper, args=(artist_name, artist_id))
        scraper_thread.start()
        return artist_id

class Msg(BaseModel):
    msg: str

@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}


@app.get("/path")
async def demo_get():
    return {"message": "This is /path endpoint, use a post request to transform the text to uppercase"}


@app.post("/path")
async def demo_post(inp: Msg):
    return {"message": inp.msg.upper()}


@app.get("/artists/{artist_id}")
async def demo_get_path_id(artist_id: str):
    return scrape_artist(artist_id)

@app.get("/get_active_scrapers")
async def demo_get_artist_data():
    cursor = active_scrapers_collection.find({})
    print(cursor)
    data = []
    for document in cursor:
        data.append(document)
    return data


@app.get("/artist-data/{artist_id}")
async def demo_get_artist_data(artist_id: str):
    active_scraper = active_scrapers_collection.find_one({"_id": int(artist_id)})
    print(artist_id)
    artist = artists_collection.find_one({"_id": int(artist_id)})
    print(artist)
    if artist:
        print('artist found')
        cc = artist["collaborators"]
        print(cc)
        if cc != []:
            return cc
        else:
            return {"message": "Artist still loading..."}
    else:
        return {"message": "Artist still loading..."}

