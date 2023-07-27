"""Ad-hoc script to verify the expected functionality of the GoogleSheets class

NOTE: It is assumed that this file exists and has the expected data and nothing else."""

from routine_butler.configs import G_SUITE_CREDENTIALS_MANAGER
from routine_butler.utils.dataframe_like import GoogleSheet

ROOT_FOLDER_NAME = "ROUTINE-BUTLER-TEST-FOLDER"
FILE_PATH = "TEST"
EXPECTED_DATA_IN_FIRST_ROW = ["1", "2", "3"]
EXPECTED_DATA_IN_FIFTH_ROW = ["1", "2", "3", "4"]


def google_sheet_integration_test(
    root_folder_name: str, file_path: str
) -> None:
    google_drive_folder = GoogleSheet(
        root_folder_name=root_folder_name,
        path=file_path,
        credentials_manager=G_SUITE_CREDENTIALS_MANAGER,
    )
    row = google_drive_folder.get_row_at_idx(0)
    assert row == EXPECTED_DATA_IN_FIRST_ROW
    print("✅: First row is as expected")
    row = google_drive_folder.get_row_at_idx(4)
    assert row == EXPECTED_DATA_IN_FIFTH_ROW
    print("✅: Fifth row is as expected")
    assert google_drive_folder.shape() == (5, 4)
    print("✅: Shape is as expected")


if __name__ == "__main__":
    google_sheet_integration_test(
        root_folder_name=ROOT_FOLDER_NAME, file_path=FILE_PATH
    )
