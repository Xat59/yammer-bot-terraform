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


# DB file is empty.
# It means, that's the first time we run the script.
if len(db) == 0:
    for repo in repos:
        if repo['name'].startswith('terraform-provider-') and not repo['archived']:
            print(repo['name'])

            # Get the latest release
            url = 'https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases/latest'
            response = get_url(url, headers=headers)

            # If there are a response content for the latest release of the repo
            if response is not None:
                # print(response.text)
                # Create a json object with the response content
                latest_release = json.loads(response.text)

                # Add the release URL to the DB file
                print(latest_release['html_url'], 'added to DB.')
                db.add(latest_release['html_url'])

    # Save the DB file with latest releases of all repos.
    with open('db/github.db', 'w') as f:
        f.write('\n'.join(db))
# DB file is not empty.
# It means the script has already ran at least once.
elif len(db) > 0:
    for repo in repos:
        if repo['name'].startswith('terraform-provider-') and not repo['archived']:
            print(repo['name'])

            # Get all releases for the repo
            url = 'https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases'
            response = get_url(url, headers=headers)

            # If there are a response content when getting ALL releases
            if response is not None:
                # Create a json object with the response content
                all_releases = json.loads(response.text)

                # Loop over all releases of the repo
                # List of releases are already ordered by date
                for index, release in enumerate(all_releases):
                    # If the current release is already in the DB
                    if release['html_url'] in db:
                        # If current release is not the first one
                        # It means there are newer release(s)
                        if index > 0:
                            # Remove the old one latest from the DB
                            print(release['html_url'], 'removed from DB.')
                            db.remove(release['html_url'])
                            # Save the DB file
                            with open('db/github.db', 'w') as f:
                                f.write('\n'.join(db))
                        # Go to the next repo.
                        print(release['html_url'], "already been published. Go to the next repo.")
                        break
                    # The current release is not in the DB
                    else:
                        # Construct the message to post to Yammer group
                        provider_name = urlparse(url).path.split('/')[3]
                        message = {
                            'body': provider_name + ' provider: new release ' + release['tag_name'],
                            'og_url': release['html_url']
                        }
                        
                        # Notify to Yammer group
                        print("Notify:", release['html_url'])
                        yammer_response = post_yammer_message(message)

                        # If the message has been posted, we can update the DB file
                        # to track the latest release posted for this repo.
                        # We need to update the DB with the latest release.
                        # If the current release is the first one from the list,
                        # that means it is the latest release in the repo.
                        # So write the release in the DB
                        if yammer_response.status_code  == '201' and index == 0:
                            # Add the latest release in the DB.
                            print(release['html_url'], 'added to DB.')
                            db.add(release['html_url'])
                            # Save the DB file
                            with open('db/github.db', 'w') as f:
                                f.write('\n'.join(db))