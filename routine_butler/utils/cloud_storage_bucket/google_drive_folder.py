import os.path
from os import PathLike
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger

from routine_butler.utils.cloud_storage_bucket.base import (
    CloudStorageBucket,
    CloudStorageBucketItem,
)
from routine_butler.utils.google.arbitrary_types import (
    GoogleDriveServiceObject,
)
from routine_butler.utils.google.drive_folder_manager import DriveFolderManager
from routine_butler.utils.google.g_suite_credentials_manager import (
    G_Suite_Credentials_Manager,
)


class GoogleDriveFolder(CloudStorageBucket):
    def __init__(
        self,
        folder_name: str,
        credentials_manager: G_Suite_Credentials_Manager,
    ):
        self.credentials_manager = credentials_manager
        self.drive_folder_manager = DriveFolderManager(
            root_folder_name=folder_name,
        )

    def _get_service_object(self) -> GoogleDriveServiceObject:
        """Builds and returns a Google Drive service object."""
        service = build(
            "drive",
            "v3",
            credentials=self.credentials_manager.get_credentials(),
        )
        return service

    def _list(self, remote_path: Optional[str] = None):
        service = self._get_service_object()
        if remote_path is None:
            folder_id = self.drive_folder_manager.get_root_folder_id(service)
        else:
            folder_id = self.drive_folder_manager.get_folder_id_from_path(
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
            folder_id = self.drive_folder_manager.get_root_folder_id(service)
        else:
            folder_id = self.drive_folder_manager.get_folder_id_from_path(
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
            folder_id = self.drive_folder_manager.get_root_folder_id(service)
        else:
            folder_id = self.drive_folder_manager.get_folder_id_from_path(
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
            folder_id = self.drive_folder_manager.get_root_folder_id(service)
            item_name = remote_path
        else:
            remote_path_components = remote_path.split("/")
            folder_id = self.drive_folder_manager.get_folder_id_from_path(
                service, "/".join(remote_path_components[:-1]), False
            )
            item_name = remote_path_components[-1]

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
