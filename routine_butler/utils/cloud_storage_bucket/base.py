from os import PathLike
from typing import List, Optional, Protocol

from pydantic import BaseModel


class CloudStorageBucketItem(BaseModel):
    name: str
    is_dir: bool


class CloudStorageBucket(Protocol):
    """Protocol for interacting with a cloud storage bucket."""

    def list(
        self, remote_path: Optional[str] = None
    ) -> List[CloudStorageBucketItem]:
        """Attempts to list all files (non-recursively) in the `remote_path` on the
        bucket (must be a path to a directory). If remote_path is None, lists all
        items (files & directories) in the bucket's root.
        """
        ...

    def upload(
        self, local_path: PathLike, remote_dir_path: Optional[str] = None
    ) -> None:
        """Attempts to upload the file at `local_path` to the `remote_dir_path` on the
        bucket. If no `remote_dir_path` is provided, uploads the file to the bucket's
        root.
        """
        ...

    def download(self, local_path: PathLike, remote_path: str) -> None:
        """Attempts to download the file at `remote_path` on the bucket (must be a path
        to a file) to the `local_path`.
        """
        ...

    def delete(self, remote_path: str) -> bool:
        """Attempts to delete the file at `remote_path` on the bucket (must be a path to
        either a file or an empty directory).
        """
        ...

    def validate_connection(self) -> bool:
        """Attempts to validate the connection to the bucket."""
        ...
