import os.path
from typing import Optional, Protocol, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger


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


class GoogleDriveFolder:
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

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if self._credentials is None and os.path.exists("token.json"):
            self._credentials = Credentials.from_authorized_user_file(
                "token.json", self.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not self._credentials or not self._credentials.valid:
            if (
                self._credentials
                and self._credentials.expired
                and self._credentials.refresh_token
            ):
                self._credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file_path, self.SCOPES
                )
                self._credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self._credentials.to_json())

    def _ascertain_folder_in_drive_and_get_id(
        self,
        service: GoogleDriveServiceObject,
        subfolder_name: Optional[str] = None,
    ) -> str:
        """Helper function that either:
            - Finds the folder in Google Drive and returns its id
        ...or, if the folder does not exist...
            - Creates the folder in Google Drive and returns its id
        """
        if subfolder_name is not None and self._root_folder_id is None:
            msg = "Root folder id must be ascertained before using subfolders"
            raise ValueError(msg)

        if subfolder_name is None and self._root_folder_id is not None:
            return self._root_folder_id  # already ascertained

        if subfolder_name is None:
            folder_name = self.root_folder_name
            query_insertion = ""
        else:
            folder_name = subfolder_name
            query_insertion = f"and '{self._root_folder_id}' in parents "

        folder_query = (
            f"name='{folder_name}' {query_insertion}"
            f"and mimeType='application/vnd.google-apps.folder'"
        )

        resp = service.files().list(q=folder_query, spaces="drive").execute()

        if len(resp["files"]) == 0:  # Folder does not yet exist in Drive
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if subfolder_name is not None:  # Add parent if subfolder
                folder_metadata["parents"] = [self._root_folder_id]
            resp = (
                service.files()
                .create(body=folder_metadata, fields="id")
                .execute()
            )
            folder_id = resp["id"]
        else:
            folder_id = resp["files"][0]["id"]

        # set root folder id if not already set
        if subfolder_name is None and self._root_folder_id is None:
            self._root_folder_id = folder_id

        return folder_id

    def _get_service_object_and_folder_id(
        self, subfolder_name: Optional[str] = None
    ) -> Tuple[GoogleDriveServiceObject, str]:
        """Helper function to get the necessary service object and folder id used in
        upload, download and list methods
        """
        if not self._credentials or not self._credentials.valid:
            self._authorize()
        service = build("drive", "v3", credentials=self._credentials)
        root_folder_id = self._ascertain_folder_in_drive_and_get_id(service)

        if subfolder_name is not None:
            folder_id = self._ascertain_folder_in_drive_and_get_id(
                subfolder_name=subfolder_name,
                service=service,
            )
        else:
            folder_id = root_folder_id

        return service, folder_id

    def list(self, subfolder_name: Optional[str] = None) -> list:
        """Lists the files in the root Google Drive folder, or if subfolder_name is
        provided, the Google Drive subfolder
        """
        service, folder_id = self._get_service_object_and_folder_id(
            subfolder_name=subfolder_name
        )
        resp = service.files().list(q=f"'{folder_id}' in parents").execute()
        return resp["files"]

    def upload(
        self,
        file_to_upload_path: str,
        destination_subfolder_name: Optional[str] = None,
    ) -> None:
        """Uploads the file at the destination_subfolder_name in the Google Drive folder,
        or root folder if no destination_subfolder_name is provided
        """
        service, folder_id = self._get_service_object_and_folder_id(
            subfolder_name=destination_subfolder_name
        )

        file_metadata = {
            "name": os.path.basename(file_to_upload_path),
            "parents": [folder_id],
        }
        media = MediaFileUpload(file_to_upload_path)
        resp = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return resp["id"]

    def download(
        self,
        file_to_download_name: str,
        destination_path: str,
        file_to_download_subfolder_name: Optional[str] = None,
    ) -> None:
        """Downloads the file with the given name from the Google Drive root folder (or
        subfolder if provided) to the given destination file path"""
        service, folder_id = self._get_service_object_and_folder_id(
            subfolder_name=file_to_download_subfolder_name
        )

        file_query = (
            f"name='{file_to_download_name}' "
            f"and mimeType!='application/vnd.google-apps.folder'"
            f"and '{folder_id}' in parents"
        )
        resp = (
            service.files()
            .list(q=file_query, spaces="drive", fields="files(id)")
            .execute()
        )
        file_id = resp["files"][0]["id"]
        request = service.files().get_media(fileId=file_id)
        with open(destination_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(
                    f"Remote file download: {int(status.progress() * 100)}%."
                )
        return file_id

    def delete(
        self, file_name: str, subfolder_name: Optional[str] = None
    ) -> None:
        """Deletes the files with the given name from the Google Drive root folder or
        subfolder, if provided
        """
        service, _ = self._get_service_object_and_folder_id(
            subfolder_name=subfolder_name
        )
        files = self.list(subfolder_name) if subfolder_name else self.list()
        for f in files:
            if f["name"] == file_name:
                service.files().delete(fileId=f["id"]).execute()
        return


# if __name__ == "__main__":
#     # Quick integration tests
#     remote_storage_folder = GoogleDriveFolder(
#         folder_name=GDRIVE_FOLDER_NAME,
#         credentials_file_path=GDRIVE_CREDENTIALS_FILE_PATH,
#     )

#     arbitrary_str = "d0jA%Ae23D23G#RAae4$a#@uSAhFD23G#RAw23G#RA%AG"

#     # Create an arbitrary, blank file locally
#     local_file_name = f"{arbitrary_str}.txt"
#     with open(local_file_name, "w") as f:
#         pass

#     def test_upload_list_and_delete_in_root_folder():
#         remote_storage_folder.upload(local_file_name)
#         files_in_root_folder = remote_storage_folder.list()
#         assert any(local_file_name == f["name"] for f in files_in_root_folder)
#         remote_storage_folder.delete(local_file_name)
#         files_in_root_folder = remote_storage_folder.list()
#         assert not any(
#             local_file_name == f["name"] for f in files_in_root_folder
#         )

#     def test_upload_list_and_delete_in_subfolder():
#         subfolder_name = arbitrary_str
#         remote_storage_folder.upload(
#             local_file_name, destination_subfolder_name=subfolder_name
#         )
#         files_in_subfolder = remote_storage_folder.list(subfolder_name)
#         assert any(local_file_name == f["name"] for f in files_in_subfolder)
#         remote_storage_folder.delete(
#             local_file_name, subfolder_name=subfolder_name
#         )
#         files_in_subfolder = remote_storage_folder.list(subfolder_name)
#         assert not any(
#             local_file_name == f["name"] for f in files_in_subfolder
#         )

#     test_upload_list_and_delete_in_root_folder()
#     test_upload_list_and_delete_in_subfolder()

#     # Delete the file locally
#     os.remove(local_file_name)
