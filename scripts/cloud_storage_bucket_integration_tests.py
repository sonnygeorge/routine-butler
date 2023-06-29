"""Ad-hoc script to verify the expected functionality of CloudStorageBucket classes
generally & more specifically, the GoogleDriveFolder class."""


import os
import shutil
from typing import List

from routine_butler.configs import GDRIVE_CREDENTIALS_PATH
from routine_butler.utils.cloud_storage_bucket.base import (
    CloudStorageBucket,
    CloudStorageBucketItem,
)
from routine_butler.utils.cloud_storage_bucket.google_drive_folder import (
    GoogleDriveFolder,
)


def cloud_storage_bucket_integration_test(
    cloud_storage_bucket: CloudStorageBucket,
) -> None:
    def get_subpaths(path: str) -> List[str]:
        subpaths = []
        split_path = path.split("/")
        current_path = ""
        for subpath in split_path[:-1]:
            current_path += subpath + "/"
            subpaths.append(current_path.rstrip("/"))
        return subpaths

    def cloud_storage_bucket_path_test(
        cloud_storage_bucket: CloudStorageBucket,
        path: str,
    ) -> None:
        """Helper function to test the upload, list, download and delete methods of a
        CloudStorageBucket object.
        """
        root_items_pre_testing = cloud_storage_bucket.list()
        root_item_names_pre_testing = [x.name for x in root_items_pre_testing]

        assert (
            path.split("/")[-1] not in root_item_names_pre_testing
        ), "Please remove traces of this path from the cloud storage bucket"

        print(f"Testing {path} with object {cloud_storage_bucket}")
        subpaths = get_subpaths(path)
        file_name = os.path.basename(path)
        parent_dir_path = subpaths[-1] if len(subpaths) > 0 else None

        # Create file (& all subpaths) locally temporarily
        for subpath in subpaths:
            if not os.path.exists(subpath):
                os.mkdir(subpath)
        if os.path.isdir(path):
            shutil.rmtree(path)
        with open(path, "w"):
            pass

        # Upload file
        cloud_storage_bucket.upload(
            local_path=path, remote_dir_path=parent_dir_path
        )

        # List what's currently in parent directory
        parent_dir_items = cloud_storage_bucket.list(
            remote_path=parent_dir_path
        )

        # Assert that the return value is a list of CloudStorageBucketItem objects
        assert isinstance(parent_dir_items, list)
        assert len(parent_dir_items) > 0
        chk = [isinstance(x, CloudStorageBucketItem) for x in parent_dir_items]
        assert all(chk)
        print(" - ✅ list method returns correct type")

        # Assert that the file is in the bucket at the correct path
        items_w_name = [x for x in parent_dir_items if x.name == file_name]
        assert len(items_w_name) == 1
        assert all([x.is_dir is False for x in items_w_name])
        print(" - ✅ file is in bucket at correct path & is_dir is False")

        # Download file
        cloud_storage_bucket.download(remote_path=path, local_path=path)

        # Delete remnants
        dirs_to_delete = get_subpaths(path)[::-1]

        # Assert that deleting a dir before deleting its contents raises an error
        error_was_raised = False
        if parent_dir_path is not None:
            try:
                cloud_storage_bucket.delete(parent_dir_path)
            except:  # noqa
                error_was_raised = True
                print(
                    " - ✅ deleting a dir before its contents raises an error"
                )
            if not error_was_raised:
                raise AssertionError(
                    "Deleting a dir before its contents should raise an error"
                )

        # Delete file and all subpaths & assert that they're gone
        cloud_storage_bucket.delete(path)
        assert len(cloud_storage_bucket.list(remote_path=parent_dir_path)) == 0
        for dir_path in dirs_to_delete:
            assert len(cloud_storage_bucket.list(remote_path=dir_path)) == 0
            cloud_storage_bucket.delete(dir_path)
        root_items = cloud_storage_bucket.list()
        if len(dirs_to_delete) > 0:
            assert len([x.name == dirs_to_delete[-1] for x in root_items]) == 0
        print(" - ✅ delete method works as expected")

        # Assert that the root items are the same before and after testing
        assert root_items_pre_testing == root_items
        print(" - ✅ bucket's root items are the same before & after testing")

        # Delete local temp file
        os.remove(path)
        for dir_path in dirs_to_delete:
            os.rmdir(dir_path)

        print(" - ✅ all tests passed")

    arbitrary_str = "Ln3P(9!dF#2"  # something not found locally or in bucket
    paths_to_test = [
        f"{arbitrary_str}",
        f"{arbitrary_str}/{arbitrary_str}",
        f"{arbitrary_str}/{arbitrary_str}/{arbitrary_str}",
    ]

    for path in paths_to_test:
        cloud_storage_bucket_path_test(cloud_storage_bucket, path)


if __name__ == "__main__":
    google_drive_folder = GoogleDriveFolder(
        folder_name="ROUTINE-BUTLER-TEST-FOLDER",
        credentials_file_path=GDRIVE_CREDENTIALS_PATH,
    )

    cloud_storage_bucket_integration_test(
        cloud_storage_bucket=google_drive_folder
    )
