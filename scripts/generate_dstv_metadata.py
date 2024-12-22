#!/usr/bin/env python3
import requests
import json
import time
from pathlib import Path
 
CHANNELS_URL = "https://www.dstv.com/umbraco/api/TvGuide/GetChannels"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.dstv.com/en-za/tv-guide",
    "Origin": "https://www.dstv.com",
    "Cache-Control": "no-cache"
}
 
def get_channels():
    try:
        response = requests.get(
            CHANNELS_URL,
            params={
                "country": "zaf",
                "unit": "dstv"
                "cachebuster": time.time()
            },
            headers=DEFAULT_HEADERS
        )
        response.raise_for_status()
        return response.json()["Channels"]
    except Exception as e:
        print(f"Error fetching channels: {e}")
        return []
 
def generate_metadata():
    channels_data = get_channels()
    
    channels = []
    for channel in channels_data:
        channel_obj = {
            "id": str(channel["Number"]),  # Keep using channel number as ID
            #"@id": str(channel["Number"]),  # Keep using channel number as ID
            "display_name": {
                "@lang": "en",
                "#text": channel["Name"]
            },
            "icon": {
                "@src": channel.get("Logo", "")
            },
            #"xml_id": channel.get("Tag", "")  # Store the Tag for XML output
            "xml_id": channel.get("Tag", str(channel["Number"]))  # Store the Tag for XML output
        }
        channels.append(channel_obj)
    
    metadata = {"channels": channels}
    output_dir = Path(__file__).parents[1]/"epg_grabber"/"sites"/"channels_metadata"
    output_file = output_dir/"dstv_com.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
 
if __name__ == "__main__":
    generate_metadata()
