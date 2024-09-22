## Linkedin Automator

A Python library to automate various operations on LinkedIn posts, comments, and replies. So far, it supports the following features:
- Viewing all comments on posts (as well as last two replies) for each
- Deleting a comment or more given their links
- Deleting comments written by specific users across a number of posts 

### 🚀 Installation
```
pip install linkedin-automator
```

### 📒 Guide

Set in you `.env`:
```
LINKEDIN_EMAIL=...
LINKEDIN_PASSWORD=...
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_ACTOR_URN=...
```

Import the package and instantiate


```python
from linkedin_automator import LinkedInAutomator

auto = LinkedInAutomator()
```

Viewing comments on a post and deleting comments given a link:


```python
# Get comments on a post
comments_info = auto.get_comments('https://www.linkedin.com/feed/update/...')

# Delete comment given link
auto.purge_comment_given_link('https://www.linkedin.com/feed/update/...')
# Delete multiple comments
comment_links = [
    'https://www.linkedin.com/feed/update/...',
    'https://www.linkedin.com/feed/update/...'
]
auto.purge_comments_given_links(comment_links)
```


```python
profile_ids = ['abc-def-1999', 'ggref-please']
post_urls = [
             'https://www.linkedin.com/feed/update/...', 
             'https://www.linkedin.com/feed/update/...'
             ]
auto.purge_comments(post_urls, profile_ids)
```

