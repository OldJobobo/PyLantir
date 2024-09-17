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
                
                # Check for missing fields in the hex data and log a warning
                missing_fields = []
                if 'terrain' not in region:
                    missing_fields.append('terrain')
                if 'population' not in region:
                    missing_fields.append('population')
                if 'products' not in region:
                    missing_fields.append('products')
                if 'markets' not in region:
                    missing_fields.append('markets')
                if missing_fields:
                    print(f"Region at ({x}, {y}) is missing fields: {', '.join(missing_fields)}")

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