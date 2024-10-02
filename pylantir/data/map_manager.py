from typing import Dict, Any

class MapManager:

    def __init__(self):
        self.map_data = {}


    def set_map_data(self, map_data: Dict[str, Any]) -> None:
        """
        Set the map data.

        Args:
            map_data (Dict[str, Any]): A dictionary containing the map data.
        """
        self.map_data = map_data

    def get_map_data(self) -> Dict[str, Any]:
        """
        Get the map data.

        Returns:
            Dict[str, Any]: A dictionary containing the map data.
        """
        return self.map_data    

    def get_region(self, x, y):
        return self.map_data.get(f"{x},{y}")

    def set_region(self, x, y, region):
        self.map_data[f"{x},{y}"] = region

    def get_units_in_region(self, x, y):
        region = self.get_region(x, y)
        return region.get('units', [])

    def update_map_data(self, new_data):
        """
        Update the map data with new information.

        Args:
            new_data (dict): New map data to be merged with existing data.
        """
        for key, value in new_data.items():
            if key in self.map_data:
                self.map_data[key].update(value)
            else:
                self.map_data[key] = value

    def update_region(self, x: int, y: int, region_data: Dict[str, Any]) -> None:
        """
        Update an existing region or add a new one if it doesn't exist.

        Args:
            x (int): X-coordinate of the region.
            y (int): Y-coordinate of the region.
            region_data (Dict[str, Any]): New data for the region.
        """
        key = f"{x},{y}"
        if key in self.map_data:
            self.map_data[key].update(region_data)
        else:
            self.map_data[key] = region_data
        print(f"Region ({x}, {y}) updated/added in MapManager.")

