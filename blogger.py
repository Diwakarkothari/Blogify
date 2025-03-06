from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Blogger API Settings
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "3517756953939998114"  # Replace with your Blogger Blog ID


def authenticate_google():
    creds = None
    # Load token if exists
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, ask user to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def create_post(title, content, is_draft=False):
    """Posts a new article to Blogger"""
    creds = authenticate_google()
    service = build("blogger", "v3", credentials=creds)

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": ["Automated", "Python"],  # Tags
        "status": "DRAFT" if is_draft else "LIVE"
    }

    post = service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
    print(f"Post Published: {post['url']}")


# Example Usage
create_post("My Automated Blog Post", "<p>This is an automated post using Python and Blogger API.</p>", is_draft=True)
