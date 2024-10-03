import requests
from linkedin_api import Linkedin
from linkedin_automator.extractor import extract_post_urn, extract_comment_or_reply_params
from dotenv import load_dotenv; load_dotenv()
from tqdm import tqdm
import os

import signal

# Let's make a new exception type for timeout
class TimeoutError(Exception):
    pass

# A function to throw timeout error (SIGALARM will trigger it when it needs to)
def timeout_handler(signum, frame):
    raise TimeoutError("API request timed out")

signal.signal(signal.SIGALRM, timeout_handler)


class LinkedInAutomator:
    def __init__(self, 
                 linkedin_email=os.getenv("LINKEDIN_EMAIL"), 
                 linkedin_actor_urn=os.getenv("LINKEDIN_ACTOR_URN"), 
                 linkedin_password=os.getenv("LINKEDIN_PASSWORD"), 
                 linkedin_access_token=os.getenv("LINKEDIN_ACCESS_TOKEN"),
                 cookies=None
                 ):
        load_dotenv()
        self.email = linkedin_email
        self.actor_urn = linkedin_actor_urn
        self.password = linkedin_password
        self.access_token = linkedin_access_token
        self.api = Linkedin(self.email, self.password, cookies=cookies)
        
    def get_comments(self, post_url, return_full_objects=False):
            """
            Retrieves comments from a LinkedIn post.

            Args:
            post_url (str): URL of the LinkedIn post.
            return_full_objects (bool): Whether to return full comment objects. Defaults to False.

            Returns:
            tuple or list: Comments information and optionally full comment objects.
            """
            # Use linked api package to get comments
            try:
                signal.alarm(30)  # Set timeout to 45 seconds; if they pass before signal.alarm(0), it will raise TimeoutError
                comments = self.api.get_post_comments(post_urn=extract_post_urn(post_url), comment_count=200)
                signal.alarm(0)  # Disable alarm
            except TimeoutError:
                print("API request timed out. Moving on.")
                return ([], []) if return_full_objects else []
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
                    # Append reply info
                    replies.append({
                        "profileID": profileId,
                        "link": reply['permalink'],
                        "text": reply["commentV2"]['text'],
                    })
                # Get the lone key incommener obj defining normal user or company
                commenter_obj = comment['commenter']
                profile_attr = next(iter(commenter_obj))
                # Set profileId accordingly
                if profile_attr == 'com.linkedin.voyager.feed.MemberActor':
                    profileId = commenter_obj[profile_attr]['miniProfile']['publicIdentifier']
                else:
                    profileId = commenter_obj[profile_attr]['miniCompany']['universalName']
                # Append comment info
                comments_info.append({
                    "profileID": profileId,
                    "link": comment['permalink'],
                    "text": comment['comment']['values'][0]['value'],
                    "replies": replies
                })
            # comments is the full spaghetti object from the library 
            return (comments_info, comments) if return_full_objects else comments_info

    def get_recent_posts(self,public_id, max_results):
        """
        Retrieves the recent posts of a company.
        
        Args:
        public_id (str): Public ID of the company.
        max_results (int): Maximum number of posts to retrieve.
        
        Returns:
        list: Links of the recent posts.
        """
        try:
            res = self.api.get_company_updates(public_id=public_id, max_results=max_results)
        except Exception as e:
            return "Error in getting the posts: "+str(e)
        
        links=[]
        for i in range(len(res)):
            links.append(res[i]['permalink'])
        return links[:min(max_results, len(links))]

    def get_bad_comments_links(self, post_url, bad_profile_ids):
        """
        Retrieves links of comments made by bad profiles.

        Args:
        post_url (str): URL of the LinkedIn post.
        bad_profile_ids (list): List of bad profile IDs.

        Returns:
        list: Links of bad comments.
        """
        comments_info = self.get_comments(post_url)
        bad_comments_links = []
        # Loop on each comment and add its link if its in bad_profile_ids
        for comment in comments_info:
            if comment['profileID'] in bad_profile_ids:
                bad_comments_links.append(comment['link'])
            # Loop on each reply and add its link if its in bad_profile_ids
            for reply in comment['replies']:
                if reply['profileID'] in bad_profile_ids:
                    bad_comments_links.append(reply['link'])
        return bad_comments_links
    def get_bad_comments_links_many_posts(self, post_urls, bad_profile_ids):
        """
        Retrieves links of comments or replies made by bad profiles across multiple posts.

        Args:
        post_urls (list): List of LinkedIn post URLs.
        bad_profile_ids (list): List of bad profile IDs.

        Returns:
        list: Links of bad comments or replies.
        """
        bad_comments_links = []
        for post_url in tqdm(post_urls, desc='Collecting comments for posts'):
            bad_comments_links.extend(self.get_bad_comments_links(post_url, bad_profile_ids))
        return bad_comments_links


    def purge_comment_given_link(self, comment_link):
        """
        Deletes a comment or reply on a LinkedIn post.

        Args:
        comments_link (string): link to the comment or reply to be deleted.

        Returns:
        tuple: A tuple containing a boolean indicating success or failure, and a string with an indicative message.
        """
        ugc_post_urn, comment_id = extract_comment_or_reply_params(comment_link)
        url = f'https://api.linkedin.com/v2/socialActions/{ugc_post_urn}/comments/{comment_id}?actor=urn:li:person:{self.actor_urn}'
        
        # Set up the headers with your access token
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

        # Make the DELETE request
        response = requests.delete(url, headers=headers)
        
        # Check the response status and print an indicative response message
        if response.status_code == 204:
            return True, 'Comment deleted successfully.'
        else:
            return False, f'Error: {response.status_code} - {response.text}'
        
    def purge_comments_given_links(self, comments_links):
        """
        Deletes multiple comments or replies on LinkedIn posts.

        Args:
        comments_links (list): List of links to the comments or replies to be deleted.

        Returns:
        list: A list of dictionaries containing the link to the comment that failed to be deleted and the corresponding error message.
        """
        # for each comment, get the URN and comment ID and delete the comment
        # add the failed comments to a list and return it
        failed_comments = []
        for comment_link in tqdm(comments_links, desc='Purging comments', total=len(comments_links)):
            status, message = self.purge_comment_given_link(comment_link)
            if not status:
                failed_comments.append({"comment_link":comment_link,"Response": message}) 
        if len(failed_comments) == 0 and len(comments_links) > 0: print('All comments deleted successfully.')
        return failed_comments
    
    def purge_comments(self, post_urls, profile_ids):
        """
        Deletes comments or replies made by bad profiles across multiple posts.

        Args:
        post_urls (list): List of LinkedIn post URLs.
        bad_profile_ids (list): List of bad profile IDs.

        Returns:
        list: A list of dictionaries containing the link to the comment that failed to be deleted and the corresponding error message.
        """
        comments_links = self.get_bad_comments_links_many_posts(post_urls, profile_ids)
        return self.purge_comments_given_links(comments_links)
    
    def purge_comments_recent(self, company_id, profile_ids, max_results=10, extra_post_urls=[]):
        """
        Deletes comments or replies made by bad profiles from the recent posts of a company.

        Args:
        company_id (str): Public ID of the company to get the recent posts from.
        profile_ids (list): List of bad profile IDs (whose comments or replies should be deleted).
        max_results (int): Maximum number of recent posts to retrieve. Defaults to 10.
        extra_links (list): List of extra post links to purge.

        Returns:
        list: A list of dictionaries containing the link to the comment that failed to be deleted and the corresponding error message.
        """
        recent_posts_links = self.get_recent_posts(company_id, max_results)
        failed_extra_comments = []
        if len(extra_post_urls) > 0:
            print("Extra post linked have been supplied. Purging them first....")
            failed_extra_comments = self.purge_comments_given_links(extra_post_urls)
        print(f"Back to purging comments on the {max_results} most recent posts....")
        return self.purge_comments(recent_posts_links, profile_ids) + failed_extra_comments
        