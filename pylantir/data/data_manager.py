# pylantir/data/data_manager.py

import json
import os

class DataManager:
    def __init__(self):
        self.report_data = {}  # This will store the entire report
        self.persistent_map_data = {}
        self.regions = {}

    def load_report(self, filename):
        """
        Load a JSON report file and process its data.

        This method reads a JSON file specified by the filename, stores its contents
        in self.report_data, and then processes this data using the _process_report_data method.

        Args:
            filename (str): The path to the JSON report file to be loaded.

        Raises:
            Exception: If there's an error while reading or processing the file.

        Returns:
            None
        """
        try:
            with open(filename, 'r') as f:
                self.report_data = json.load(f)
            self._process_report_data()
            print("Report loaded successfully.")
        except Exception as e:
            print(f"Error loading report: {e}")

    def _process_report_data(self):
        self.regions.clear()
        for region in self.report_data.get('regions', []):
            coordinates = region['coordinates']
            x, y = coordinates['x'], coordinates['y']
            self.regions[(x, y)] = region
            self._merge_persistent_data(x, y)

    def _merge_persistent_data(self, x, y):
        if (x, y) in self.persistent_map_data:
            self.regions[(x, y)].update(self.persistent_map_data[(x, y)])

    def save_persistent_data(self, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(self.persistent_map_data, f)
            print("Persistent data saved successfully.")
        except Exception as e:
            print(f"Error saving persistent data: {e}")

    def load_persistent_data(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    self.persistent_map_data = json.load(f)
                print("Persistent data loaded successfully.")
            except Exception as e:
                print(f"Error loading persistent data: {e}")
        else:
            print("No persistent data file found. Starting with empty data.")

    def update_region(self, x, y, data):
        if (x, y) in self.regions:
            self.regions[(x, y)].update(data)
            self.persistent_map_data[(x, y)] = self.persistent_map_data.get((x, y), {})
            self.persistent_map_data[(x, y)].update(data)

    def get_regions(self):
        return list(self.regions.values())

    def get_region(self, x, y):
        return self.regions.get((x, y))

    def get_faction_info(self):
        return {
            "name": self.report_data.get("name", "Unknown"),
            "number": self.report_data.get("number", "Unknown")
        }

    def get_date_info(self):
        date_info = self.report_data.get("date", {})
        return {
            "month": date_info.get("month", "Unknown"),
            "year": date_info.get("year", "Unknown")
        }

    def get_engine_info(self):
        engine_info = self.report_data.get("engine", {})
        return {
            "ruleset": engine_info.get("ruleset", "Unknown"),
            "ruleset_version": engine_info.get("ruleset_version", "Unknown"),
            "version": engine_info.get("version", "Unknown")
        }

    def get_attitudes(self):
        attitudes = self.report_data.get("attitudes", {})
        return {
            "default": attitudes.get("default", "Unknown").capitalize()
        }

    def get_administrative_settings(self):
        admin = self.report_data.get("administrative", {})
        return {
            "password_unset": admin.get("password_unset", False),
            "show_unit_attitudes": admin.get("show_unit_attitudes", False),
            "times_sent": admin.get("times_sent", True)
        }
    
    def get_markets(self, x, y):
        """
        Retrieve the markets for the region at coordinates (x, y).

        Parameters:
            x (int): The x-coordinate of the region.
            y (int): The y-coordinate of the region.

        Returns:
            dict: A dictionary containing 'for_sale' and 'wanted' markets.
                  Returns None if the region does not exist or has no markets.
        """
        region = self.get_region(x, y)
        if not region:
            print(f"No region found at coordinates ({x}, {y}).")
            return None

        markets = region.get('markets')
        if not markets:
            print(f"Region at ({x}, {y}) has no markets data.")
            return None

        return markets
    
    def get_settlement(self, x, y):
        """
        Retrieve the settlement information for the region at coordinates (x, y).

        Parameters:
            x (int): The x-coordinate of the region.
            y (int): The y-coordinate of the region.

        Returns:
            dict: A dictionary containing settlement details (e.g., name, size).
                  Returns None if the region does not exist or has no settlement.
        """
        region = self.get_region(x, y)
        if not region:
            print(f"No region found at coordinates ({x}, {y}).")
            return None

        settlement = region.get('settlement')
        if not settlement:
            print(f"Region at ({x}, {y}) has no settlement data.")
            return None

        return settlement