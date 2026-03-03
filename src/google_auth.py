import google.oauth2.service_account
import google.auth.transport.requests
import os


SERVICE_ACCOUNT_KEY_FILE = os.environ.get('SERVICE_ACCOUNT_KEY_FILE')
# SERVICE_ACCOUNT_KEY_FILE ="/home/datasuke/projects/blankit-server/hallowed-byte-429019-g1-e0f0c3a585ed.json"
SCOPES = [os.environ.get('GOOGLE_SCOPES')]

def get_access_token():
    # Create credentials from the service account key file
    credentials = google.oauth2.service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_FILE, scopes=SCOPES)

    # Create a request object
    request = google.auth.transport.requests.Request()

    # Refresh credentials to get an access token
    credentials.refresh(request)

    # The access token is now available
    access_token = credentials.token

    return access_token

if __name__=='__main__':
    access_token = get_access_token()
    print(f"Access Token: {access_token}")