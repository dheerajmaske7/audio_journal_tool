
import requests
import json

# Replace with your actual Medium integration token
MEDIUM_TOKEN = '2ca2e40b348a302dfb0f4ec927f9b0f596596f2fc28f9c550f6b823f1aa6ef83e'


# Read the title from title.txt
with open('title.txt', 'r') as title_file:
    title = title_file.read().strip()

# Read the content from blog.txt
with open('Blog_generated\content.txt', 'r') as content_file:
    content = content_file.read().strip()


# Setting up headers with authorization
headers = {
    'Authorization': f'Bearer {MEDIUM_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Host': 'api.medium.com',
    'Accept-Charset': 'utf-8'
}

# Fetch user details to get the user ID
user_url = 'https://api.medium.com/v1/me'
user_response = requests.get(url=user_url, headers=headers)
user_data = user_response.json()

# Check if the user data was fetched successfully
if 'data' in user_data:
    user_id = user_data['data']['id']
else:
    print("Error fetching user data:", user_data)
    exit()

# Article content and metadata
article_data = {
    'title': title,
    'contentFormat': 'markdown',  # Choose 'html', 'markdown', or 'plain'
    'content': content,
    'tags': ['python', 'api', 'medium'],
    'publishStatus': 'draft'  # Choose 'public' or 'draft'
}

# Publish the article
publish_url = f'https://api.medium.com/v1/users/{user_id}/posts'
publish_response = requests.post(url=publish_url, headers=headers, data=json.dumps(article_data))

# Check if the post was created successfully
if publish_response.status_code == 201:
    print('Post published successfully:', publish_response.json())
else:
    print('Failed to publish the post:', publish_response.json())
