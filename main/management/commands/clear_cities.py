from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Delete extra columns from cities.txt, keeping only place, link, and station type."
    )

    def handle(self, *args, **kwargs):
        try:
            delimiter = settings.CSV_DELIMITER
            static_root = str(settings.STATIC_DATA_PATH)
            if not static_root.endswith("/"):
                static_root += "/"

            with open(f"{static_root}cities.txt", encoding="utf-8") as file:
                lines: list[str] = file.readlines()
            for i, line in enumerate(lines):
                parts = line.split(delimiter)[0:3]
                if parts[2] == "0":
                    parts[2] = "0\n"
                lines[i] = parts

            with open(f"{static_root}cities.txt", "w", encoding="utf-8") as file:
                for parts in lines:
                    file.write(delimiter.join(map(str, parts)))
        except Exception as e:
            self.stdout.write(f"Error is:\n{e}")
        else:
            self.stdout.write("Cities was cleared to: place, link, type.")
