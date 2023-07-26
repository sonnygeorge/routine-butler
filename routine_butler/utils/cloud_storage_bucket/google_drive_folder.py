import os.path
from os import PathLike
from typing import List, Optional, Protocol

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger

from routine_butler.utils.cloud_storage_bucket.base import (
    CloudStorageBucket,
    CloudStorageBucketItem,
)

# Some protocols for the Google API Drive-related objects
# (their "Resources" are dynamically generated and thus, not typed)


class GoogleDrivePendingOperation(Protocol):
    def execute(self) -> dict:
        ...


class GoogleDriveFilesObject(Protocol):
    def list(
        self,
        q: str,
        spaces: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> GoogleDrivePendingOperation:
        ...

    def create(
        self,
        body: dict,
        fields: str,
        media_body: Optional[MediaFileUpload] = None,
    ) -> GoogleDrivePendingOperation:
        ...

    def delete(
        self,
        fileId: str,
    ) -> GoogleDrivePendingOperation:
        ...

    def get_media(self, fileId: str):
        ...


class GoogleDriveServiceObject(Protocol):
    def files(self) -> GoogleDriveFilesObject:
        ...


class GoogleDriveFolder(CloudStorageBucket):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, folder_name: str, credentials_file_path: str):
        self.root_folder_name = folder_name
        self.credentials_file_path = credentials_file_path
        self._root_folder_id = None
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

    def _create_folder(
        self,
        service: GoogleDriveServiceObject,
        folder_name: str,
        parent_folder_id: str,
    ) -> str:
        """Creates a folder with the given name and parent folder ID in Google Drive.
        Args:
            service: Google Drive service object.
            folder_name: Name of the folder to create.
            parent_folder_id: ID of the folder to create it in
        Returns:
            ID of the created folder.
        """
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id],
        }
        r = service.files().create(body=folder_metadata, fields="id").execute()
        return r["id"]

    def _get_root_folder_id(self, service: GoogleDriveServiceObject) -> str:
        if self._root_folder_id is not None:
            return self._root_folder_id  # Previously gotten

        # Check if root folder exists in Drive
        query = (
            f"name='{self.root_folder_name}' "
            f"and mimeType='application/vnd.google-apps.folder'"
        )
        resp = service.files().list(q=query, spaces="drive").execute()
        if len(resp["files"]) == 0:
            # If not, create it
            root_id = self._create_folder(service, self.root_folder_name, None)
        else:
            root_id = resp["files"][0]["id"]
        self._root_folder_id = root_id  # store for later
        return self._root_folder_id

    def _get_folder_id(
        self,
        service: GoogleDriveServiceObject,
        folder_name: str,
        parent_folder_id: str,
        create_if_non_existant: bool = False,
    ) -> str:
        # Check if folder exists in Drive
        query = (
            f"name='{folder_name}' and '{parent_folder_id}' in parents "
            f"and mimeType='application/vnd.google-apps.folder'"
        )
        resp = service.files().list(q=query, spaces="drive").execute()

        if len(resp["files"]) == 0 and create_if_non_existant:
            return self._create_folder(service, folder_name, parent_folder_id)
        elif len(resp["files"]) == 0:
            raise ValueError(f"Folder '{folder_name}' not found")
        else:
            mime_type = resp["files"][0]["mimeType"]
            if mime_type != "application/vnd.google-apps.folder":
                raise ValueError("_get_folder_id() called on a non-folder")
            return resp["files"][0]["id"]

    def _get_folder_id_from_path(
        self,
        service: GoogleDriveServiceObject,
        path_to_folder: str,
        should_create_path: bool = False,
    ) -> str:
        current_parent_folder_id = self._get_root_folder_id(service)
        for folder_name in path_to_folder.split("/"):
            current_parent_folder_id = self._get_folder_id(
                service,
                folder_name,
                current_parent_folder_id,
                should_create_path,
            )
        return current_parent_folder_id

    def _get_service_object(self) -> GoogleDriveServiceObject:
        if not self._credentials or not self._credentials.valid:
            self._authorize()
        service = build("drive", "v3", credentials=self._credentials)
        return service

    def _list(self, remote_path: Optional[str] = None):
        service = self._get_service_object()
        if remote_path is None:
            folder_id = self._get_root_folder_id(service)
        else:
            folder_id = self._get_folder_id_from_path(
                service, remote_path, False
            )
        q = f"'{folder_id}' in parents and trashed = false"
        resp = service.files().list(q=q).execute()
        return resp["files"]

    def list(
        self, remote_path: Optional[str] = None
    ) -> List[CloudStorageBucketItem]:
        files = self._list(remote_path=remote_path)
        items = []
        for file in files:
            name = file["name"]
            is_dir = file["mimeType"] == "application/vnd.google-apps.folder"
            # exclude deleted files
            if name == "test_sheet_3_40_12":
                print("here")
            items.append(CloudStorageBucketItem(name=name, is_dir=is_dir))
        return items

    def upload(
        self, local_path: PathLike, remote_dir_path: Optional[str]
    ) -> None:
        service = self._get_service_object()

        if remote_dir_path is None:
            folder_id = self._get_root_folder_id(service)
        else:
            folder_id = self._get_folder_id_from_path(
                service, remote_dir_path, True
            )

        file_metadata = {
            "name": os.path.basename(local_path),
            "parents": [folder_id],
        }
        media = MediaFileUpload(local_path)
        service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

    def download(self, local_path: PathLike, remote_path: str) -> None:
        service = self._get_service_object()
        remote_path_trail = remote_path.split("/")

        if len(remote_path_trail) == 1:
            folder_id = self._get_root_folder_id(service)
        else:
            folder_id = self._get_folder_id_from_path(
                service, "/".join(remote_path_trail[:-1]), False
            )

        # Get file id
        file_query = (
            f"name='{remote_path_trail[-1]}' "
            f"and mimeType!='application/vnd.google-apps.folder'"
            f"and '{folder_id}' in parents"
        )
        resp = (
            service.files()
            .list(q=file_query, spaces="drive", fields="files(id)")
            .execute()
        )
        file_id = resp["files"][0]["id"]

        # Download file
        request = service.files().get_media(fileId=file_id)
        with open(local_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(
                    f"Remote file download: {int(status.progress() * 100)}%."
                )
        return file_id

    def delete(self, remote_path: str) -> bool:
        service = self._get_service_object()

        if "/" not in remote_path:
            folder_id = self._get_root_folder_id(service)
            item_name = remote_path
        else:
            remote_path_trail = remote_path.split("/")
            folder_id = self._get_folder_id_from_path(
                service, "/".join(remote_path_trail[:-1]), False
            )
            item_name = remote_path_trail[-1]

        # Get item id
        query = f"name='{item_name}' and '{folder_id}' in parents"
        resp = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id)")
            .execute()
        )
        item_id = resp["files"][0]["id"]

        # Check if item has children and raise error if so
        query = f"'{item_id}' in parents"
        resp = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id)")
            .execute()
        )
        if len(resp["files"]) > 0:
            raise ValueError("Cannot delete a folder that has children.")

        # Delete item
        service.files().delete(fileId=item_id).execute()
