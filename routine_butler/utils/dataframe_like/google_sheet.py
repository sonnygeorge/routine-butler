import time
from typing import Any, List, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger

from routine_butler.utils.dataframe_like.base import DataframeLike
from routine_butler.utils.google.arbitrary_types import (
    GoogleDriveServiceObject,
    GoogleSheetsServiceObject,
)
from routine_butler.utils.google.drive_folder_manager import DriveFolderManager
from routine_butler.utils.google.g_suite_credentials_manager import (
    G_Suite_Credentials_Manager,
)

N_RETRIES = 13
SECONDS_BETWEEN_RETRIES = 3


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
        self.num_rows = None
        self.num_cols = None

    async def _get_drive_service_object(self) -> GoogleDriveServiceObject:
        """Builds and returns a Google Drive service object."""
        return build(
            "drive",
            "v3",
            credentials=await self.credentials_manager.get_credentials(),
        )

    async def _get_sheets_service_object(self) -> GoogleSheetsServiceObject:
        """Builds and returns a Google Sheets service object."""
        return build(
            "sheets",
            "v4",
            credentials=await self.credentials_manager.get_credentials(),
        )

    async def _ascertain_file_id(self) -> None:
        service = await self._get_drive_service_object()
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
        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.files().list(q=query, fields="files(id)").execute()
                )
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)

        if len(resp["files"]) == 0:
            raise FileNotFoundError(
                f"Spreadsheet file '{self.path}' not found " "in Google Drive."
            )
        else:
            self._file_id = resp["files"][0]["id"]

    async def _ascertain_sheet_name(
        self, service: GoogleSheetsServiceObject
    ) -> None:
        if self._sheet_name is not None:
            return

        if self._file_id is None:
            await self._ascertain_file_id()

        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.spreadsheets()
                    .get(spreadsheetId=self._file_id)
                    .execute()
                )
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)
        sheets = resp["sheets"]
        if len(sheets) != 1:
            raise Exception(
                f"Expected exactly one sheet in workbook '{self.path}'"
            )
        self._sheet_name = sheets[0]["properties"]["title"]

    async def get_row_at_idx(self, idx: int) -> List[Any]:
        """Returns the row at the given index as a one-dimensional list of values."""
        service = await self._get_sheets_service_object()
        await self._ascertain_sheet_name(service)

        sheet_range = f"Sheet1!{idx+1}:{idx+1}"
        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=self._file_id, range=sheet_range)
                    .execute()
                )
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)
        return resp["values"][0]

    async def get_all_data(self) -> List[List[Any]]:
        """Returns all rows in the sheet as a two-dimensional list of values."""
        service = await self._get_sheets_service_object()
        await self._ascertain_sheet_name(service)

        sheet_range = "Sheet1"
        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=self._file_id, range=sheet_range)
                    .execute()
                )
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)
        return resp["values"]

    async def _ascertain_spreadsheet_metadata(
        self, service: GoogleSheetsServiceObject
    ) -> None:
        if self._file_id is None:
            await self._ascertain_file_id()

        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.spreadsheets()
                    .get(spreadsheetId=self._file_id)
                    .execute()
                )
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)

        self._sheet_name = resp["properties"]["title"]
        properties = resp["sheets"][0]["properties"]
        self.num_rows = properties["gridProperties"]["rowCount"]
        self.num_cols = properties["gridProperties"]["columnCount"]

    async def shape(self) -> Tuple[int, int]:
        """Returns the number of populated rows and columns in the sheet."""
        service = await self._get_sheets_service_object()

        if self.num_rows is None or self.num_cols is None:
            await self._ascertain_spreadsheet_metadata(service)

        return self.num_rows, self.num_cols

    async def update_row_at_idx(self, idx: int, data: List[Any]) -> None:
        """Updates the row at the given index with the given data."""
        service = await self._get_sheets_service_object()
        await self._ascertain_sheet_name(service)

        sheet_range = f"Sheet1!{idx+1}:{idx+1}"
        body = {"values": [data]}
        for _ in range(N_RETRIES):
            try:
                resp = (
                    service.spreadsheets()
                    .values()
                    .update(
                        spreadsheetId=self._file_id,
                        range=sheet_range,
                        valueInputOption="RAW",
                        body=body,
                    )
                    .execute()
                )  # FIXME: type hints
                print(resp)
                break
            except HttpError as e:
                logger.warning(e)
                time.sleep(SECONDS_BETWEEN_RETRIES)
