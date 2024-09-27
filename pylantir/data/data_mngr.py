import json
from typing import List, Dict, Optional, Any, Union
from pylantir.data.map_manager import MapManager

class DataMngr:
    def __init__(self, map_manager: MapManager):
        self.report_data: Optional[Dict] = None
        self.map_manager = map_manager
 

    def load_report(self, filename: str) -> None:
        """
        Load a JSON report file into the data manager.

        This method clears any existing report data and then loads the
        contents of the specified JSON file into self.report_data.

        Args:
            filename (str): The path to the JSON report file to be loaded.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            PermissionError: If the file cannot be read due to permissions.

        Returns:
            None
        """
        try:
            # Clear existing data
            self.report_data = None

            # Load and parse the JSON file
            with open(filename, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)

            print(f"Report loaded successfully from {filename}")
            print(f"Number of regions in report: {len(self.report_data.get('regions', []))}")
            
            # After successfully loading the report, update the MapManager
            self.update_map_manager()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in '{filename}': {str(e)}")
            raise
        except PermissionError:
            print(f"Error: Permission denied when trying to read '{filename}'.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while loading the report: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def update_map_manager(self) -> None:
        if self.report_data is None:
            print("No report data loaded. Please load a report first.")
            return

        regions = self.report_data.get('regions', [])
        print(f"Updating MapManager with {len(regions)} regions")
        for region in regions:
            coordinates = region.get('coordinates', {})
            x, y = coordinates.get('x'), coordinates.get('y')
            if x is not None and y is not None:
                self.map_manager.update_region(x, y, region)

        print("MapManager updated with the latest report data.")

    def update_map_manager(self) -> None:
        """
        Update the MapManager with the latest report data.
        """
        if self.report_data is None:
            print("No report data loaded. Please load a report first.")
            return

        regions = self.report_data.get('regions', [])
        for region in regions:
            coordinates = region.get('coordinates', {})
            x, y = coordinates.get('x'), coordinates.get('y')
            if x is not None and y is not None:
                self.map_manager.update_region(x, y, region)

        print("MapManager updated with the latest report data.")

    def get_regions(self) -> List[Dict]:
        """
        Extract and return region data from the loaded report.

        Returns:
            List[Dict]: A list of dictionaries, each containing data for a single region.
                        Returns an empty list if no report data is loaded or if there are no regions.

        Raises:
            AttributeError: If report_data is None or doesn't have a 'regions' key.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return []

            regions = self.report_data.get('regions', [])
            if not regions:
                print("No region data found in the loaded report.")

            return regions

        except AttributeError as e:
            print(f"Error accessing region data: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while getting regions: {e}")
            return []

    def get_faction_info(self) -> Dict[str, str]:
        """
        Retrieve faction information from the loaded report data.

        Returns:
            Dict[str, str]: A dictionary containing the faction name and number.
                            Keys are 'name' and 'number'.
                            Returns {'name': 'Unknown', 'number': 'Unknown'} if data is not available.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return {"name": "Unknown", "number": "Unknown"}

            faction_info = {
                "name": self.report_data.get("name", "Unknown"),
                "number": self.report_data.get("number", "Unknown")
            }

            return faction_info

        except AttributeError as e:
            print(f"Error accessing faction data: {e}")
            return {"name": "Unknown", "number": "Unknown"}
        except Exception as e:
            print(f"An unexpected error occurred while getting faction info: {e}")
            return {"name": "Unknown", "number": "Unknown"}

    def save_persistent_data(self, map_manager: MapManager) -> None:
        """
        Save persistent data from the current report to the provided MapManager.

        Args:
            map_manager (MapManager): The MapManager instance to update with persistent data.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return

            regions = self.report_data.get('regions', [])
            persistent_data = {}

            for region in regions:
                coordinates = region.get('coordinates', {})
                x, y = coordinates.get('x'), coordinates.get('y')
                if x is not None and y is not None:
                    key = f"{x},{y}"
                    persistent_data[key] = {
                        'terrain': region.get('terrain'),
                        'province': region.get('province'),
                        'settlement': region.get('settlement'),
                        'population': region.get('population'),
                        # Add any other persistent data you want to keep
                    }

            map_manager.update_map_data(persistent_data)
            print("Persistent data saved to MapManager successfully.")

        except AttributeError as e:
            print(f"Error accessing report data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving persistent data: {e}")

    def get_date_info(self) -> Dict[str, str]:
        """
        Retrieve date information from the loaded report data.

        Returns:
            Dict[str, str]: A dictionary containing the month and year of the report.
                            Keys are 'month' and 'year'.
                            Returns {'month': 'Unknown', 'year': 'Unknown'} if data is not available.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return {"month": "Unknown", "year": "Unknown"}

            date_info = self.report_data.get("date", {})
            return {
                "month": date_info.get("month", "Unknown"),
                "year": str(date_info.get("year", "Unknown"))
            }

        except AttributeError as e:
            print(f"Error accessing date information: {e}")
            return {"month": "Unknown", "year": "Unknown"}
        except Exception as e:
            print(f"An unexpected error occurred while getting date info: {e}")
            return {"month": "Unknown", "year": "Unknown"}

    def get_all_events_for_hex(self, x: int, y: int) -> List[Dict[str, Any]]:
        """
        Retrieve all unique events associated with a specific hex.

        Args:
            x (int): X-coordinate of the hex.
            y (int): Y-coordinate of the hex.

        Returns:
            List[Dict[str, Any]]: A list of unique events relevant to the hex.
                                  Returns an empty list if no events are found or if there's an error.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return []

            all_events = self.report_data.get('events', [])
            hex_events = []

            # Get region-based events
            hex_events.extend([
                event for event in all_events
                if event.get('region', {}).get('coordinates', {}).get('x') == x
                and event.get('region', {}).get('coordinates', {}).get('y') == y
            ])

            # Get unit-based events
            units_in_hex = self.map_manager.get_units_in_region(x, y)
            unit_numbers = [unit.get('number') for unit in units_in_hex if unit.get('number') is not None]
            hex_events.extend([
                event for event in all_events
                if event.get('unit', {}).get('number') in unit_numbers
            ])

            # Remove duplicates while preserving order
            unique_events = []
            seen_messages = set()
            for event in hex_events:
                message = event.get('message')
                if message and message not in seen_messages:
                    unique_events.append(event)
                    seen_messages.add(message)

            return unique_events

        except AttributeError as e:
            print(f"Error accessing report data: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while getting events for hex ({x}, {y}): {e}")
            return []

    def get_orders_for_hex(self, x: int, y: int) -> List[Dict[str, Any]]:
        """
        Retrieve orders for all units in a specific hex.

        Args:
            x (int): X-coordinate of the hex.
            y (int): Y-coordinate of the hex.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing unit names, numbers, and their orders.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return []

            regions = self.report_data.get('regions', [])
            target_region = next((region for region in regions 
                                  if region.get('coordinates', {}).get('x') == x 
                                  and region.get('coordinates', {}).get('y') == y), None)

            if not target_region:
                print(f"No region found for coordinates ({x}, {y})")
                return []

            units = target_region.get('units', [])
            orders = []

            for unit in units:
                if unit.get('own_unit', False):  # Only include orders for own units
                    unit_orders = unit.get('orders', [])
                    orders.append({
                        'unit_name': unit.get('name', 'Unknown Unit'),
                        'unit_number': unit.get('number', 'Unknown'),
                        'orders': unit_orders
                    })

            return orders

        except Exception as e:
            print(f"An error occurred while getting orders for hex ({x}, {y}): {e}")
            return []

    def get_engine_info(self) -> Dict[str, str]:
        """
        Retrieve engine information from the loaded report data.

        Returns:
            Dict[str, str]: A dictionary containing the engine information.
                            Keys are 'ruleset', 'ruleset_version', and 'version'.
                            Returns default values if data is not available.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return {
                    "ruleset": "Unknown",
                    "ruleset_version": "Unknown",
                    "version": "Unknown"
                }

            engine_info = self.report_data.get("engine", {})
            return {
                "ruleset": engine_info.get("ruleset", "Unknown"),
                "ruleset_version": engine_info.get("ruleset_version", "Unknown"),
                "version": engine_info.get("version", "Unknown")
            }

        except AttributeError as e:
            print(f"Error accessing engine information: {e}")
            return {
                "ruleset": "Unknown",
                "ruleset_version": "Unknown",
                "version": "Unknown"
            }
        except Exception as e:
            print(f"An unexpected error occurred while getting engine info: {e}")
            return {
                "ruleset": "Unknown",
                "ruleset_version": "Unknown",
                "version": "Unknown"
            }

    def get_attitudes(self) -> Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]:
        """
        Retrieve attitude information from the loaded report data.

        Returns:
            Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]: A dictionary containing the attitude information.
                Keys are 'default', 'ally', 'friendly', 'neutral', 'unfriendly', and 'hostile'.
                The 'default' value is a string, while others are lists of dictionaries with 'name' and 'number' keys.
                Returns default values if data is not available.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return {
                    "default": "neutral",
                    "ally": [],
                    "friendly": [],
                    "neutral": [],
                    "unfriendly": [],
                    "hostile": []
                }

            attitudes = self.report_data.get("attitudes", {})
            return {
                "default": attitudes.get("default", "neutral"),
                "ally": attitudes.get("ally", []),
                "friendly": attitudes.get("friendly", []),
                "neutral": attitudes.get("neutral", []),
                "unfriendly": attitudes.get("unfriendly", []),
                "hostile": attitudes.get("hostile", [])
            }

        except AttributeError as e:
            print(f"Error accessing attitude information: {e}")
            return {
                "default": "neutral",
                "ally": [],
                "friendly": [],
                "neutral": [],
                "unfriendly": [],
                "hostile": []
            }
        except Exception as e:
            print(f"An unexpected error occurred while getting attitude info: {e}")
            return {
                "default": "neutral",
                "ally": [],
                "friendly": [],
                "neutral": [],
                "unfriendly": [],
                "hostile": []
            }

    def get_administrative_settings(self) -> Dict[str, Union[str, bool]]:
        """
        Retrieve administrative settings from the loaded report data.

        Returns:
            Dict[str, Union[str, bool]]: A dictionary containing the administrative settings.
                Keys are 'email', 'password_unset', 'show_unit_attitudes', and 'times_sent'.
                Returns default values if data is not available.

        Raises:
            AttributeError: If report_data is None.
        """
        try:
            if self.report_data is None:
                print("No report data loaded. Please load a report first.")
                return {
                    "email": "",
                    "password_unset": False,
                    "show_unit_attitudes": False,
                    "times_sent": False
                }

            admin_settings = self.report_data.get("administrative", {})
            return {
                "email": admin_settings.get("email", ""),
                "password_unset": admin_settings.get("password_unset", False),
                "show_unit_attitudes": admin_settings.get("show_unit_attitudes", False),
                "times_sent": admin_settings.get("times_sent", False)
            }

        except AttributeError as e:
            print(f"Error accessing administrative settings: {e}")
            return {
                "email": "",
                "password_unset": False,
                "show_unit_attitudes": False,
                "times_sent": False
            }
        except Exception as e:
            print(f"An unexpected error occurred while getting administrative settings: {e}")
            return {
                "email": "",
                "password_unset": False,
                "show_unit_attitudes": False,
                "times_sent": False
            }

