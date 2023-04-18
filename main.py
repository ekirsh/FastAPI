from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from lxml import etree

app = FastAPI()

proxy = {
    'http': 'http://kOKRLEQTDsyH9mmzKyzJlQ@smartproxy.crawlbase.com:8012',
    'https': 'http://kOKRLEQTDsyH9mmzKyzJlQ@smartproxy.crawlbase.com:8012'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def scrape_artist(artist_name):
    url = f"https://genius.com/artists/{artist_name.replace(' ', '-')}"

    response = requests.get(url, proxies=proxy, headers=headers, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    song_list = soup.find_all('div', class_='mini_card-title')
    link_list = []
    for a in soup.find_all('a', class_='mini_card'):
        link_list.append(a['href'])


    print(f"Top songs by {artist_name}:")
    song_data = {}
    for i, song in enumerate(song_list):
        print(f"{i+1}. {song.text} ({link_list[i]})")
        r = requests.get(link_list[i], proxies=proxy, headers=headers)
        s = BeautifulSoup(r.content, 'html.parser')
        credits = s.find_all('div', class_="SongInfo__Credit-nekw6x-3 fognin")
        song_data[song.text] = {'collaborators': []}

        collab = []
        for c in credits:
            c_type = c.find('div').text
            if (c_type == "Written By" or c_type == "Produced By"):
                names = c.find_all('a')
                for n in names:
                    if n.text not in collab:
                        masterlist.append(n.text)
                        collab.append(n.text)

        song_data[song.text]['collaborators'] = collab
    return song_data

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
