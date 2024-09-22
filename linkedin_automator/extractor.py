import re
from urllib.parse import unquote


def extract_post_urn(post_url_or_urn):
    # Pattern for URN directly given as input
    urn_pattern = r'(\d+)'
    # Pattern for the first URL form (feed/update/urn:li:activity)
    pattern1 = r'urn:li:activity:(\d+)'
    # Pattern for the second URL form (activity-<ID>)
    pattern2 = r'activity-(\d+)'
    
    # Check if input is already a URN
    urn_match = re.match(urn_pattern, post_url_or_urn)
    if urn_match:
        return urn_match.group(1)
    
    # Try matching the first URL form
    urn_match = re.search(pattern1, post_url_or_urn)
    if urn_match:
        return urn_match.group(1)
    
    # Try matching the second URL form
    urn_match = re.search(pattern2, post_url_or_urn)
    if urn_match:
        return urn_match.group(1)
    
    # Return None if no URN is found
    return None


def extract_comment_or_reply_params(url):
    # Decode the URL
    decoded_url = unquote(url)
    # Pattern to identify UGC post URN
    ugc_post_pattern = r'urn:li:ugcPost:\d+'
    # Pattern to identify comment ID (ugcPost + comment ID)
    comment_id_pattern = r'ugcPost:\d+,\d+'
    # Pattern to identify reply ID from the replyUrn section
    reply_id_pattern = r'replyUrn=urn:li:comment:\(ugcPost:\d+,\d+\)'
    
    # Extract UGC post URN
    ugc_post_urn_match = re.search(ugc_post_pattern, decoded_url)
    ugc_post_urn = ugc_post_urn_match.group(0) if ugc_post_urn_match else None
    
    # Extract reply ID if present
    reply_id_match = re.search(reply_id_pattern, decoded_url)
    reply_id = None
    if reply_id_match:
        # Split by ',' and extract the second part, then remove the closing parenthesis
        reply_id = reply_id_match.group(0).split(',')[1].split(')')[0]
        return ugc_post_urn,reply_id
    
    # If no reply found, look for comment ID
    comment_id_match = re.search(comment_id_pattern, decoded_url)
    if comment_id_match:
        comment_id = comment_id_match.group(0).split(',')[1]
        return ugc_post_urn, comment_id  # Return UGC post URN and comment ID
    
    # Return UGC post URN and None if neither is found
    return ugc_post_urn, None
