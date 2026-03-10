from backup_method import FolderBackupManager

#This class serves as the main entry point for the console application. It interacts with the user to gather input for the source folder,
# destination folder, and backup version.
class BackupConsoleApp:
    def __init__(self):
        self.backup_manager = FolderBackupManager()

    def run(self):
        print("=== File Backup Logger - Step 1 & 2 ===")

        source_path = input("Enter source folder path: ").strip()
        destination_path = input("Enter destination folder path: ").strip()
        version = input("Enter backup version: ").strip()

        try:
            backup_path = self.backup_manager.create_backup(source_path, destination_path, version)
            print("Backup completed successfully.")
            print(f"Backup created at: {backup_path}")

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    app = BackupConsoleApp()
    app.run()