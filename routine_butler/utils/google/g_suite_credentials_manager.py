import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class G_Suite_Credentials_Manager:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, credentials_file_path: str):
        self.credentials_file_path = credentials_file_path
        self._credentials = None

    def _authorize(self):
        """Performs Google API authorization by using by either asserting that token.json
        exists and is valid, or opening the Google's auth screen in a browser and either
        creating or overwriting token.json with valid credentials.
        """

        # token.json stores the access and refresh tokens, and is auto-generated
        if self._credentials is None and os.path.exists("token.json"):
            self._credentials = Credentials.from_authorized_user_file(
                "token.json", self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not self._credentials or not self._credentials.valid:
            run_auth_flow = False

            if (  # If token.json exists but is expired, try to refresh it
                self._credentials
                and self._credentials.expired
                and self._credentials.refresh_token
            ):
                try:
                    self._credentials.refresh(Request())
                except RefreshError:
                    run_auth_flow = True
            else:
                run_auth_flow = True

            if run_auth_flow:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file_path, self.SCOPES
                )
                self._credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self._credentials.to_json())

    def get_credentials(self):
        if not self._credentials or not self._credentials.valid:
            self._authorize()
        return self._credentials
