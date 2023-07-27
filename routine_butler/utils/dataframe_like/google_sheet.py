from typing import Any, List, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from routine_butler.utils.dataframe_like.base import DataframeLike
from routine_butler.utils.google.arbitrary_types import (
    GoogleDriveServiceObject,
    GoogleSheetsServiceObject,
)
from routine_butler.utils.google.drive_folder_manager import DriveFolderManager
from routine_butler.utils.google.g_suite_credentials_manager import (
    G_Suite_Credentials_Manager,
)


class GoogleSheet(DataframeLike):
    """Class for interacting with a Google Sheets workbook as if it were a single
    dataframe.

    NOTE: This class assumes that the "workbook" has exactly one sheet."""

    def __init__(
        self,
        path: str,
        root_folder_name: str,
        credentials_manager: G_Suite_Credentials_Manager,
    ):
        self.path = path
        self.drive_folder_manager = DriveFolderManager(
            root_folder_name=root_folder_name
        )
        self.credentials_manager = credentials_manager
        self._file_id: str = None
        self._sheet_name: str = None

    def _get_drive_service_object(self) -> GoogleDriveServiceObject:
        """Builds and returns a Google Drive service object."""
        return build(
            "drive",
            "v3",
            credentials=self.credentials_manager.get_credentials(),
        )

    def _get_sheets_service_object(self) -> GoogleSheetsServiceObject:
        """Builds and returns a Google Sheets service object."""
        return build(
            "sheets",
            "v4",
            credentials=self.credentials_manager.get_credentials(),
        )

    def _ascertain_file_id(self) -> None:
        service = self._get_drive_service_object()
        if self._file_id is not None:
            return

        if "/" not in self.path:
            folder_id = self.drive_folder_manager.get_root_folder_id(service)
            file_name = self.path
        else:
            path_components = self.path.split("/")
            folder_id = self.drive_folder_manager.get_folder_id_from_path(
                service, "/".join(path_components[:-1]), False
            )
            file_name = path_components[-1]

        query = (
            f"name='{file_name}' "
            f"and '{folder_id}' in parents "
            "and mimeType='application/vnd.google-apps.spreadsheet'"
        )
        try:
            resp = service.files().list(q=query, fields="files(id)").execute()
            if len(resp["files"]) == 0:
                raise FileNotFoundError(
                    f"Spreadsheet file '{self.path}' not found "
                    "in Google Drive."
                )
            else:
                self._file_id = resp["files"][0]["id"]
        except HttpError as e:
            raise Exception(
                f"An error occurred while fetching the spreadsheet ID: {e}"
            )

    def _ascertain_sheet_name(
        self, service: GoogleSheetsServiceObject
    ) -> None:
        if self._sheet_name is not None:
            return

        if self._file_id is None:
            self._ascertain_file_id()

        resp = (
            service.spreadsheets().get(spreadsheetId=self._file_id).execute()
        )
        sheets = resp["sheets"]
        if len(sheets) != 1:
            raise Exception(
                f"Expected exactly one sheet in workbook '{self.path}'"
            )
        self._sheet_name = sheets[0]["properties"]["title"]

    def get_row_at_idx(self, idx: int) -> List[Any]:
        """Returns the row at the given index as a one-dimensional list of values."""
        service = self._get_sheets_service_object()
        self._ascertain_sheet_name(service)

        range = f"{self._sheet_name}!{idx+1}:{idx+1}"
        resp = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=self._file_id, range=range)
            .execute()
        )
        return resp["values"][0]

    def shape(self) -> Tuple[int, int]:
        """Returns the number of populated rows and columns in the sheet."""
        service = self._get_sheets_service_object()
        self._ascertain_sheet_name(service)

        range = f"{self._sheet_name}!A1:ZZ"
        resp = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=self._file_id, range=range)
            .execute()
        )
        if "values" not in resp:
            return 0, 0
        rows = len(resp["values"])
        cols = max([len(row) for row in resp["values"]])
        return rows, cols
