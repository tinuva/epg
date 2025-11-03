from epg_grabber.constants import EPG_GENERATOR, EPG_XMLTV_TIMEFORMAT
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from string import punctuation
from typing import List, Optional, Union, Dict
from pytz import timezone


class Channel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="@id")
    display_name: Dict = Field(alias="display-name")
    channel_id: Optional[str] = None
    icon: Dict

    @field_validator("id", mode="before")
    @classmethod
    def tvg_id_sanitize(cls, value):
        value = [value.replace(char, "")
                 for char in punctuation if char != "."][0]
        value = value.replace(" ", "")
        return value.lower()

    @field_validator("display_name")
    @classmethod
    def lang_dict(cls, value):
        if isinstance(value, Dict):
            value = value["#text"]

        return dict({"@lang": "en", "#text": value.strip()})

    @field_validator("icon")
    @classmethod
    def icon_str(cls, value):
        if isinstance(value, Dict):
            value = value["@src"]
        return dict({"@src": value})


class ChannelMetadata(BaseModel):
    channels: List[Channel]


class Programme(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start: str = Field(alias="@start")
    stop: str = Field(alias="@stop")
    channel: str = Field(alias="@channel")
    title: Dict
    desc: Optional[Dict] = None
    season: Optional[str] = None
    episode: Optional[str] = None
    category: Optional[List[Dict]] = None
    icon: Optional[Dict] = None
    rating: Optional[str] = None

    @field_validator("start", "stop", mode="before")
    @classmethod
    def xmltv_datetime_string(cls, value):
        if isinstance(value, str):
            return value
        if not value.tzinfo:
            utc = timezone('utc')
            value = utc.localize(value)
        xmltv_string = value.strftime(EPG_XMLTV_TIMEFORMAT)
        return xmltv_string

    @field_validator("title", "desc", mode="before")
    @classmethod
    def lang_dict(cls, value):
        if isinstance(value, Dict):
            return value
        if not value:
            value = ''
        return dict({"@lang": "en", "#text": value.strip()})

    @field_validator("category", mode="before")
    @classmethod
    def category_list_to_dict(cls, value):
        if not value:
            return None
        if isinstance(value, list) and value and isinstance(value[0], Dict):
            return value
        return [{"@lang": "en", "#text": cat.strip()} for cat in value if cat]

    @field_validator("icon", mode="before")
    @classmethod
    def icon_str(cls, value):
        if isinstance(value, Dict):
            if "@src" in value:
                return value
            value = value.get("@src", value)
        return dict({"@src": value})


class TvDataItem(BaseModel):
    generator: str = Field(default=EPG_GENERATOR, alias="@generator-info-name")
    channel: List[Channel]
    programme: List[Programme]


class TvData(BaseModel):
    tv: TvDataItem


class InputConfigItem(BaseModel):
    site: str
    channels: List[str]


class InputConfig(BaseModel):
    days: Optional[int] = None
    configs: List[InputConfigItem]
    workers: Optional[int] = None
