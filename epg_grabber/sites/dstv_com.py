from epg_grabber.models import Programme, Channel, ChannelMetadata
from typing import List
from datetime import datetime, timedelta
import requests
from pytz import timezone
import time
from functools import lru_cache
from loguru import logger
 
ALL_CHANNELS_URL = "https://www.dstv.com/umbraco/api/TvGuide/GetChannels"
PROGRAMS_URL = "https://www.dstv.com/umbraco/api/TvGuide/GetProgrammes"
PROGRAM_DETAIL_URL = "https://www.dstv.com/umbraco/api/TvGuide/GetProgramme"
 
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    #"Accept": "application/json",
    "Accept": "*/*",
    #"Referer": "https://www.dstv.com/en-za/tv-guide",
    #"Origin": "https://www.dstv.com"
}
 
session = requests.Session()

@lru_cache(maxsize=None)
def _cached_get_request(url: str, params_str: str) -> dict:
    """
    Make a cached GET request. Cache is based on URL and stringified parameters.
    Only successful responses with channels are cached.
    
    Args:
        url: The URL to request
        params_str: JSON string of parameters for cache key
        
    Returns:
        dict: JSON response data
    """
    params = eval(params_str)  # Convert string back to dict
    response = session.get(url, params=params, headers=DEFAULT_HEADERS)
    data = response.json()
    return data

def generate() -> ChannelMetadata:
    try:
        response = session.get(
            ALL_CHANNELS_URL,
            params={
                "country": "zaf",
                "unit": "dstv"
            },
            headers=DEFAULT_HEADERS
        )
    except Exception as e:
        raise e
 
    data = response.json()
    channels = []
 
    for channel in data["Channels"]:
        channel_obj = Channel(
            id=str(channel["Number"]),
            display_name=channel["Name"],
            xml_id=channel["Tag"],
            channel_id=str(channel["Number"]),
            icon=channel["Logo"] if "Logo" in channel else ""
        )
        channels.append(channel_obj)
 
    channel_metadata = ChannelMetadata(channels=channels)
    return channel_metadata
 
def get_programs(
    channel_id: str, days: int = 1, channel_xml_id: str = None
) -> List[Programme]:
    programmes: List[Programme] = []
    channel_name = channel_xml_id if channel_xml_id else channel_id
    #channel_name = channel_xml_id  # Use the Tag (HDT) as the channel ID in output
    #channel_name = channel_id  # Use the numeric channel ID in output
 
    # DSTV uses South African timezone
    sa_tz = timezone('Africa/Johannesburg')
    date_today = datetime.now(sa_tz).date()
 
    for day in range(days):
        logger.debug(f"Fetching programs for channel {channel_id} - Day {day + 1}/{days}")
        current_date = date_today + timedelta(days=day)

        params = {
                    "d": current_date.strftime("%Y-%m-%d"),
                    "package": "Premium",
                    "country": "zaf",
                    "unit": "dstv"
                }

        max_retries = 3
        retry_count = 0
        retry_delay = 10  # seconds between retries
 
        while retry_count < max_retries:
            try:
                params_str = str(params)  # Convert params dict to string for cache key
                # Try to get from cache first
                try:
                    data = _cached_get_request(PROGRAMS_URL, params_str)
                    logger.debug(f"Programs cache info: {_cached_get_request.cache_info()}")
                except Exception:
                    # If cache miss or error, make new request
                    response = session.get(PROGRAMS_URL, params=params, headers=DEFAULT_HEADERS)
                    data = response.json()
                if data.get("Channels"):
                    success = True
                    break

                # Clear cache for failed attempts
                _cached_get_request.cache_clear()
                session.close()

            except Exception as e:
                logger.warning(f"Request failed: {e}")
                logger.debug(f"URL: {PROGRAMS_URL}{params_str}")

            retry_count += 1
            logger.warning(f"Attempt {retry_count}/{max_retries}: No valid data, retrying...")
            logger.debug(f"URL: {PROGRAMS_URL}{params_str}")
            session.close()
            if retry_count < max_retries:
                time.sleep(retry_delay)
        
        if not success:
            logger.error(f"Failed to get valid data after {max_retries} attempts")
            continue

        # Find the channel's programs
        channel_data = None
        for ch in data.get("Channels", []):
            if ch["Number"] == channel_id:
                channel_data = ch
                break
 
        if not channel_data:
            logger.warning(f"Channel {channel_id} not found in response")
            continue
 
        # Process each program
        logger.debug(f"Found {len(channel_data.get('Programmes', []))} programs for channel {channel_id}")
        for program in channel_data.get("Programmes", []):
            # Get program details
            try:
                details_response = session.get(
                    PROGRAM_DETAIL_URL,
                    params={"id": program["Id"]},
                    headers=DEFAULT_HEADERS
                )
                details = details_response.json()
                #params_str = str({"id": program["Id"]})
                #details = _cached_get_request(PROGRAM_DETAIL_URL, params_str)
                #logger.debug(f"Program details cache info: {_cached_get_request.cache_info()}")
            except Exception as e:
                logger.error(f"Error fetching program details: {e}")
                details = {}
 
            # Handle categories
            categories = []
            if "SubGenres" in details and details["SubGenres"]:
                # Take first genre if multiple exist
                categories.extend(details["SubGenres"])
            if "Genre" in details and details["Genre"]:
                categories.append(details["Genre"])

            # Get program icon if available
            icon = details.get("Image", None)
            if icon and not icon.startswith("http"):
                icon = f"https://03mcdecdnimagerepository.blob.core.windows.net/epguideimage/img/{icon}"

            programme_obj = Programme(
                start=sa_tz.localize(datetime.strptime(program["StartTime"], "%Y-%m-%dT%H:%M:%S")),
                stop=sa_tz.localize(datetime.strptime(program["EndTime"], "%Y-%m-%dT%H:%M:%S")),
                channel=channel_name,
                title=program["Title"],
                desc=details.get("Synopsis", ""),
                #category=details.get("SubGenres", []) if "SubGenres" in details else None
                category=categories if categories else None,
                icon=icon
            )
 
            programmes.append(programme_obj)
 
    return programmes
