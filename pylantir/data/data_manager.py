# pylantir/data/data_manager.py

import json

class DataManager:
    def __init__(self):
        self.data = {}
        self.regions = {}  # Dictionary to store regions by their coordinates

    def load_report(self, filename):
        try:
            with open(filename, 'r') as f:
                self.data = json.load(f)
            
            # Populate regions dictionary for quick access
            for region in self.data.get('regions', []):
                coordinates = region['coordinates']
                x = coordinates['x']
                y = coordinates['y']
                self.regions[(x, y)] = region

            print("Report loaded successfully.")
            print(f"Total regions: {len(self.regions)}")
        except Exception as e:
            print(f"Error loading report: {e}")

    def get_regions(self):
        return list(self.regions.values())

    def get_region(self, x, y):
        return self.regions.get((x, y))

    def get_faction_info(self):
        return {
            "name": self.data.get("name", "Unknown"),
            "number": self.data.get("number", "Unknown")
        }

    def get_date_info(self):
        date_info = self.data.get("date", {})
        return {
            "month": date_info.get("month", "Unknown"),
            "year": date_info.get("year", "Unknown")
        }

    def get_engine_info(self):
        engine_info = self.data.get("engine", {})
        return {
            "ruleset": engine_info.get("ruleset", "Unknown"),
            "ruleset_version": engine_info.get("ruleset_version", "Unknown"),
            "version": engine_info.get("version", "Unknown")
        }

    def get_attitudes(self):
        attitudes = self.data.get("attitudes", {})
        return {
            "default": attitudes.get("default", "Unknown").capitalize()
        }

    def get_administrative_settings(self):
        admin = self.data.get("administrative", {})
        return {
            "password_unset": admin.get("password_unset", False),
            "show_unit_attitudes": admin.get("show_unit_attitudes", False),
            "times_sent": admin.get("times_sent", True)
        }