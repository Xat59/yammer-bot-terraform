#! /usr/bin/env python3

import requests
from datetime import datetime
from urllib.parse import urlparse
import configparser
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

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
            print("  Rate limit expiration:", str(datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))), "(", get_remaining_time(datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))), ")")
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

def get_remaining_time(date):
    """Get the remaining time to reach the provided date in human readable format."""
    try:
        # Current time
        now = datetime.now()

        # Time difference
        time_difference = relativedelta(date, now)

        # Construct the remaining time string
        remaining_time = ""
        if time_difference.years > 0:
            remaining_time = remaining_time + str(time_difference.years) + " years, "
        if time_difference.months > 0:
            remaining_time = remaining_time + str(time_difference.months) + " months, "
        if time_difference.days > 0:
            remaining_time = remaining_time + str(time_difference.days) + " days, "
        if time_difference.hours > 0:
            remaining_time = remaining_time + str(time_difference.hours) + " hours, "
        if time_difference.minutes > 0:
            remaining_time = remaining_time + str(time_difference.minutes) + " minutes, "
        if time_difference.seconds > 0:
            remaining_time = remaining_time + str(time_difference.seconds) + " seconds"
        
        # Return the time difference in human-readable format
        return remaining_time
    except:
        return None

def create_db_file(filename):
    """Create the db/<filename>.db that contains already published items."""
    try:
        # Set the filename location
        filename = 'db/'+ filename + '.db'

        # Create the db directory if it doesn't exist
        if not os.path.exists('db'):
            os.makedirs('db')

        # Check if the file exists
        if not os.path.exists(filename):
            # Create the file if it doesn't exist
            open(filename, 'w').close()
    except:
        print('Cannot create DB file: db/' + filename + '.db')
        sys.exit()