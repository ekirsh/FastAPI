
import requests, json
from time import sleep
from collections import defaultdict
from functools import partial
from typing import List, Dict
import sys
import re
import firebase_admin
import os
import datetime
from firebase_admin import credentials, firestore
from pymongo import MongoClient

password = os.environ.get('MONGO_PASSWORD')
uri = f'mongodb+srv://ezkirsh:{password}@genius.riaazno.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(uri)

#cred = credentials.Certificate('music-genius-383921-firebase-adminsdk-5pb85-70bdafbc7b.json')
#firebase_admin.initialize_app(cred)

#db = firestore.client()
db = client['music-genius']
artists_collection = db['artists']

# constant values.
BASE_URL = "https://api.genius.com"
CLIENT_ACCESS_TOKEN = "uFcrDVB7L-4RswcUSzhO_yz6bldyQZ2dBbJQZCceXjrio6JJ4nBR5RVXuWA9G2c-"
ARTIST_NAME = sys.argv[1]

def get_artist_info(artist_id):
    base_url = "https://api.genius.com/artists/"
    headers = {'Authorization': 'Bearer uFcrDVB7L-4RswcUSzhO_yz6bldyQZ2dBbJQZCceXjrio6JJ4nBR5RVXuWA9G2c-'}
    url = base_url + str(artist_id) + "?text_format=plain"
    response = requests.get(url, headers=headers)
    data = response.json()
    data = data['response']['artist']
    artist_info = {'description': data['description']['plain'], 'instagram': data['instagram_name'],
                   'twitter': data['twitter_name'], 'image': data['image_url']}
    return artist_info

def format_string(string):
    # convert string to lowercase
    string = string.lower()
    
    # remove special characters from string
    string = string.replace(' ', '').replace('-', '')
    string = string.lstrip()
    string = string.replace('\u200b', '')
    string = re.sub(r'^\s*', '', string)
    
    return string
    

def rank_collaborators(songs, artist_name):

    collaborators = {}

    for i, song in enumerate(songs):

        for collaborator in song['writer_artists'] + song['producer_artists']:

            id_num = collaborator['id']

            collaborator = collaborator['name']

            print(collaborator)

            print(artist_name)

            if collaborator != artist_name:

                if collaborator not in collaborators:

                    collaborators[collaborator] = {'count': 1, 'hot_count': int(song['hot']), 'id': str(id_num), 'views': song['views'], 'song_list': [{'title': song['title'], 'id': song['id'], 'song_art': song['song_art'], 'rank': song['rank']}]}

                    score = (len(songs) - i) / len(songs)

                    collaborators[collaborator]['relevance'] = collaborators.get(collaborator, {}).get('relevance', 0) + score

                    collaborators[collaborator]['relevance_score'] = collaborators[collaborator]['relevance'] / collaborators[collaborator]['count']

                else:

                    new_song = {'title': song['title'], 'id': song['id'], 'song_art': song['song_art'], 'rank': song['rank']}

                    if new_song not in collaborators[collaborator]['song_list']:

                        collaborators[collaborator]['hot_count'] += int(song['hot'])

                        collaborators[collaborator]['views'] += song['views']

                        collaborators[collaborator]['song_list'].append(new_song)

                        collaborators[collaborator]['count'] += 1

                        collaborators[collaborator]['avg_views'] = collaborators[collaborator]['views'] /  collaborators[collaborator]['count']

                        score = (len(songs) - i) / len(songs)

                        collaborators[collaborator]['relevance'] = collaborators.get(collaborator, {}).get('relevance', 0) + score

                        collaborators[collaborator]['relevance_score'] = collaborators[collaborator]['relevance'] / collaborators[collaborator]['count']

    sorted_collaborators = sorted(collaborators.items(),

    key=lambda x: (-x[1]['relevance_score']*0.2 if x[1]['count']==1 else -x[1]['relevance_score']*0.3

    + -x[1]['count']*0.9 if x[1]['count']==1 else -x[1]['count']*0.7

    + -x[1]['views']*0.2,

    -x[1]['hot_count']))



    return sorted_collaborators




#def rank_collaborators(songs_data):
    # Create a dictionary to store collaborators and their stats
    #collaborators = defaultdict(lambda: {'count': 0, 'last_release': None, 'views': 0, 'hot_count': 0})
    
    #for song in songs_data:
        # Update collaborators' count
        #print(song)
        #for collaborator in song['writer_artists'] + song['producer_artists']:
            #collaborators[collaborator]['count'] += 1
            #collaborators[collaborator]['views'] += song['views']
            #if song['hot']:
                #collaborators[collaborator]['hot_count'] += 1
            #if collaborators[collaborator]['last_release'] is None or song['release_date'] > collaborators[collaborator]['last_release']:
                #collaborators[collaborator]['last_release'] = song['release_date']
    
    # Sort collaborators based on the stats
    #sorted_collaborators = sorted(collaborators.items(), key=lambda x: (x[1]['count'], x[1]['last_release'], x[1]['views'] / x[1]['count'], x[1]['hot_count']), reverse=True)
    
    #return sorted_collaborators


# send request and get response in json format.
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
        return response.json()
    except:
        sleep(2)
        _get(path=path, params=params, headers=headers)


def get_artist_songs(artist_id):
    # initialize variables & a list.
    current_page = 1
    next_page = True
    songs = []

    # main loop
    while next_page:

        if current_page > 2:
            break

        path = "artists/{}/songs/?sort=popularity".format(artist_id)
        params = {'page': current_page}
        data = _get(path=path, params=params)
        #print(data)
        page_songs = data['response']['songs']

        if page_songs:
            # add all the songs of current page,
            # and increment current_page value for next loop.
            songs += page_songs
            current_page += 1
        else:
            # if page_songs is empty, quit.
            next_page = False

    # get all the song ids, excluding not-primary-artist songs.
    songs = [song["id"] for song in songs
             if song["primary_artist"]["id"] == artist_id]

    print(songs)
    return songs

def get_collaborator_songs(artist_id):
    # initialize variables & a list.
    current_page = 1
    next_page = True
    songs = []

    # main loop
    while next_page:

        path = "artists/{}/songs/?sort=popularity".format(artist_id)
        params = {'page': current_page}
        data = _get(path=path, params=params)
        #print(data)
        page_songs = data['response']['songs']

        if page_songs:
            # add all the songs of current page,
            # and increment current_page value for next loop.
            songs += page_songs
            current_page += 1
        else:
            # if page_songs is empty, quit.
            next_page = False

    # get all the song ids, excluding not-primary-artist songs.
    songs = [song["id"] for song in songs]
             

    print(songs)
    return songs

def get_song_information(song_ids):
    # initialize a dictionary.
    song_list = []
    i = 0
    # main loop
    for i, song_id in enumerate(song_ids):
        if i > 80:
            break
        print("id:" + str(song_id) + " start. ->")

        path = "songs/{}".format(song_id)
        data1 = _get(path=path)
        if data1 is None:
            continue
        data = data1['response']['song']


        song_list.append(
            {
                "title": data["title"],
                "album": data["album"]["name"] if data["album"] else "single",
                "release_date": data["release_date"] if data["release_date"] else "unidentified",
                "primary_artist": data["primary_artist"],
                "featured_artists":
                    [{'name': feat["name"], 'id': feat['id']} if data["featured_artists"] else "" for feat in data["featured_artists"]],
                "producer_artists":
                    [{'name': feat["name"], 'id': feat['id']} if data["producer_artists"] else "" for feat in data["producer_artists"]],
                "writer_artists":
                    [{'name': feat["name"], 'id': feat['id']} if data["writer_artists"] else "" for feat in data["writer_artists"]],
                "genius_track_id": song_id,
                "genius_album_id": data["album"]["id"] if data["album"] else "none",
                "song_art": data["song_art_image_thumbnail_url"],
                "hot": data["stats"]["hot"],
                "views": data["stats"].get("pageviews", 0),
                "id": str(song_id),
                "rank": i + 1
            }
        )

        i += 1
        print("-> id:" + str(song_id) + " is finished. \n")
    return song_list

# # # 

print("searching " + ARTIST_NAME + "'s artist id. \n")

# find artist id from given data.
find_id = _get("search", {'q': ARTIST_NAME})
artist_name = ""
artist_id = 0
for hit in find_id["response"]["hits"]:
    original_name = hit["result"]["primary_artist"]["name"]
    formatted_name = format_string(original_name)
    print(formatted_name)
    print(format_string(ARTIST_NAME))
    if formatted_name == format_string(ARTIST_NAME):
        artist_id = hit["result"]["primary_artist"]["id"]
        artist_name = original_name
        print(artist_id)
        break

print("-> " + ARTIST_NAME + "'s id is " + str(artist_id) + "\n")

artists_collection.insert_one({"_id": artist_id, "name": artist_name, "collaborators": []})
current_artist = artists_collection.find_one({"_id": artist_id})


print("getting song ids. \n")

# get all song ids and make a list.
song_ids = get_artist_songs(artist_id)

#with open("./" + ARTIST_NAME + " Genius Song IDs.text", "w") as f:
    #write(song_ids)

print(song_ids)
print("\n-> got all the song ids. take a break for a while \n")

sleep(2)

print("getting meta data of each song. \n")

# finally, make a full list of songs with meta data.
full_list_of_songs = get_song_information(song_ids)

print("-> Finished! Dump the data into json data. \n")

#with open("./" + ARTIST_NAME + " Songs.json", "w") as f:
    #json.dump(full_list_of_songs, g)

x = rank_collaborators(full_list_of_songs, artist_name)
#print(x)

y = 0
ids = [data[1]['id'] for data in x]
names = [data[0] for data in x]

for card in x:
    if y > 30:
        break
    info_a = get_artist_info(card[1]['id'])
    current_artist['collaborators'].append({
            'info': info_a,
            'name': names[y],
            'rank': y + 1,
            '_id': card[1]['id'],
            'count': card[1]['count'],
            'hot_count': card[1]['hot_count'],
            'views': card[1]['views'],
            'song_list': card[1]['song_list'],
            'songs': [],
            'collaborators': [],
            'relevance': card[1]['relevance'],
            'relevance_score': card[1]['relevance_score']
        })
    artists_collection.replace_one({"_id": artist_id}, current_artist)
    #print(ids[y])
    songs = get_collaborator_songs(ids[y])
    #print(songs)
    sleep(2)
    song_info = get_song_information(songs)
    #print(song_info)
    for song in song_info[:15]:
        current_artist["collaborators"][-1]["songs"].append(song)
    z = rank_collaborators(song_info, names[y])
    for i, (collaborator, data) in enumerate(z):
        if i > 20:
            break
        current_artist['collaborators'][-1]['collaborators'].append({
            'name': collaborator,
            'rank': i + 1,
            '_id': data['id'],
            'count': data['count'],
            'hot_count': data['hot_count'],
            'views': data['views'],
            'song_list': data['song_list'],
            'relevance': data['relevance'],
            'relevance_score': data['relevance_score']
        })
        print(f'{names[y]} {collaborator}')
    artists_collection.replace_one({"_id": artist_id}, current_artist)
    y += 1

print("-> Mission complete! Check it out!")
