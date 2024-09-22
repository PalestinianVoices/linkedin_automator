import requests
from linkedin_api import Linkedin
from extractor import extract_post_urn, extract_comment_or_reply_params

api = Linkedin('stand-with-palestine@outlook.com', 'Palestine1948')


def get_comments_info(post_url, return_full_objects=False):
    try:
        # Use linked api package to get comments
        comments = api.get_post_comments(post_urn=extract_post_urn(post_url), comment_count=200)
    except Exception as e:
        # Often fails if no comment
        if "paginationToken" in str(e):
            print("Pagination token error. Post may have no comments")
            return ([],[]) if return_full_objects else []
        else:
            print("An error occurred:", e)
    # List of comments/replies for the post
    comments_info = []
    for i, comment in enumerate(comments):
        replies = []
        # Get replies if any first
        for reply in comments[i]['socialDetail']['comments']['elements']:
            reply_commenter_obj = reply['commenter']
            # Get the lone key inside the reply_comenter_obj which indicates user or company
            profile_attr = next(iter(reply_commenter_obj))
            # Set replier profileId
            if profile_attr == 'com.linkedin.voyager.feed.MemberActor':
                profileId = reply_commenter_obj[profile_attr]['miniProfile']['publicIdentifier']
            else:
                profileId = reply_commenter_obj[profile_attr]['miniCompany']['universalName']
                # append reply info
                replies.append({
                    "profileID": profileId,
                    "link": reply['permalink'],
                    "text": reply["commentV2"]['text'],
                }
                    )
        # Get the lone key incommener obj defining normal user or company
        commenter_obj = comment['commenter']
        profile_attr = next(iter(commenter_obj))
        # Set profileId accordingly
        if profile_attr == 'com.linkedin.voyager.feed.MemberActor':
            profileId = commenter_obj[profile_attr]['miniProfile']['publicIdentifier']
        else:
            profileId = commenter_obj[profile_attr]['miniCompany']['universalName']
        # append comment into
        comments_info.append(
            {
            "profileID": profileId,
            "link": comment['permalink'],
            "text": comment['comment']['values'][0]['value'],
            "replies": replies
            }
            )
    # comments is the full spaghetti object from the library 
    return (comments_info, comments) if return_full_objects else comments_info

def get_bad_comments_links(post_url, bad_profile_ids):
    comments_info = get_comments_info(post_url)
    bad_comments_links = []
    # loop on each comment and add its link if its in bad_profile_ids
    for comment in comments_info:
        if comment['profileID'] in bad_profile_ids:
            bad_comments_links.append(comment['link'])
        # loop on each reply and add its link if its in bad_profile_ids
        for reply in comment['replies']:
            if reply['profileID'] in bad_profile_ids:
                bad_comments_links.append(reply['link'])
    return bad_comments_links

def get_bad_comments_links_many_posts(post_urls, bad_profile_ids):
    # apply get_bad_comments_links to each post and return result in one flattened list
    bad_comments_links = []
    for post_url in post_urls:
        bad_comments_links.extend(get_bad_comments_links(post_url, bad_profile_ids))
    return bad_comments_links

def purge_comment(actor_urn,access_token, ugc_post_urn,comment_id):
    url = f'https://api.linkedin.com/v2/socialActions/{ugc_post_urn}/comments/{comment_id}?actor={actor_urn}'
    
    # Set up the headers with your access token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Make the DELETE request
    response = requests.delete(url, headers=headers)
    
    # Check the response status and print an indicative response message
    if response.status_code == 204:
        return True,'Comment deleted successfully.'
    else:
        return False,f'Error: {response.status_code} - {response.text}'
    
def purge_comments(actor_urn,access_token,comments_links):
    
    # for each comment, get the URN and comment ID and delete the comment
    # add the failed comments to a list and return it
    failed_comments = []
    for comment_link in comments_links:
        ugc_post_urn,comment_id = extract_comment_or_reply_params(comment_link)
        status,message = purge_comment(actor_urn,access_token,ugc_post_urn,comment_id)
        if not status:
            failed_comments.append({"comment_link":comment_link,"Response": message}) 

    return failed_comments

