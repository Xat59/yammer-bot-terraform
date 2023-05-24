#! /usr/bin/env python3

import requests
from datetime import datetime
from urllib.parse import urlparse
import configparser
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import sys

def get_url(url, params=None, headers=None):
    """This function makes a GET request to the given URL and returns the full response."""
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        # Give more information when there are an error with api.github.com
        if urlparse(url).hostname == "api.github.com":
            if response.status_code == '403':
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

def load_github_config():
    """Get GitHub configuration from config.ini file."""
    try:
        parser = configparser.ConfigParser()
        parser.read('config.ini')

        config = {
            'access_token': parser.get('github', 'access_token')
        }

        # Return the GitHub config and print we will use an access token.
        print(f"Using authenticated GitHub user.")
        return config
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        print(f"Using anonymous GitHub user: no GitHub access token found in config.ini file.")
        return None

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

def post_yammer_message(message):
    """Send a message to a Yammer group."""
    
    # Load Yammer configuration
    yammer_cfg = load_yammer_config()

    # Add the Yammer group in the request
    message['group_id'] = yammer_cfg['group_id']

    # Set the Yammer API request headers and make request.
    headers = {'Authorization': 'Bearer ' + yammer_cfg['access_token']}
    response = requests.post(yammer_cfg['api_endpoint'], headers=headers, json=message)

    # Print Yammer API response.
    # And return the response.
    print('Yammer API response for:', message['og_url'], ':', str(response.status_code))
    return response

def get_github_release_from_db(repo_name):
    """Retrieve the release that is actually in the DB file for a specific Github repository."""

    repo_url = 'https://github.com/hashicorp/' + repo_name + '/'
    try:
        with open('db/github.db', 'r') as f:
            for line in f:
                # If we have a release for this repo in DB, just return its URL.
                if repo_url in line:
                    return urlparse(line).path.split('/')[5]

        # No release has been found for this repo in the DB.
        return None
    except FileNotFoundError:
        print('The file was not found.')
    except IOError:
        print('An error occurred while reading the file.')