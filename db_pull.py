import pandas as pd
import requests
import json


BASE_URL = "http://vocadb.net/api/"

### Helper Methods ###

# Load a .json file
def load_data(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

# Retrieve the data from an endpoint
def get_single(endpoint, params=None):

    url = BASE_URL + endpoint
    r = requests.get(url, params=params, timeout=5)
    data = r.json()
    return data

# Retrieve the data from an endpoint
def get_data(endpoint, params, max_results=100, all=False):
    data = []
    url = BASE_URL + endpoint
    offset = 0
    params["maxResults"] = max_results
    params["getTotalCount"] = "true"

    if all:  
        if params:
            params["start"] = offset
        else:
            params = {
                "maxResults" : max_results,
                "getTotalCount" : "true",
                "start" : offset
            }
        while True:
            params["start"] = offset
            resp = requests.get(url, params=params, timeout=10)
            payload = resp.json()

            batch = payload.get("items", [])
            #total = payload.get("totalCount")
            data.extend(batch)

            if not batch:
                break
            # if total is not None and len(data) >= total:
            #     break

            offset += len(batch)
    else:
        data = get_single(endpoint, params)

    print(len(data))
    return data

# Pull all songlist fields
def extract_songlist_fields(sl_data):
    sl_ids = []
    for sl in sl_data:
        sl_ids.append(sl["id"])

    return sl_ids

# Write the data to a .json file
def write_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Get ALL songlists
def get_all_songlists():
    params = {
        "featuredCategory": "Concerts",
    }
    data = get_data("songLists/featured", params=params, max_results=100, all=True)
    return data

# Get data on ALL setlists and all their songs (NOT UNIQUE)
def get_songlist_songs(clean=False):
    data = get_all_songlists()
    ex_data = extract_songlist_fields(data)
    sl_song_data = []
    for sl_id in ex_data:
        params = {
            "listId" : sl_id,
            "fields" : "Names"
        }
        sl_data = get_data(f"songLists/{sl_id}/songs", params=params, max_results=100, all=True)

        if clean == True and len(sl_data) > 50:
            continue
        else:
            sl_song_data.extend(sl_data)

    if clean == True:
        write_data(sl_song_data, "CLEAN_sl_song_data.json")
    else:
        write_data(sl_song_data,"sl_song_data.json")

# Build list of unique songs and compute their average order in a setlist
def build_songs_dataset(clean=False):
    sl_song_data = load_data("sl_song_data.json")

    if clean == True:
        sl_song_data = load_data("CLEAN_sl_song_data.json")

    unique_sdata = {}
    sdata_list = []
    for s in sl_song_data:
        order = s["order"]

        if(clean == True):
            if order > 50:
                continue

        id = s["song"]["id"]

        if id not in unique_sdata:
            s["count"] = 1
            s["avg_order"] = order

            unique_sdata[id] = s
            sdata_list.append(s)
        else:
            song = unique_sdata[id]
            song["count"] += 1

            c = song["count"]
            song["avg_order"] += (order - song["avg_order"])/c

#    sdata_list.sort(key = lambda d: d["count"])

    if clean == True:
        write_data(sdata_list, "CLEAN_unique_setlist_songs.json")
    else:
        write_data(sdata_list, "unique_setlist_songs.json") 

# Create dataset that will be used for the rest of the project
def build_simplified_dataset(clean=False):
    full_data_list = load_data("unique_setlist_songs.json")
   
    if clean == True:
        full_data_list = load_data("CLEAN_unique_setlist_songs.json")

    simple_data_list = []
    for song_data in full_data_list:
        song = song_data["song"]
        

        eng_idx = next(
            (idx for idx,dict in enumerate(song["names"]) if dict["language"] == "English"),
            None
        )

        if eng_idx:
            et = song["names"][eng_idx]["value"]
        else:

            eng_idx = next(
                (idx for idx,dict in enumerate(song["names"]) if dict["language"] == "Romaji"),
                None
            )
            if eng_idx:
                et = song["names"][eng_idx]["value"]
            else:
                et = "None"


        data = {
            "title" : song["defaultName"],
            "english_title" : et,
            "artist": song["artistString"],
            "length_seconds" : song["lengthSeconds"],
            "setlist_frequency": song_data["count"],
            "avg_setlist_order" : song_data["avg_order"],
            "song_type" : song["songType"],
            "pv_services" : song["pvServices"],
            "times_favorited" : song["favoritedTimes"],
            "rating" : song["ratingScore"],
        }
        simple_data_list.append(data)
    return simple_data_list


# Main
if __name__ == "__main__":
    # Retrieve all basic data (this is necessary for the cleaned data steps)
    #get_songlist_songs()
    #build_songs_dataset()
    #data = load_data("unique_setlist_songs.json")
    #print(len(data)) # Test print
    #data = build_simplified_dataset()
    #write_data(data, "vocaloid_setlist_songs.json")

    # Retrieve cleaned preprocessor data (DO NOT include any songs where order > 50)
    get_songlist_songs(clean=True)
    build_songs_dataset(clean=True)
    data = load_data("CLEAN_unique_setlist_songs.json")
    data = build_simplified_dataset(clean=True)
    write_data(data, "CLEAN_vocaloid_setlist_songs.json")



