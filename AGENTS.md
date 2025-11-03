# AGENTS.md - AI Assistant Context

## Project Overview

**epg-grabber** is a Python-based Electronic Program Guide (EPG) scraper that extracts TV program schedules from various streaming and television service websites. The project generates standardized XMLTV format files compatible with media center applications like Plex, Kodi, Jellyfin, etc.

## Purpose

This tool allows users to:
- Scrape EPG data from multiple TV/streaming services
- Generate unified XMLTV files for media center applications
- Automate TV schedule collection for personal IPTV setups
- Access rich program metadata including titles, descriptions, categories, ratings, etc.

## Technical Stack

- **Language**: Python 3.7+
- **Build System**: setuptools with pyproject.toml
- **Key Dependencies**:
  - `requests~=2.31.0` - HTTP requests to streaming services
  - `loguru~=0.6.0` - Structured logging
  - `pydantic~=1.10.0` - Data validation and models
  - `xmltodict~=0.13.0` - XML generation for XMLTV format
  - `pytz~=2022.0` & `tzlocal~=5.2` - Timezone handling

## Project Structure

```
epg-grabber/
├── epg_grabber/              # Main package
│   ├── __init__.py
│   ├── app.py                # Core application logic
│   ├── cli.py                # Command-line interface
│   ├── models.py             # Pydantic data models
│   ├── constants.py          # Project constants
│   ├── utils.py              # Utility functions
│   └── sites/                # Site-specific scrapers
│       ├── channels_metadata/ # Pre-built channel metadata (JSON)
│       ├── astro_com_my.py
│       ├── dstv_com.py
│       ├── mewatch_sg.py
│       ├── tonton_com_my.py
│       ├── visionplus_id.py
│       ├── rtmklik_rtm_gov_my.py
│       ├── cinemaworld_asia.py
│       ├── mana2_my.py
│       ├── sooka_my.py
│       ├── unifi_com_my.py
│       └── nostv_pt.py
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── build/                    # Build artifacts
├── pyproject.toml            # Project configuration
├── requirements.txt          # Runtime dependencies
├── requirements-tests.txt    # Test dependencies
├── README.md                 # User documentation
├── CONTRIBUTING.md           # Contributor guide
├── LICENSE.txt               # MIT License
└── VERSION                   # Version file
```

## Supported Sites

The project currently supports EPG scraping from:

### Malaysian Services
- **astro_com_my** - Astro (Malaysia's satellite TV provider)
- **tonton_com_my** - Tonton (Media Prima streaming)
- **rtmklik_rtm_gov_my** - RTMKlik (Malaysian public broadcaster)
- **mana2_my** - Mana2 streaming service
- **sooka_my** - Sooka streaming service
- **unifi_com_my** - Unifi TV

### Regional Services
- **mewatch_sg** - MeWatch (Singapore's MediaCorp)
- **visionplus_id** - VisionPlus (Indonesia)
- **dstv_com** - DSTV (South African satellite TV)
- **nostv_pt** - NOS TV (Portugal)

### Specialized Services
- **cinemaworld_asia** - CinemaWorld Asia

## CLI Usage

The project provides `py-epg-cli` command-line tool:

### List Supported Sites
```bash
py-epg-cli --show
```

### View Channel Metadata
```bash
py-epg-cli --show astro_com_my
py-epg-cli --show astro_com_my > astro_channels.json
```

### Scrape EPG Data
```bash
py-epg-cli local --file input.json --output tv.xml --days 7 --workers 4
```

### Configuration Format
Input JSON file structure:
```json
{
    "configs": [
        {
            "site": "astro_com_my",
            "channels": ["395", "401"]
        }
    ]
}
```

## Key Features

1. **XMLTV Output** - Industry-standard format for EPG data
2. **Parallel Processing** - Multi-worker support for faster scraping
3. **Flexible Configuration** - JSON-based channel selection
4. **Rich Metadata** - Includes program titles, descriptions, categories, ratings, cast, etc.
5. **Timezone Support** - Proper handling of time zones across different regions
6. **Extensible Architecture** - Easy to add new site scrapers

## Development Guidelines

### Adding a New Site Scraper

1. Create a new Python file in `epg_grabber/sites/` named after the site (e.g., `newsite_com.py`)
2. Implement the scraper class following existing patterns
3. Add channel metadata JSON in `epg_grabber/sites/channels_metadata/`
4. Update site registry if needed
5. Add tests for the new scraper
6. Update documentation

### Data Models

The project uses Pydantic models (defined in `models.py`) for:
- Channel information
- Programme/show data
- Configuration schemas
- XMLTV output structure

### Contributing

See `CONTRIBUTING.md` for detailed guidelines on:
- Project structure conventions
- Code style requirements
- Testing procedures
- Pull request process

## Installation

### From Source
```bash
pip install git+https://github.com/akmalharith/epg-grabber.git@$VERSION
```

### Development Installation
```bash
git clone <repository-url>
cd epg-grabber
pip install -e .
```

## Common Use Cases

1. **Personal IPTV Setup** - Generate EPG for personal IPTV server
2. **Media Center Integration** - Feed program data to Plex/Kodi
3. **TV Schedule Archival** - Collect and archive program schedules
4. **Multi-region Content** - Aggregate EPG from multiple countries/services

## License

MIT License - See LICENSE.txt

## Version

Current version stored in `VERSION` file (used by setuptools dynamic versioning)