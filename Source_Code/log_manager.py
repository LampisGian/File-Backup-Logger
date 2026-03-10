from pathlib import Path
from datetime import datetime


class LogFormatter:
    def format_log_entry(
        self,
        backup_time: str,
        status: str,
        source: str,
        destination: str,
        version: str,
        message: str
    ) -> str:
        return (
            f"[{backup_time}] "
            f"STATUS={status} | "
            f"SOURCE={source} | "
            f"DESTINATION={destination} | "
            f"VERSION=v{version} | "
            f"MESSAGE={message}\n"
        )


class BackupLogger:
    def __init__(self):
        self.logs_folder = Path(__file__).resolve().parent / "logs"
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_folder / "backup.log"
        self.formatter = LogFormatter()

    def write_log(
        self,
        status: str,
        source: str,
        destination: str,
        version: str,
        message: str
    ) -> None:
        backup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = self.formatter.format_log_entry(
            backup_time=backup_time,
            status=status,
            source=source,
            destination=destination,
            version=version,
            message=message
        )

        with open(self.log_file, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)