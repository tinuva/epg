#!/usr/bin/env python3
import json
from pathlib import Path
 
def generate_config():
    # Read the metadata file
    metadata_path = Path(__file__).parents[1]/"epg_grabber"/"sites"/"channels_metadata"/"dstv_com.json"
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return
    
    # Extract all channel IDs
    channel_ids = [channel["id"] for channel in metadata["channels"]]
    
    # Create the config structure
    config = {
        "days": 3,
        "workers": 1,
        "configs": [
            {
                "site": "dstv_com",
                "channels": channel_ids
            }
        ]
    }
    
    # Save the config
    output_file = Path(__file__).parents[1]/"dstv_com.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
 
if __name__ == "__main__":
    generate_config()