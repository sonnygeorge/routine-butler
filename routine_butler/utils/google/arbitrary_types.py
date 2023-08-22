from typing import Optional, Protocol

from googleapiclient.http import MediaFileUpload

# NOTE: Google API "Resources" are dynamically generated and thus, not typed


class GoogleDrivePendingOperation(Protocol):
    """Arbitrary protocol for type-hinting the Google Drive pending operation object"""

    def execute(self) -> dict:
        ...


class GoogleDriveFilesObject(Protocol):
    """Arbitrary protocol for type-hinting the Google Drive files object"""

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
    """Arbitrary protocol for type-hinting the Google Drive service object"""

    def files(self) -> GoogleDriveFilesObject:
        ...


class GoogleSheetsValuesObject(Protocol):
    """Arbitrary protocol for type-hinting the Google Sheets values object"""

    def get(
        self, spreadsheetId: str, range: str
    ) -> GoogleDrivePendingOperation:
        ...

    def update(
        self,
        spreadsheetId: str,
        range: str,
        body: dict,
        valueInputOption: str,
    ) -> GoogleDrivePendingOperation:
        ...


class GoogleSheetsSpreadsheetsObject(Protocol):
    """Arbitrary protocol for type-hinting the Google Sheets spreadsheets object"""

    def get(self, spreadsheetId: str) -> GoogleDrivePendingOperation:
        ...

    def values(self) -> GoogleSheetsValuesObject:
        ...


class GoogleSheetsServiceObject(Protocol):
    """Arbitrary protocol for type-hinting the Google Sheets service object"""

    def spreadsheets(self) -> GoogleSheetsSpreadsheetsObject:
        ...

    def values(self) -> GoogleSheetsValuesObject:
        ...
