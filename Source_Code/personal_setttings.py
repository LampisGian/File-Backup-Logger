import json
from pathlib import Path

#This class is responsible for managing the personal settings of the useer and saving them in the local .json file named config 
#also is used to load the settings from the config file and update them when the user changes them in the GUI or when a backup is made 
# successfully to keep track of the last used source and destination folders and the last version of the backup.
class ConfigManager:
    def __init__(self):
        self.config_file = Path(__file__).resolve().parent / "config.json"
        self.default_config = {
            "preferences": {
                "default_destination_folder": "",
                "default_backup_type": "folder",
                "backup_interval": "manual"
            },
            "last_used": {
                "last_source_folder": "",
                "last_destination_folder": "",
                "last_version": ""
            },
            "backup_state": {
                "last_successful_backup_time": ""
            }
        }

    def load_config(self) -> dict:
        if not self.config_file.exists():
            self.save_config(self.default_config)
            return self.default_config.copy()

        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                config_data = json.load(file)

            return self._merge_with_defaults(config_data)

        except (json.JSONDecodeError, OSError):
            self.save_config(self.default_config)
            return self.default_config.copy()

    def save_config(self, config_data: dict) -> None:
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(config_data, file, indent=4)

    def _merge_with_defaults(self, config_data: dict) -> dict:
        merged_config = {
            "preferences": {
                "default_destination_folder": config_data.get("preferences", {}).get(
                    "default_destination_folder",
                    self.default_config["preferences"]["default_destination_folder"]
                ),
                "default_backup_type": config_data.get("preferences", {}).get(
                    "default_backup_type",
                    self.default_config["preferences"]["default_backup_type"]
                ),
                "backup_interval": config_data.get("preferences", {}).get(
                    "backup_interval",
                    self.default_config["preferences"]["backup_interval"]
                )
            },
            "last_used": {
                "last_source_folder": config_data.get("last_used", {}).get(
                    "last_source_folder",
                    self.default_config["last_used"]["last_source_folder"]
                ),
                "last_destination_folder": config_data.get("last_used", {}).get(
                    "last_destination_folder",
                    self.default_config["last_used"]["last_destination_folder"]
                ),
                "last_version": config_data.get("last_used", {}).get(
                    "last_version",
                    self.default_config["last_used"]["last_version"]
                )
            },
            "backup_state": {
                "last_successful_backup_time": config_data.get("backup_state", {}).get(
                    "last_successful_backup_time",
                    self.default_config["backup_state"]["last_successful_backup_time"]
                )
            }
        }

        return merged_config

    def get_preferences(self) -> dict:
        config_data = self.load_config()
        return config_data["preferences"]

    def get_last_used(self) -> dict:
        config_data = self.load_config()
        return config_data["last_used"]

    def get_backup_state(self) -> dict:
        config_data = self.load_config()
        return config_data["backup_state"]

    def update_preferences(
        self,
        default_destination_folder: str | None = None,
        default_backup_type: str | None = None,
        backup_interval: str | None = None
    ) -> None:
        config_data = self.load_config()

        if default_destination_folder is not None:
            config_data["preferences"]["default_destination_folder"] = default_destination_folder

        if default_backup_type is not None:
            config_data["preferences"]["default_backup_type"] = default_backup_type

        if backup_interval is not None:
            config_data["preferences"]["backup_interval"] = backup_interval

        self.save_config(config_data)

    def update_last_used(
        self,
        last_source_folder: str | None = None,
        last_destination_folder: str | None = None,
        last_version: str | None = None
    ) -> None:
        config_data = self.load_config()

        if last_source_folder is not None:
            config_data["last_used"]["last_source_folder"] = last_source_folder

        if last_destination_folder is not None:
            config_data["last_used"]["last_destination_folder"] = last_destination_folder

        if last_version is not None:
            config_data["last_used"]["last_version"] = last_version

        self.save_config(config_data)

    def update_last_successful_backup_time(self, backup_time: str) -> None:
        config_data = self.load_config()
        config_data["backup_state"]["last_successful_backup_time"] = backup_time
        self.save_config(config_data)

    def reset_to_defaults(self) -> None:
        self.save_config(self.default_config.copy())