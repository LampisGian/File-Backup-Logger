from pathlib import Path
from datetime import datetime
import shutil
import re
import time

from general_managers import BackupPreparationManager
from log_manager import BackupLogger


class BackupVersionChecker:
    def get_existing_backups(self, source: Path, destination: Path) -> list[str]:
        backup_entries = []
        prefix = f"{source.name}_backup_"

        for item in destination.iterdir():
            item_name = item.name

            if not item_name.startswith(prefix):
                continue

            match = re.search(r"_v(.+?)(\.zip)?$", item_name)
            if not match:
                continue

            version = match.group(1)

            if item.is_dir():
                backup_entries.append(f"v{version} (folder)")
            elif item.is_file() and item.suffix == ".zip":
                backup_entries.append(f"v{version} (zip)")

        return sorted(set(backup_entries))


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

    def count_files(self, source: Path) -> int:
        return sum(1 for item in source.rglob("*") if item.is_file())

    def get_existing_backups(self, source_path: str, destination_path: str) -> list[str]:
        source = self.preparation_manager.prepare_source(source_path)
        destination = self.preparation_manager.prepare_destination(destination_path)
        return self.version_checker.get_existing_backups(source, destination)

    def get_existing_versions(self, source_path: str, destination_path: str) -> list[str]:
        source = self.preparation_manager.prepare_source(source_path)
        destination = self.preparation_manager.prepare_destination(destination_path)
        return self.version_checker.get_existing_versions(source, destination)

    def create_backup(self, source_path: str, destination_path: str, version: str):
        source = "UNKNOWN"
        destination = "UNKNOWN"
        safe_version = version.strip() if version.strip() else "1"
        file_count = 0
        start_time = time.time()

        try:
            source_obj, destination_obj, safe_version = self.preparation_manager.prepare_backup_data(
                source_path,
                destination_path,
                version
            )

            source = str(source_obj)
            destination = str(destination_obj)
            file_count = self.count_files(source_obj)

            backup_path = self.name_builder.build_backup_path(
                source_obj,
                destination_obj,
                safe_version
            )

            shutil.copytree(source_obj, backup_path)

            duration = time.time() - start_time

            self.logger.write_log(
                status="SUCCESS",
                source=source,
                destination=destination,
                version=safe_version,
                file_count=file_count,
                duration=duration,
                message=f"Folder backup created successfully at {backup_path}"
            )

            return backup_path

        except PermissionError:
            duration = time.time() - start_time

            self.logger.write_log(
                status="FAILED",
                source=source,
                destination=destination,
                version=safe_version,
                file_count=file_count,
                duration=duration,
                message="Permission denied during backup process."
            )
            raise PermissionError("Permission denied. Check folder access permissions.")

        except Exception as error:
            duration = time.time() - start_time

            self.logger.write_log(
                status="FAILED",
                source=source,
                destination=destination,
                version=safe_version,
                file_count=file_count,
                duration=duration,
                message=str(error)
            )
            raise