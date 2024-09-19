# pylantir/data/data_manager.py

import json
import os

class DataManager:
    def __init__(self):
        self.report_data = {}  # This will store the entire report
        self.persistent_map_data = {}
        self.regions = {}
        self.events = []  # Add this line to store events

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
            with open(filename, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            self._process_report_data()
            print("Report loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            print(f"Error loading report: {e}")
            raise  # Re-raise the exception after logging

    def _process_report_data(self):
        self.regions.clear()
        for region in self.report_data.get('regions', []):
            coordinates = region['coordinates']
            x, y = coordinates['x'], coordinates['y']
            self.regions[(x, y)] = region
            self._merge_persistent_data(x, y)
        
        # Process events
        self.events = self.report_data.get('events', [])  # Add this line

    def _merge_persistent_data(self, x, y):
        if (x, y) in self.persistent_map_data:
            self.regions[(x, y)].update(self.persistent_map_data[(x, y)])

    def save_persistent_data(self, filename):
        """
        Save persistent map data to a JSON file.

        Args:
            filename (str): The path to save the JSON file.

        Raises:
            Exception: If there's an error while saving the file.
    """
        try:
            # Convert tuple keys to strings
            serializable_data = {f"{k[0]},{k[1]}": v for k, v in self.persistent_map_data.items()}
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=4)
            print("Persistent data saved successfully.")
        except (IOError, PermissionError, json.JSONDecodeError, TypeError) as e:
            print(f"Error saving persistent data: {e}")

    def load_persistent_data(self, filename):
        """
        Load persistent data from a JSON file.

        Args:
            filename (str): Path to the JSON file.

        Raises:
            Exception: If there's an error while loading the file.
        """
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Convert string keys back to tuples
                self.persistent_map_data = {tuple(map(int, k.split(','))): v for k, v in data.items()}
                self.regions = self.persistent_map_data
                print("Persistent data loaded successfully.")
            except Exception as e:
                print(f"Error loading persistent data: {e}")
        else:
            print("No persistent data file found. Starting with empty data.")
            self.persistent_map_data = {}

    def update_region(self, x, y, data):
        """
        Update a region's data at the given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.
            data (dict): New data to update the region with.
        """
        key = (x, y)
        if key in self.regions:
            self.regions[key].update(data)
            self.persistent_map_data[key] = self.persistent_map_data.get(key, {})
            self.persistent_map_data[key].update(data)

    def get_regions(self):
        """Return a list of all region data."""
        return list(self.regions.values())

    def get_region(self, x, y):
        """
        Retrieve the region data for given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.

        Returns:
            dict: Region data or None if not found.
        """
        return self.regions.get((x, y))

    def get_faction_info(self):
        """
        Retrieve faction information from the report data.

        Returns:
            dict: Faction name and number, with 'Unknown' as default.
        """
        return {
            "name": self.report_data.get("name", "Unknown"),
            "number": self.report_data.get("number", "Unknown")
        }

    def get_date_info(self):
        """
        Retrieve date information from the report data.

        Returns:
            dict: Month and year, with 'Unknown' as default.
        """
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

    def save_persistent_data_to_file(self, filename):
        """
        Save the persistent map data to a JSON file specified by the filename.

        Args:
            filename (str): The path to the JSON file where data will be saved.
        """
        if filename:
            try:
                self.save_persistent_data(filename)
                print(f"Persistent data saved to {filename}.")
            except Exception as e:
                print(f"Error saving persistent data: {e}")
        else:
            print("No filename provided. Save operation cancelled.")

    def load_persistent_data_from_file(self, filename):
        """
        Load persistent map data from a JSON file specified by the filename.
        Clears all current loaded data and loads the saved data from the file.

        Args:
            filename (str): The path to the JSON file from which data will be loaded.
        """
        if filename:
            try:
                self.persistent_map_data.clear()
                self.regions.clear()
                self.load_persistent_data(filename)
                self._process_report_data()
                print(f"Persistent data loaded from {filename}.")

                # After loading, update the hex map and main window if necessary
                # For example:
                # if hasattr(self, 'hex_map'):
                #     self.hex_map.update_map(self.regions)
                # if hasattr(self, 'main_window'):
                #     self.main_window.refresh()

            except Exception as e:
                print(f"Error loading persistent data: {e}")
        else:
            print("No filename provided. Load operation cancelled.")

    def get_events(self):
        """Return the list of events from the report."""
        return self.events

    def get_events_for_region(self, x, y):
        """
        Return events specific to a region.
        This method filters events that have a 'region' key matching the given coordinates.
        """
        return [event for event in self.events if 
                event.get('region', {}).get('coordinates', {}).get('x') == x and 
                event.get('region', {}).get('coordinates', {}).get('y') == y]