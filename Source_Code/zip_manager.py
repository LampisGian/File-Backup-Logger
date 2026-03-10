from pathlib import Path
from datetime import datetime
import zipfile

from general_managers import BackupPreparationManager
from log_manager import BackupLogger


class ZipBackupNameBuilder:
    def build_zip_backup_path(self, source: Path, destination: Path, version: str) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_file_name = f"{source.name}_backup_{timestamp}_v{version}.zip"
        return destination / zip_file_name


class ZipBackupManager:
    def __init__(self):
        self.preparation_manager = BackupPreparationManager()
        self.name_builder = ZipBackupNameBuilder()
        self.logger = BackupLogger()

    def create_zip_backup(self, source_path: str, destination_path: str, version: str) -> Path:
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

            zip_backup_path = self.name_builder.build_zip_backup_path(
                source_obj,
                destination_obj,
                safe_version
            )

            with zipfile.ZipFile(zip_backup_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in source_obj.rglob("*"):
                    if file_path.is_file():
                        archive_name = file_path.relative_to(source_obj.parent)
                        zip_file.write(file_path, arcname=archive_name)

            self.logger.write_log(
                status="SUCCESS",
                source=source,
                destination=destination,
                version=safe_version,
                message=f"ZIP backup created successfully at {zip_backup_path}"
            )

            return zip_backup_path

        except PermissionError:
            self.logger.write_log(
                status="FAILED",
                source=source,
                destination=destination,
                version=safe_version,
                message="Permission denied during ZIP backup process."
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