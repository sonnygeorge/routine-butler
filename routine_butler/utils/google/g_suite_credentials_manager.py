import asyncio
import multiprocessing
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import google_auth_oauthlib.flow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from nicegui import ui

CODE_TEMP_FILE_PATH = "code.txt"
TOKEN_FILE_PATH = "token.json"


class AuthRedirectRequestHandler(BaseHTTPRequestHandler):
    """HTTP server class to capture the authorization response"""

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params:
            code = query_params["code"][0]
            with open(CODE_TEMP_FILE_PATH, "w") as f:
                f.write(code)
            # redirect back to Routine Butler
            self.send_response(302)
            self.send_header("Location", "http://localhost:8080/do-routine")
            self.end_headers()


# Start the HTTP server in a separate process
def start_server_to_listen_for_auth_redirect():
    server_address = ("", 8081)  # Change the port to 8081
    httpd = HTTPServer(server_address, AuthRedirectRequestHandler)
    httpd.serve_forever()


class G_Suite_Credentials_Manager:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, credentials_file_path: str):
        self.credentials_file_path = credentials_file_path
        self._credentials = None

    async def run_auth_flow(self):
        if os.path.exists(CODE_TEMP_FILE_PATH):
            os.remove(CODE_TEMP_FILE_PATH)
        # start a temporary server to listen for the redirect
        server_process = multiprocessing.Process(
            target=start_server_to_listen_for_auth_redirect
        )
        server_process.start()
        # build the flow and get the authorization url
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.credentials_file_path,
            scopes=self.SCOPES,
            redirect_uri="http://localhost:8081",
        )
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        # redirect to given authorization url
        ui.timer(0.1, lambda: ui.open(authorization_url), once=True)
        # wait for the code to be written to the file once auth is complete
        while not os.path.exists(CODE_TEMP_FILE_PATH):
            await asyncio.sleep(0.2)
        # stop the server
        server_process.terminate()
        # read the code from the file & delete it
        with open(CODE_TEMP_FILE_PATH, "r") as f:
            code = f.read()
        os.remove(CODE_TEMP_FILE_PATH)
        # ascertain credentials
        flow.fetch_token(code=code)
        self._credentials = flow.credentials
        # save the credentials
        with open(TOKEN_FILE_PATH, "w") as f:
            f.write(self._credentials.to_json())

    async def _authorize(self):
        """Performs Google API authorization by using by either asserting that token.json
        exists and is valid, or opening the Google's auth screen in the  browser and
        either creating or overwriting token.json with valid credentials.
        """

        # token.json stores the access and refresh tokens, and is auto-generated
        if self._credentials is None and os.path.exists(TOKEN_FILE_PATH):
            self._credentials = Credentials.from_authorized_user_file(
                TOKEN_FILE_PATH, self.SCOPES
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
                    with open(TOKEN_FILE_PATH, "w") as f:
                        f.write(self._credentials.to_json())
                except RefreshError:
                    run_auth_flow = True
            else:
                run_auth_flow = True

            if run_auth_flow:
                await self.run_auth_flow()

    async def get_credentials(self):
        if not self._credentials or not self._credentials.valid:
            await self._authorize()
        return self._credentials
