from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from lxml import etree
import subprocess
import threading


app = FastAPI()


def run_scraper(artist):
    cmd = ['python3', 'GeniusMetaData.py', artist]
    subprocess.run(cmd)


def scrape_artist(artist_name):
    scraper_thread = threading.Thread(target=run_scraper, args=(artist_name,))
    scraper_thread.start()
    return artist_name

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
