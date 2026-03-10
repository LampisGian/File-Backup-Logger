from pathlib import Path

#This class is responsible for validating the source and destination paths, as well as normalizing the version string.
class PathValidator:
    def validate_source(self, source_path: str) -> Path:
        cleaned_source_path = source_path.strip()

        if not cleaned_source_path:
            raise ValueError("Source path cannot be empty.")

        source = Path(cleaned_source_path).expanduser().resolve()

        if not source.exists():
            raise FileNotFoundError(f"Source path does not exist: {source}")

        if not source.is_dir():
            raise NotADirectoryError(f"Source path is not a folder: {source}")

        return source

    def validate_destination(self, destination_path: str) -> Path:
        cleaned_destination_path = destination_path.strip()

        if not cleaned_destination_path:
            destination = Path(__file__).resolve().parent.parent / "Backups"
            destination.mkdir(parents=True, exist_ok=True)
            return destination.resolve()

        destination = Path(cleaned_destination_path).expanduser().resolve()

        if not destination.exists():
            raise FileNotFoundError(f"Destination path does not exist: {destination}")

        if not destination.is_dir():
            raise NotADirectoryError(f"Destination path is not a folder: {destination}")

        return destination

#This class is responsible for checking existing backup versions and building backup folder names based on the source
class VersionManager:
    def normalize_version(self, version: str) -> str:
        cleaned_version = version.strip()

        if not cleaned_version:
            return "1"

        return cleaned_version.replace(" ", "-")

#This class is responsible for checking existing backup versions and building backup folder names based on the source folder, destination, and version. It also handles the creation of backups while ensuring that version conflicts are avoided.
class BackupPreparationManager:
    def __init__(self):
        self.path_validator = PathValidator()
        self.version_manager = VersionManager()

    def prepare_source(self, source_path: str):
        return self.path_validator.validate_source(source_path)

    def prepare_destination(self, destination_path: str):
        return self.path_validator.validate_destination(destination_path)

    def prepare_version(self, version: str) -> str:
        return self.version_manager.normalize_version(version)

    def prepare_backup_data(self, source_path: str, destination_path: str, version: str):
        source = self.prepare_source(source_path)
        destination = self.prepare_destination(destination_path)
        safe_version = self.prepare_version(version)
        return source, destination, safe_version