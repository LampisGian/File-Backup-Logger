from backup_method import FolderBackupManager


class BackupConsoleApp:
    def __init__(self):
        self.backup_manager = FolderBackupManager()

    def show_existing_versions(self, source_path: str, destination_path: str) -> None:
        existing_versions = self.backup_manager.get_existing_versions(
            source_path,
            destination_path
        )

        if existing_versions:
            print("\nExisting versions for this folder:")
            for version in existing_versions:
                print(f"- v{version}")
            print()
        else:
            print("\nNo previous versions were found for this folder.\n")

    def run(self):
        print("=== File Backup Logger ===")

        source_path = input("Enter source folder path: ").strip()
        destination_path = input(
            "Enter destination folder path (press Enter for default Backups): "
        ).strip()

        try:
            self.show_existing_versions(source_path, destination_path)

            version = input("Enter backup version (press Enter for default v1): ").strip()

            backup_path = self.backup_manager.create_backup(
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