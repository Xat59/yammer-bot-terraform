#! /usr/bin/env python3

import feedparser
import requests
from utils import *

# Set the RSS feed URL and load Yammer configuration
rss_url = 'https://www.hashicorp.com/blog/products/terraform/feed.xml'
yammer_cfg = load_yammer_config()

# Load the stored blog article IDs from a file
with open('db/blog.db', 'r') as f:
    published_blog = set(f.read().splitlines())

# Parse the RSS feed
feed = feedparser.parse(rss_url)

# Sort the feed items by date in descending order
sorted_items = sorted(feed['items'], key=lambda x: x['updated'], reverse=False)

# Loop through the feed items and post each item to Yammer
for item in sorted_items:
    # Check if the article has already been published
    if item['id'] in published_blog:
        print('Item already published:', item['id'])
        continue

    # Construct the message to post to Yammer
    message = {
        'body': item['title'] + '\n' + item['summary'],
        'og_url': item['link'],
        'group_id': yammer_cfg['group_id']
    }

    # Set the Yammer API request headers
    headers = {'Authorization': 'Bearer ' + yammer_cfg['access_token']}

    # Make the Yammer API request to post the message
    response = requests.post(yammer_cfg['api_endpoint'], headers=headers, json=message)
    
    # Print the response status code to the console
    print('Yammer API response status code: ' + str(response.status_code))

    # Add the article ID to the set of published articles
    if str(response.status_code) == '201':
        published_blog.add(item['id'])

# Save the updated set of published article IDs to the file
with open('db/blog.db', 'w') as f:
    f.write('\n'.join(published_blog))
