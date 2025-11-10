import json
import csv
from pathlib import Path
from fastapi.responses import FileResponse

LOG_FILE = Path("backend/logs/system_events.jsonl")
EXPORTS_DIR = Path("backend/exports")
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class Exporter:
    def __init__(self):
        self.filepath_json = EXPORTS_DIR / "events_export.json"
        self.filepath_csv = EXPORTS_DIR / "events_export.csv"

    def export_json(self):
        """Export logs as JSON array."""
        if not LOG_FILE.exists():
            return {"error": "No logs found to export."}

        data = []
        with LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    pass

        with self.filepath_json.open("w", encoding="utf-8") as out:
            json.dump(data, out, indent=4)

        return FileResponse(
            path=self.filepath_json,
            filename="smartcity_events.json",
            media_type="application/json"
        )

    def export_csv(self):
        """Export logs as CSV file."""
        if not LOG_FILE.exists():
            return {"error": "No logs found to export."}

        rows = []
        with LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except:
                    pass

        if not rows:
            return {"error": "No valid log entries found."}

        keys = sorted({k for r in rows for k in r.keys()})

        with self.filepath_csv.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

        return FileResponse(
            path=self.filepath_csv,
            filename="smartcity_events.csv",
            media_type="text/csv"
        )
