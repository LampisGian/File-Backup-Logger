from pathlib import Path
from datetime import datetime
import shutil
import re

from general_managers import BackupPreparationManager
from log_manager import BackupLogger


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
        self.logger = BackupLogger()

    def get_existing_versions(self, source_path: str, destination_path: str) -> list[str]:
        source = self.preparation_manager.prepare_source(source_path)
        destination = self.preparation_manager.prepare_destination(destination_path)
        return self.version_checker.get_existing_versions(source, destination)

    def create_backup(self, source_path: str, destination_path: str, version: str):
        source = "UNKNOWN"
        destination = "UNKNOWN"
        safe_version = version.strip() if version.strip() else "1"

        try:
            source_obj, destination_obj, safe_version = self.preparation_manager.prepare_backup_data(
                source_path,
                destination_path,
                version
            )

            source = str(source_obj)
            destination = str(destination_obj)

            backup_path = self.name_builder.build_backup_path(
                source_obj,
                destination_obj,
                safe_version
            )

            shutil.copytree(source_obj, backup_path)

            self.logger.write_log(
                status="SUCCESS",
                source=source,
                destination=destination,
                version=safe_version,
                message=f"Backup created successfully at {backup_path}"
            )

            return backup_path

        except PermissionError:
            self.logger.write_log(
                status="FAILED",
                source=source,
                destination=destination,
                version=safe_version,
                message="Permission denied during backup process."
            )
            raise PermissionError("Permission denied. Check folder access permissions.")

        except Exception as error:
            self.logger.write_log(
                status="FAILED",
                source=source,
                destination=destination,
                version=safe_version,
                message=str(error)
            )
            raise