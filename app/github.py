#! /usr/bin/env python3

import json
from urllib.parse import urlparse
import sys
from utils import *

# Init the github.db DB file
create_db_file('github')

# Load Yammer configuration
yammer_cfg = load_yammer_config()
github_cfg = load_github_config()

# Init the empty list of repo and set the URL, parameters for the GitHub API
u = 'https://api.github.com/orgs/hashicorp/repos'
page = 1
repos = []

# Set GitHub headers when using GitHub access token weither we have an access token or not.
if github_cfg is not None and github_cfg['access_token']:
    headers = {
        "Authorization": f"Bearer {github_cfg['access_token']}",
        "Accept": "application/vnd.github.v3+json"
    }
else:
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

# Load the stored release from a file
with open('db/github.db', 'r') as f:
    db = set(f.read().splitlines())

# Loop through the paginated results until all repositories have been retrieved
while True:
    # Send a GET request to the API for the current page of repositories
    params = {'per_page': 100, 'page': page}
    response = get_url(u, params=params, headers=headers)

    # If the response is a 2XX,
    # check if there are no more pages of repositories
    if response is not None:
        if not response.json():
            break

        # Parse the JSON response and append the repositories to the list
        data = json.loads(response.text)
        repos.extend(data)

        # Increment the page counter
        page += 1
    # If the response is not a 2XX, quit.
    else:
        sys.exit()

# Loop through requested GitHub repo
for repo in repos:
    if repo['name'].startswith('terraform-provider-') and not repo['archived']:
        print(repo['name'])
        # When the repo does not have any release registered in DB yet.
        # Build the DB file with the latest release for this repo.
        if get_github_release_from_db(repo['name']) is None:

            # Get the latest release for the repo
            url = 'https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases/latest'
            response = get_url(url, headers=headers)

            # If there are a response content when getting ALL releases
            if response is not None:
                # Create a json object with the response content
                latest_release = json.loads(response.text)

                # Add the latest release in the DB for this repo.
                print(latest_release['html_url'], 'added to DB.')
                db.add(latest_release['html_url'])
                
                # Save the DB file
                with open('db/github.db', 'w') as f:
                    f.write('\n'.join(db))

        # When the repo already has any release registered in DB.
        # If the registered release in DB is the latest,
        #   that means we've already notified about it.
        # If the registered release in DB is not the latest one,
        #   that means we have to notify about release updates.
        elif get_github_release_from_db(repo['name']) is not None:
            # Get the release information for the repo that is already registered in DB
            release_in_db_tag = get_github_release_from_db(repo['name'])
            print('The current release registered in DB is', release_in_db_tag)
            r = get_url('https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases/tags/' + release_in_db_tag, headers=headers)
            if r is not None:
                release_in_db = json.loads(r.text)

            # Initiate the list that contains releases to be published
            releases_to_publish = []

            # Get all releases for the repo
            url = 'https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases'
            response = get_url(url, headers=headers)

            # If there are a response content when getting ALL releases
            if response is not None:
                # Create a json object with the response content
                all_releases = json.loads(response.text)

                # Loop over all releases of the repo
                # List of releases are ordered by date from the GitHub API response
                for release in all_releases:
                    if release['published_at'] > release_in_db['published_at']:
                        provider_name = urlparse(release['html_url']).path.split('/')[2]
                        releases_to_publish.append({
                            'provider_name': provider_name,
                            'html_url': release['html_url'],
                            'tag_name': release['tag_name'],
                            'published_at': release['published_at']
                        })

            releases_to_publish.reverse()
            for index, release in enumerate(releases_to_publish):
                if index == 0:
                    release_to_delete = release_in_db['html_url']
                else:
                    release_to_delete = releases_to_publish[index - 1]['html_url']

                # Construct the message to post to Yammer group
                message = {
                    'body': release['provider_name'] + ': new release ' + release['tag_name'],
                    'og_url': release['html_url']
                }
                
                # Notify to Yammer group
                print("Notify:", release['html_url'])
                yammer_response = post_yammer_message(message)

                if yammer_response.status_code == 201:
                    # Add this release in the DB.
                    print(release['html_url'], 'added to DB.')
                    db.add(release['html_url'])

                    # Remove the old one latest from the DB
                    print(release_in_db['html_url'], 'removed from DB.')
                    db.remove(release_to_delete)

                    # Save the DB file
                    with open('db/github.db', 'w') as f:
                        f.write('\n'.join(db))