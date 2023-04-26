#! /usr/bin/env python3

import json
from urllib.parse import urlparse
import sys
from utils import *

# Load Yammer configuration
yammer_cfg = load_yammer_config()

# Load the stored release from a file
with open('db/github.db', 'r') as f:
    published_github = set(f.read().splitlines())

# Init the empty list of repo and Set the URL, parameters for the GitHub API
u = 'https://api.github.com/orgs/hashicorp/repos'
page = 1
repos = []

# Loop through the paginated results until all repositories have been retrieved
while True:
    # Send a GET request to the API for the current page of repositories
    params = {'per_page': 100, 'page': page}
    response = get_url(u, params=params)

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

# Now we have the list of repos, loop over them to find releases of all terraform providers
for repo in repos:
    if repo['name'].startswith('terraform-provider-') and not repo['archived']:
        print(repo['name'])

        # Send a GET request to the API
        url = 'https://api.github.com/repos/hashicorp/' + repo['name'] + '/releases'
        response = get_url(url)
        
        # If the response is a 2XX,
        # list releases for the current repo and notify.
        if response is not None:
            releases = json.loads(response.text)

            for release in releases:
                # Check if the release has already been published
                if release['html_url'] in published_github:
                    print('Item already published:', release['html_url'])
                    continue

                # Get terraform provider name
                provider_name = urlparse(url).path.split('/')[3]

                # Construct the message to post to Yammer
                message = {
                    'body': provider_name + ' provider: new release ' + release['tag_name'],
                    'og_url': release['html_url'],
                    'group_id': yammer_cfg['group_id']
                }

                # Set the Yammer API request headers and make request.
                headers = {'Authorization': 'Bearer ' + yammer_cfg['access_token']}
                response = requests.post(yammer_cfg['api_endpoint'], headers=headers, json=message)
            
                # Add the article ID to the set of published articles,
                # and print the return code.
                print('Yammer API response for:', release['html_url'], ':', str(response.status_code))
                if str(response.status_code) == '201':
                    published_github.add(release['html_url'])

            # Save the updated set of published article IDs to the file
            with open('db/github.db', 'w') as f:
                f.write('\n'.join(published_github))
        # If the response is not a 2XX, quit.
        else:
            sys.exit()