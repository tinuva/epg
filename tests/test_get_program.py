from epg_grabber.utils import get_sites
from epg_grabber.constants import SITES_MODULE_IMPORT_PATH
from epg_grabber.models import Programme, InputConfig
from importlib import import_module
import pytest
import os

import logging

LOGGER = logging.getLogger(__name__)

sites = get_sites()

# Skip certain tests in CI environment
SKIP_IN_CI = [
    "unifi_com_my",
    "visionplus_id",
    "sooka_my",
    "nostv_pt"
]

site_test_config = {
    "configs": [
        {
            "site": "unifi_com_my",
            "channels": ["20000009"],
        },
        {
            "site": "astro_com_my",
            "channels": ["395"],
        },
        {
            "site": "cinemaworld_asia",
            "channels": ["cinemaworld"]
        },
        {
            "site": "mewatch_sg",
            "channels": ["97098"]
        },
        {
            "site": "rtmklik_rtm_gov_my",
            "channels": ["1"]
        },
        {
            "site": "tonton_com_my",
            "channels": ["tv3"]
        },
        {
            "site": "visionplus_id",
            "channels": ["2"]
        },
        {
            "site": "sooka_my",
            "channels": ["2443"]
        },
        {
            "site": "mana2_my",
            "channels": ["1"]
        },
        {
            "site": "nostv_pt",
            "channels": ["139"]
        }
    ]
}

input_config = InputConfig.parse_obj(site_test_config)
input_config_items = input_config.configs


@pytest.mark.parametrize("config", input_config_items)
def test_get_program(config):
    # Skip problematic services in CI
    if os.environ.get('CI') and config.site in SKIP_IN_CI:
        pytest.skip(f"Skipping {config.site} in CI environment")
        return

    LOGGER.info(f"Testing {config.site}.")
    site_module_path = f"{SITES_MODULE_IMPORT_PATH}.{config.site}"
    site_module = import_module(site_module_path)

    # Get first program
    program = site_module.get_programs(channel_id=config.channels[0])[0]

    assert isinstance(program, Programme)
