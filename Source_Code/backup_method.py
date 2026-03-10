from pathlib import Path
from datetime import datetime
import shutil
import re
from general_managers import BackupPreparationManager


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


class BackupNameBuilder:
    def build_backup_path(self, source: Path, destination: Path, version: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder_name = f"{source.name}_backup_{timestamp}_v{version}"
        return destination / backup_folder_name


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