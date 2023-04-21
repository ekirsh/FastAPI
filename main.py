from fastapi import FastAPI
from pydantic import BaseModel
import requests, json
from bs4 import BeautifulSoup
from lxml import etree
from pymongo import MongoClient
import subprocess
import threading

client = MongoClient('mongodb://mongo:99dOOEhHeU3cbLwHjYzQ@containers-us-west-79.railway.app:7240')
db = client['music-genius']
artists_collection = db['artists']
app = FastAPI()
BASE_URL = "https://api.genius.com"
CLIENT_ACCESS_TOKEN = "uFcrDVB7L-4RswcUSzhO_yz6bldyQZ2dBbJQZCceXjrio6JJ4nBR5RVXuWA9G2c-"

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
        print('e')
        _get(path, params, headers)

    return response.json()


def run_scraper(artist):
    cmd = ['python3', 'GeniusMetaData.py', artist]
    subprocess.run(cmd)


def scrape_artist(artist_name):
    find_id = _get("search", {'q': artist_name})
    artist_name = ""
    artist_id = ""
    for hit in find_id["response"]["hits"]:
        original_name = hit["result"]["primary_artist"]["name"]
        formatted_name = format_string(original_name)
        print(formatted_name)
        print(format_string(artist_name))
        if formatted_name == format_string(artist_name):
            artist_id = hit["result"]["primary_artist"]["id"]
            artist_name = original_name
            print(artist_id)
            break
    scraper_thread = threading.Thread(target=run_scraper, args=(artist_name,))
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

@app.get("/artist-data/{artist_id}")
async def demo_get_artist_data(artist_id: str):
    artist = artists_collection.find_one({"_id": artist_id})
    if artist:
        cc = artist["collaborators"]
        if cc != []:
            return cc
        else:
            return {"message": "Artist still loading..."}
    else:
        return {"message": "Artist still loading..."}
