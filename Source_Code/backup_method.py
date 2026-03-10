from pathlib import Path
from datetime import datetime
import shutil
import re
from general_managers import BackupPreparationManager

#This class is responsible for checking existing backup versions and building backup folder names based on the source 
#folder, destination, and version. It also handles the creation of backups while ensuring that version conflicts are avoided.
class BackupVersionChecker:
    def get_existing_versions(self, source: Path, destination: Path) -> list[str]:
        versions = []
        prefix = f"{source.name}_backup_"
        version_pattern = re.compile(r"_v(.+)$")

        for item in destination.iterdir():
            if not item.is_dir():
                continue

            if not item.name.startswith(prefix):
                continue

            match = version_pattern.search(item.name)
            if match:
                versions.append(match.group(1))

        return sorted(set(versions))

    def version_exists(self, source: Path, destination: Path, version: str) -> bool:
        return version in self.get_existing_versions(source, destination)

#This class is responsible for building the backup folder name based on the source folder, destination, and version. 
#It uses the current timestamp to ensure that each backup has a unique name, even if the same version is used multiple times.
class BackupNameBuilder:
    def build_backup_path(self, source: Path, destination: Path, version: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder_name = f"{source.name}_backup_{timestamp}_v{version}"
        return destination / backup_folder_name

#This class is responsible for managing the backup process, including validating the source and destination paths, 
# checking for existing versions, and creating the backup. It uses the BackupPreparationManager to prepare the 
# paths and the BackupVersionChecker to ensure that version conflicts are avoided.
class FolderBackupManager:
    def __init__(self):
        self.preparation_manager = BackupPreparationManager()
        self.version_checker = BackupVersionChecker()
        self.name_builder = BackupNameBuilder()

    def get_existing_versions(self, source_path: str, destination_path: str) -> list[str]:
        source = self.preparation_manager.prepare_source(source_path)
        destination = self.preparation_manager.prepare_destination(destination_path)
        return self.version_checker.get_existing_versions(source, destination)

    def is_version_available(self, source_path: str, destination_path: str, version: str) -> bool:
        source, destination, safe_version = self.preparation_manager.prepare_backup_data(
            source_path,
            destination_path,
            version
        )
        return not self.version_checker.version_exists(source, destination, safe_version)

    def create_backup(self, source_path: str, destination_path: str, version: str):
        source, destination, safe_version = self.preparation_manager.prepare_backup_data(
            source_path,
            destination_path,
            version
        )

        if self.version_checker.version_exists(source, destination, safe_version):
            raise ValueError(
                f"Version '{safe_version}' already exists for folder '{source.name}'."
            )

        backup_path = self.name_builder.build_backup_path(source, destination, safe_version)
        shutil.copytree(source, backup_path)
        return backup_path