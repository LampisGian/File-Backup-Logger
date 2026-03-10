from pathlib import Path
from datetime import datetime
import shutil

#This class is responsible for validating the source and destination paths for the backup operation.
# It checks weather the paths exist and if they are directories. If any of the checks fail, it raises an appropriate exception.
class PathValidator:
    def validate_source(self, source_path: str) -> Path:
        source = Path(source_path).expanduser().resolve()

        if not source.exists():
            raise FileNotFoundError(f"Source path does not exist: {source}")

        if not source.is_dir():
            raise NotADirectoryError(f"Source path is not a folder: {source}")

        return source

    def validate_destination(self, destination_path: str) -> Path:
        destination = Path(destination_path).expanduser().resolve()

        if not destination.exists():
            raise FileNotFoundError(f"Destination path does not exist: {destination}")

        if not destination.is_dir():
            raise NotADirectoryError(f"Destination path is not a folder: {destination}")

        return destination


#This class is responsible for constructing the backup folder name and path based on the source folder name, backup version, and current timestamp. 
# It generates a unique backup folder name to avoid overwriting existing backups and organizes backups in a structured manner.
class BackupNameBuilder:
    def build_backup_path(self, source: Path, destination: Path, version: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder_name = f"{source.name}_backup_v{version}_{timestamp}"
        return destination / backup_folder_name


#This class is responsible for managing the backup process. It uses the PathValidator to validate the source and destination paths, 
# and the BackupNameBuilder to construct the backup path. The create_backup method performs the actual backup operation by 
# copying the source folder to the constructed backup path using shutil.copytree.
class FolderBackupManager:
    def __init__(self):
        self.validator = PathValidator()
        self.name_builder = BackupNameBuilder()

    def create_backup(self, source_path: str, destination_path: str, version: str) -> Path:
        source = self.validator.validate_source(source_path)
        destination = self.validator.validate_destination(destination_path)

        backup_path = self.name_builder.build_backup_path(source, destination, version)

        shutil.copytree(source, backup_path)
        return backup_path