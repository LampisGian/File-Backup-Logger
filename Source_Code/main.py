from backup_method import FolderBackupManager
from zip_manager import ZipBackupManager


class BackupConsoleApp:
    def __init__(self):
        self.backup_manager = FolderBackupManager()
        self.zip_backup_manager = ZipBackupManager()

    def ask_backup_type(self) -> str:
        while True:
            print("\nChoose backup type:")
            print("1. Plain copy")
            print("2. ZIP backup")

            choice = input("Enter 1 or 2: ").strip()

            if choice == "1":
                return "plain"

            if choice == "2":
                return "zip"

            print("Invalid choice. Please enter 1 or 2.\n")

    def show_existing_backups(self, source_path: str, destination_path: str) -> None:
        existing_backups = self.backup_manager.get_existing_backups(
            source_path,
            destination_path
        )

        if existing_backups:
            print("\nExisting backups for this folder:")
            for backup_entry in existing_backups:
                print(f"- {backup_entry}")
            print()
        else:
            print("\nNo previous backups were found for this folder.\n")

    def run(self):
        print("=== File Backup Logger ===")

        source_path = input("Enter source folder path: ").strip()
        destination_path = input(
            "Enter destination folder path (press Enter for default Backups): "
        ).strip()

        try:
            backup_type = self.ask_backup_type()

            self.show_existing_backups(source_path, destination_path)

            version = input("Enter backup version (press Enter for default v1): ").strip()

            if backup_type == "plain":
                backup_path = self.backup_manager.create_backup(
                    source_path,
                    destination_path,
                    version
                )
            else:
                backup_path = self.zip_backup_manager.create_zip_backup(
                    source_path,
                    destination_path,
                    version
                )

            print("\nBackup completed successfully.")
            print(f"Backup created at: {backup_path}")

        except FileNotFoundError as error:
            print(f"File/Folder Error: {error}")

        except NotADirectoryError as error:
            print(f"Directory Error: {error}")

        except PermissionError as error:
            print(f"Permission Error: {error}")

        except ValueError as error:
            print(f"Validation Error: {error}")

        except Exception as error:
            print(f"Unexpected Error: {error}")


if __name__ == "__main__":
    app = BackupConsoleApp()
    app.run()