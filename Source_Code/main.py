from backup_method import FolderBackupManager


class BackupConsoleApp:
    def __init__(self):
        self.backup_manager = FolderBackupManager()

    def ask_version_until_valid(self, source_path: str, destination_path: str) -> str:
        while True:
            existing_versions = self.backup_manager.get_existing_versions(
                source_path,
                destination_path
            )

            if existing_versions:
                print("\nExisting versions for this folder:")
                for version in existing_versions:
                    print(f"- v{version}")
                print()

                version = input("Enter a new backup version: ").strip()
            else:
                print("\nNo previous versions were found for this folder.")
                version = input("Enter backup version (press Enter for default v1): ").strip()

            try:
                if self.backup_manager.is_version_available(
                    source_path,
                    destination_path,
                    version
                ):
                    return version

                print("\nThis version already exists. Please enter a different version.\n")

            except Exception as error:
                print(f"\nError while checking version: {error}\n")

    def run(self):
        print("=== File Backup Logger ===")

        source_path = input("Enter source folder path: ").strip()
        destination_path = input(
            "Enter destination folder path (press Enter for default Backups): "
        ).strip()

        try:
            version = self.ask_version_until_valid(source_path, destination_path)

            backup_path = self.backup_manager.create_backup(
                source_path,
                destination_path,
                version
            )

            print("\nBackup completed successfully.")
            print(f"Backup created at: {backup_path}")

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    app = BackupConsoleApp()
    app.run()