#! /usr/bin/env python3

import requests
from datetime import datetime
from urllib.parse import urlparse
import configparser

def get_url(url, params=None):
    """This function makes a GET request to the given URL and returns the full response."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        # Give more information when there are an error with api.github.com
        if urlparse(url).hostname == "api.github.com":
            print("More details:")
            print("  Remaining requests:   ", response.headers['X-RateLimit-Remaining'], "/", response.headers['X-RateLimit-Limit'])
            print("  Rate limit expiration:", str(datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))))
        return None

def load_yammer_config():
    """Get Yammer configuration from config.ini file."""
    try:
        parser = configparser.ConfigParser()
        parser.read('config.ini')

        config = {
            'api_endpoint': parser.get('yammer', 'api_endpoint'),
            'access_token': parser.get('yammer', 'access_token'),
            'group_id': parser.get('yammer', 'group_id')
        }

        return config
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)