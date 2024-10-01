# 🤖 Linkedin Automator

A Python library to automate various operations on LinkedIn posts, comments, and replies. So far, it supports the following features:
- Viewing all comments on posts (as well as last two replies) for each comment
- Deleting a comment or more given their links
- Deleting comments written by specific users across a number of posts

The last feature has been our main motivation for making this package since LinkedIn does not allow pages to block users from commenting on their posts.

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
To understand how to get these fields, see [setup.md](https://github.com/PalestinianVoices/linkedin_automator/blob/main/setup.md)

Import the package and instantiate


```python
from linkedin_automator import LinkedInAutomator

auto = LinkedInAutomator()
```

<p style="background-color: black; color: #B6FFFA; padding: 15px; border-radius: 10px; text-align: center; font-family: Arial, sans-serif; font-weight: bold; font-size: 15px;">
👀 Viewing comments and replies on a post
</p>


```python
# Get comments on a post
comments_info = auto.get_comments('https://www.linkedin.com/feed/update/...')
```


<p style="background-color: black; color: #B6FFFA; padding: 15px; border-radius: 10px; text-align: center; font-family: Arial, sans-serif; font-weight: bold; font-size: 15px;">
🗑️ Deleting comment(s) given a link or more
</p>


```python
# Delete comment given link
auto.purge_comment_given_link('https://www.linkedin.com/feed/update/...')
# Delete multiple comments
comment_links = [
    'https://www.linkedin.com/feed/update/...',
    'https://www.linkedin.com/feed/update/...'
]
auto.purge_comments_given_links(comment_links)
```

<p style="background-color: black; color: #B6FFFA; padding: 15px; border-radius: 10px; text-align: center; font-family: Arial, sans-serif; font-weight: bold; font-size: 15px;">
   🔥 Deleting comments written by specific profile ids across a number of posts.
</p>





```python
profile_ids = ['abc-def-1999', 'ggref-please']
post_urls = [
             'https://www.linkedin.com/feed/update/...', 
             'https://www.linkedin.com/feed/update/...'
             ]
auto.purge_comments(post_urls, profile_ids)
```

<p style="background-color: black; color: #B6FFFA; padding: 15px; border-radius: 10px; text-align: center; font-family: Arial, sans-serif; font-weight: bold; font-size: 15px;">
📃Getting recent K posts by a company
</p>



To understand how to get the company public_id, read [this](https://www.linkedin.com/help/linkedin/answer/a415420/associate-your-linkedin-company-id-with-the-linkedin-job-board-faqs#:~:text=What%20is%20a%20LinkedIn%20Company,Name%20on%20the%20Company%20dropdown.).



```python

auto.get_recent_posts(public_id='12345678', max_results=5)
```

