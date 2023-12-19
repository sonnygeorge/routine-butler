import asyncio
import multiprocessing
import os
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

import google_auth_oauthlib.flow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from loguru import logger
from nicegui import run, ui

if TYPE_CHECKING:
    from routine_butler.globals import PagePath

CODE_TEMP_FILE_PATH = "code.txt"
TOKEN_FILE_PATH = "token.json"


class AuthRedirectRequestHandler(BaseHTTPRequestHandler):
    """HTTP server class to capture & process the authorization response"""

    def __init__(
        self,
        redirect_server_port: int,
        redirect_page_path: str,
        *args,
        **kwargs,
    ):
        self.redirect_server_port = redirect_server_port
        self.redirect_page_path = redirect_page_path
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handles the GET request"""
        logger.info("Received GET request on temp auth-redirect server...")
        logger.info(f"Request being handled with process id {os.getpid()}.")
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if "code" in query_params:
            code = query_params["code"][0]
            logger.info(f"Received necessary code in request.")
            with open(CODE_TEMP_FILE_PATH, "w") as f:
                f.write(code)
            # Redirect back to Routine Butler
            logger.info("Responding with redirect to Routine Butler...")
            self.send_response(302)
            redirect_url = f"http://localhost:{self.redirect_server_port}"
            redirect_url += self.redirect_page_path
            self.send_header("Location", redirect_url)
            self.end_headers()
            # Shutdown after successful receiving of code
            self.server.shutdown()


# FIXME: I think this might not get taken down when I ctrl-c
def start_temp_extra_server_to_listen_for_auth_redirect(
    main_app_server_port: int,
    temp_extra_server_port: int,
    redirect_page_path: str,
):
    """Starts a temporary server to listen for the google authorization redirect"""
    logger.info(f"Temp server being started with process id {os.getpid()}.")
    server_address = ("", temp_extra_server_port)
    RequestHandlerClass = partial(
        AuthRedirectRequestHandler,
        main_app_server_port,  # NOTE: These cannot be kwargs since this is...
        redirect_page_path,  # ...later called with positional args only
    )
    httpd = HTTPServer(
        server_address=server_address,
        RequestHandlerClass=RequestHandlerClass,
    )
    httpd.serve_forever()


class G_Suite_Credentials_Manager:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(
        self,
        credentials_file_path: str,
        main_app_server_port: int,
        temp_extra_server_port: int,
        redirect_server_page_path: "PagePath",
    ):
        self.credentials_file_path = credentials_file_path
        self._credentials = None
        self.main_app_server_port = main_app_server_port
        self.temp_extra_server_port = temp_extra_server_port
        self.redirect_server_page_path = redirect_server_page_path

    async def run_auth_flow(self):
        """Runs the authorization flow and gets credentials:

        1. starts a temporary server to listen for the google auth flows redirect request
        2. builds the flow and gets the authorization url
        3. redirects to the authorization url
        4. waits for the necessary code that is embedded in the redirect request url to
           be written to a file by the temp server subprocess
        5. stops the temp server
        6. reads the code from the file
        7. exchanges the code for credentials
        8. saves the credentials to a file
        """
        if os.path.exists(CODE_TEMP_FILE_PATH):
            os.remove(CODE_TEMP_FILE_PATH)
        # 2. build the flow and get the authorization url
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.credentials_file_path,
            scopes=self.SCOPES,
            redirect_uri=f"http://localhost:{self.temp_extra_server_port}",
        )
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        # 3. redirect to given authorization url
        logger.info(f"Attempting request/redirect to google...")
        ui.timer(0.1, lambda: ui.open(authorization_url), once=True)
        # 1. start a temporary server to listen for the redirect
        start_server_callable = partial(
            start_temp_extra_server_to_listen_for_auth_redirect,
            main_app_server_port=self.main_app_server_port,
            temp_extra_server_port=self.temp_extra_server_port,
            redirect_page_path=self.redirect_server_page_path,
        )
        logger.info(
            f"Starting temporary server on port {self.temp_extra_server_port} "
            "to listen for auth redirect..."
        )
        ui.timer(0.1, lambda: run.cpu_bound(start_server_callable), once=True)
        # # 2. build the flow and get the authorization url
        # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        #     self.credentials_file_path,
        #     scopes=self.SCOPES,
        #     redirect_uri=f"http://localhost:{self.temp_extra_server_port}",
        # )
        # authorization_url, _ = flow.authorization_url(
        #     access_type="offline",
        #     include_granted_scopes="true",
        # )
        # # 3. redirect to given authorization url
        # logger.info(f"Attempting request/redirect to google...")
        # ui.timer(0.1, lambda: ui.open(authorization_url), once=True)
        # 4. wait for the code to be written to the file once auth is complete
        while not os.path.exists(CODE_TEMP_FILE_PATH):
            await asyncio.sleep(0.2)
        logger.info("Code file found.")
        # 5. stopping the server - no longer needed since server shuts itself down
        # 6. read the code from the file & deletes the file
        with open(CODE_TEMP_FILE_PATH, "r") as f:
            code = f.read()
        os.remove(CODE_TEMP_FILE_PATH)
        # 7. ascertain credentials
        flow.fetch_token(code=code)
        self._credentials = flow.credentials
        json_keys = dict(self._credentials.__dict__).keys()
        logger.info(f"Saving token file w/ keys: {json_keys}")
        # 8. save the credentials
        with open(TOKEN_FILE_PATH, "w") as f:
            f.write(self._credentials.to_json())

    def validate_credentials(self) -> bool:
        """Validates the credentials, and refreshes them if necessary.

        The implication of returning False is that user will need to re-authenticate
        """
        # If no credentials & token.json exists, try to load them
        if self._credentials is None and os.path.exists(TOKEN_FILE_PATH):
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    TOKEN_FILE_PATH, self.SCOPES
                )
            except Exception as e:
                # If the token file is somehow corrupted
                logger.error(
                    f"Error loading G-Suite token file at '{TOKEN_FILE_PATH}':"
                    f" {e}"
                )
                os.remove(TOKEN_FILE_PATH)  # Delete the corrupted token file
                return False
        # If still no credentials, return false
        if self._credentials is None:
            return False
        # If valid, return true
        if self._credentials.valid:
            return True
        # If credentials are expired, try to refresh them
        elif self._credentials.expired and self._credentials.refresh_token:
            try:
                self._credentials.refresh(Request())
                with open(TOKEN_FILE_PATH, "w") as f:
                    f.write(self._credentials.to_json())
            except RefreshError:
                return False  # Return false since refresh failed
            else:
                return False

    async def get_credentials(self) -> Credentials:
        """Returns the credentials, running the auth flow if necessary."""
        logger.info("Getting G-Suite credentials...")
        if not self.validate_credentials():
            logger.info("G-Suite credentials invalid. Running auth flow...")
            await self.run_auth_flow()
        else:
            logger.info("G-Suite credentials valid.")
        return self._credentials
