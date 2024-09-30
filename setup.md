## 💻 Setup Before using the Package

In this we assume you have a Linkedin company page for which you created a "Linkedin App" via [LinkedIn Developer Solutions](https://developer.linkedin.com/). The first step is to ensure that these two products are added to the app:

<img width="470" alt="image" src="https://github.com/user-attachments/assets/2d90cc23-bfec-454b-b36d-28eabcf67163">

Which would imply that you have the following scopes:

<img width="464" alt="image" src="https://github.com/user-attachments/assets/e5addf2b-1856-4533-b599-9de8701ce530">

## Step 1️⃣: Authorization Token
With this, you first need an authorization token:

```python
import requests

#Step 1 - GET to request for authentication
def get_auth_link():
    URL = "https://www.linkedin.com/oauth/v2/authorization"
    client_id="your client id"
    redirect_uri = 'http://localhost/'
    scope = 'openid profile email w_member_social'  
    PARAMS = {'response_type':'code', 'client_id':client_id,  'redirect_uri':redirect_uri, 'scope':scope}
    r = requests.get(url = URL, params = PARAMS)
    return_url = r.url
    print('Please copy the URL and paste it in browser for getting authentication code')
    print('')
    print(return_url)

get_auth_link()
```
Which you can get by running this then clicking the link which will give the authorization token or code in the url it forwards you to.

## Step 2️⃣: Authentication Token
The next step is to get the access token using the authorization code:
```python
import requests
import json

AUTH_CODE = "put_auth_code here"

def get_access_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'OAuth gem v0.4.4'}
    ACCESS_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    client_id= "your client id"
    client_secret= "your client secret"
    redirect_uri = 'http://localhost/'
    PARAM = {'grant_type': 'authorization_code',
      'code': AUTH_CODE,
      'redirect_uri': redirect_uri,
      'client_id': client_id,
      'client_secret': client_secret}
    response = requests.post(ACCESS_TOKEN_URL, data=PARAM, headers=headers, timeout=600)
    data = response.json()
    return data

res = get_access_token()
access_token = res['access_token']
```

## Step 3️⃣: Actor URN
The last step is to get your actor_urn code
```python
def get_user_info(access_token):
    URL = "https://api.linkedin.com/v2/userinfo"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        r = requests.get(url=URL, headers=headers)
        r.raise_for_status()
        user_info = r.json()
        return user_info
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

res_user = get_user_info(access_token)
actor_urn = res_user['sub']
```

## Step 4️⃣: Setup Environment
With this you have all the info needed to setup your environment; make a `.env` file and put:
```
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ACTOR_URN=
```

Be careful not to share even the authentication code with anyone as that would give them the ability to use the LinkedIn API on your account.
