# #!/usr/bin/env python3

# """ Module for handling OAuth Authentication for Zoho CRM """

# import os
# import redis
# import requests

# from dotenv import load_dotenv

# load_dotenv()


# def get_zoho_oauth_token():
#     """
#     Get the OAuth token for Zoho CRM
#     """
#     try:
#         redis_host = os.getenv("REDIS_HOST")
#         redis_port = os.getenv("REDIS_PORT")
#         redis_password = os.getenv("REDIS_PASSWORD")
#         redis_db = os.getenv("REDIS_DB")

#         r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=redis_db)

#         # Check if the token is already in the cache
#         if r.exists("zoho_oauth_token"):
#             return r.get("zoho_oauth_token").decode('utf-8')

#         # If the token is not in the cache, get a new token
#         code = ""
#         client_id = os.getenv("ZOHO_CLIENT_ID")
#         client_secret = os.getenv("ZOHO_CLIENT_SECRET")
#         redirect_uri = os.getenv("ZOHO_REDIRECT_URI")
#         grant_type = "authorization_code"
#         refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")

#         url = "https://accounts.zoho.com/oauth/v2/token"
#         payload = {
#             "code": code,
#             "client_id": client_id,
#             "client_secret": client_secret,
#             "redirect_uri": redirect_uri,
#             "grant_type": grant_type
#         }

#         response = requests.post(url, data=payload)
#         response.raise_for_status()

#         token = response.json()["access_token"]

#         # Cache the tokens
#         r.set("zoho_oauth_token", token, ex=3480)

#         return token
#     except Exception as e:
#         print(f"Error getting Zoho OAuth token: {str(e)}")
