from routine_butler.utils.google.arbitrary_types import (
    GoogleDriveServiceObject,
)


class DriveFolderManager:
    def __init__(
        self,
        root_folder_name: str,
    ):
        self.root_folder_name = root_folder_name
        self._root_folder_id = None

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

    def get_root_folder_id(self, service: GoogleDriveServiceObject) -> str:
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

    def get_folder_id_from_path(
        self,
        service: GoogleDriveServiceObject,
        path_to_folder: str,
        should_create_path: bool = False,
    ) -> str:
        current_parent_folder_id = self.get_root_folder_id(service)
        for folder_name in path_to_folder.split("/"):
            current_parent_folder_id = self._get_folder_id(
                service,
                folder_name,
                current_parent_folder_id,
                should_create_path,
            )
        return current_parent_folder_id
