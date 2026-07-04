import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = "3471490051249930357"

def get_blogger_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("File credentials.json tidak ditemukan. Harap unduh dari Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('blogger', 'v3', credentials=creds)

def create_post(title, content, labels=None, is_draft=False):
    service = get_blogger_service()
    if not service:
        return False
        
    post_body = {
        "title": title,
        "content": content,
    }
    
    if labels:
        post_body["labels"] = labels
        
    try:
        request = service.posts().insert(
            blogId=BLOG_ID, 
            body=post_body, 
            isDraft=is_draft
        )
        response = request.execute()
        print(f"Berhasil memposting: {title} ({'Draft' if is_draft else 'Live'})")
        return True
    except Exception as e:
        print(f"Error memposting ke Blogger: {e}")
        return False

def get_previous_post():
    service = get_blogger_service()
    if not service:
        return None
    try:
        request = service.posts().list(blogId=BLOG_ID, maxResults=1, status='LIVE')
        response = request.execute()
        items = response.get('items', [])
        if items:
            for item in items:
                title = item.get('title')
                url = item.get('url')
                if url:
                    return {'title': title, 'url': url}
    except Exception as e:
        print(f"Error mencari previous post: {e}")
    return None

if __name__ == '__main__':
    # Test otentikasi
    get_blogger_service()
    print("Otentikasi Blogger berhasil dicek!")
