import json
import os
from typing import Any, Dict, List, Optional, Tuple


class DataManager:
    """
    Manages the loading, processing, and retrieval of game data from JSON reports
    and persistent storage. Handles regions, events, units, and related information.
    """

    def __init__(self):
        """Initialize the DataManager with empty data structures."""
        self.report_data: Dict[str, Any] = {}  # Stores the entire report data
        self.persistent_map_data: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.regions: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.events: List[Dict[str, Any]] = []

    # -----------------------------
    # Report Loading and Processing
    # -----------------------------

    def load_report(self, filename: str) -> None:
        """
        Load a JSON report file and process its data.

        Args:
            filename (str): The path to the JSON report file to be loaded.

        Raises:
            Exception: If there's an error while reading or processing the file.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.report_data = json.load(file)
            self._process_report_data()
            print(f"Report '{filename}' loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            print(f"Error loading report '{filename}': {e}")
            raise

    def _process_report_data(self) -> None:
        """
        Process the loaded report data to populate regions and events.

        Clears existing regions and updates them with new data from the report.
        Merges persistent data into regions where applicable.
        """
        self.regions.clear()
        regions_data = self.report_data.get('regions', [])

        for region in regions_data:
            coordinates = region.get('coordinates', {})
            x = coordinates.get('x')
            y = coordinates.get('y')

            if x is None or y is None:
                print(f"Warning: Region with missing coordinates: {region}")
                continue

            key = (x, y)
            self.regions[key] = region
            self._merge_persistent_data(x, y)

        # Process events from the report
        self.events = self.report_data.get('events', [])
        print(f"Processed {len(self.regions)} regions and {len(self.events)} events from the report.")

    # -----------------------------
    # Persistent Data Handling
    # -----------------------------

    def save_persistent_data(self, filename: str) -> None:
        """
        Save persistent map data to a JSON file.

        Args:
            filename (str): The path to save the JSON file.

        Raises:
            Exception: If there's an error while saving the file.
        """
        try:
            # Convert tuple keys to comma-separated strings for JSON serialization
            serializable_data = {f"{k[0]},{k[1]}": v for k, v in self.persistent_map_data.items()}
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(serializable_data, file, ensure_ascii=False, indent=4)
            print(f"Persistent data saved to '{filename}' successfully.")
        except (IOError, PermissionError, TypeError) as e:
            print(f"Error saving persistent data to '{filename}': {e}")
            raise

    def load_persistent_data(self, filename: str) -> None:
        """
        Load persistent data from a JSON file and merge it with current regions.

        Args:
            filename (str): Path to the JSON file containing persistent data.

        Raises:
            Exception: If there's an error while loading the file.
        """
        if not os.path.exists(filename):
            print(f"No persistent data file found at '{filename}'. Starting with empty data.")
            return

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
            # Convert string keys back to tuple coordinates
            self.persistent_map_data = {
                tuple(map(int, k.split(','))): v for k, v in data.items()
            }
            print(f"Persistent data loaded from '{filename}' successfully.")
            self._apply_persistent_data()
        except (IOError, json.JSONDecodeError, ValueError) as e:
            print(f"Error loading persistent data from '{filename}': {e}")
            raise

    def _apply_persistent_data(self) -> None:
        """
        Merge persistent map data into the regions.

        Ensures that all persistent data is correctly integrated into the current regions.
        """
        for (x, y), data in self.persistent_map_data.items():
            self._merge_persistent_data(x, y)
        print(f"Applied persistent data to {len(self.persistent_map_data)} regions.")

    def _merge_persistent_data(self, x: int, y: int) -> None:
        """
        Merge persistent data into a specific region.

        If the region does not exist in the current regions, it initializes it.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.
        """
        key = (x, y)
        if key in self.persistent_map_data:
            if key not in self.regions:
                # Initialize the region if it doesn't exist
                self.regions[key] = {'coordinates': {'x': x, 'y': y}}
                print(f"Initialized new region at coordinates ({x}, {y}) with persistent data.")
            self.regions[key].update(self.persistent_map_data[key])
            print(f"Merged persistent data into region ({x}, {y}).")

    # -----------------------------
    # Region and Event Retrieval
    # -----------------------------

    def get_regions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all region data.

        Returns:
            List[Dict[str, Any]]: A list of all regions.
        """
        return list(self.regions.values())

    def get_region(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the region data for given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.

        Returns:
            Optional[Dict[str, Any]]: The region data if found, else None.
        """
        return self.regions.get((x, y))

    def update_region(self, x: int, y: int, data: Dict[str, Any]) -> None:
        """
        Update a region's data at the given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.
            data (Dict[str, Any]): New data to update the region with.
        """
        key = (x, y)
        if key in self.regions:
            self.regions[key].update(data)
            self.persistent_map_data[key] = self.persistent_map_data.get(key, {})
            self.persistent_map_data[key].update(data)
            print(f"Updated region ({x}, {y}) with data: {data}")
        else:
            # Initialize the region if it doesn't exist
            self.regions[key] = {'coordinates': {'x': x, 'y': y}, **data}
            self.persistent_map_data[key] = data
            print(f"Initialized and updated new region ({x}, {y}) with data: {data}")

    # -----------------------------
    # Event Retrieval Methods
    # -----------------------------

    def get_events(self) -> List[Dict[str, Any]]:
        """
        Retrieve all events from the report.

        Returns:
            List[Dict[str, Any]]: A list of all events.
        """
        return self.events

    def get_events_for_region(self, x: int, y: int) -> List[Dict[str, Any]]:
        """
        Retrieve events specific to a region based on its coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.

        Returns:
            List[Dict[str, Any]]: A list of events related to the region.
        """
        return [
            event for event in self.events
            if event.get('region', {}).get('coordinates', {}).get('x') == x and
               event.get('region', {}).get('coordinates', {}).get('y') == y
        ]

    def get_events_for_units(self, unit_numbers: List[int]) -> List[Dict[str, Any]]:
        """
        Retrieve events associated with specific units.

        Args:
            unit_numbers (List[int]): A list of unit numbers.

        Returns:
            List[Dict[str, Any]]: A list of events associated with the given units.
        """
        return [
            event for event in self.events
            if event.get('unit', {}).get('number') in unit_numbers
        ]

    def get_all_events_for_hex(self, x: int, y: int) -> List[Dict[str, Any]]:
        """
        Retrieve all unique events associated with a specific hex.

        Combines region-based and unit-based events, ensuring no duplicates.

        Args:
            x (int): X-coordinate of the hex.
            y (int): Y-coordinate of the hex.

        Returns:
            List[Dict[str, Any]]: A list of unique events relevant to the hex.
        """
        # Fetch region-based events
        region_events = self.get_events_for_region(x, y)

        # Fetch units in the hex
        region = self.get_region(x, y)
        units = region.get('units', []) if region else []
        unit_numbers = [unit.get('number') for unit in units if unit.get('number') is not None]

        # Fetch unit-based events
        unit_events = self.get_events_for_units(unit_numbers)

        # Combine and deduplicate events based on unique message or a composite key
        unique_events = []
        seen_keys = set()

        for event in region_events + unit_events:
            # Define a unique identifier for deduplication
            # Here, using the event's message as a unique key
            # Adjust this logic if messages are not unique
            message = event.get('message')
            if message and message not in seen_keys:
                unique_events.append(event)
                seen_keys.add(message)

        print(f"Aggregated {len(unique_events)} unique events for hex ({x}, {y}).")
        return unique_events

    # -----------------------------
    # Information Retrieval Methods
    # -----------------------------

    def get_faction_info(self) -> Dict[str, Any]:
        """
        Retrieve faction information from the report data.

        Returns:
            Dict[str, Any]: Faction name and number, with 'Unknown' as default.
        """
        return {
            "name": self.report_data.get("name", "Unknown"),
            "number": self.report_data.get("number", "Unknown")
        }

    def get_date_info(self) -> Dict[str, Any]:
        """
        Retrieve date information from the report data.

        Returns:
            Dict[str, Any]: Month and year, with 'Unknown' as default.
        """
        date_info = self.report_data.get("date", {})
        return {
            "month": date_info.get("month", "Unknown"),
            "year": date_info.get("year", "Unknown")
        }

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Retrieve engine information from the report data.

        Returns:
            Dict[str, Any]: Engine ruleset, version, and software version.
        """
        engine_info = self.report_data.get("engine", {})
        return {
            "ruleset": engine_info.get("ruleset", "Unknown"),
            "ruleset_version": engine_info.get("ruleset_version", "Unknown"),
            "version": engine_info.get("version", "Unknown")
        }

    def get_attitudes(self) -> Dict[str, Any]:
        """
        Retrieve attitudes information from the report data.

        Returns:
            Dict[str, Any]: Default attitude, capitalized.
        """
        attitudes = self.report_data.get("attitudes", {})
        return {
            "default": attitudes.get("default", "Unknown").capitalize()
        }

    def get_administrative_settings(self) -> Dict[str, Any]:
        """
        Retrieve administrative settings from the report data.

        Returns:
            Dict[str, Any]: Password status, unit attitudes visibility, and times sent.
        """
        admin = self.report_data.get("administrative", {})
        return {
            "password_unset": admin.get("password_unset", False),
            "show_unit_attitudes": admin.get("show_unit_attitudes", False),
            "times_sent": admin.get("times_sent", True)
        }

    def get_markets(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the markets for the region at given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.

        Returns:
            Optional[Dict[str, Any]]: 'for_sale' and 'wanted' markets if available, else None.
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

    def get_settlement(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve the settlement information for the region at given coordinates.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.

        Returns:
            Optional[Dict[str, Any]]: Settlement details if available, else None.
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
