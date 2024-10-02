import json
from pylantir.data.data_manager import DataManager
from pylantir.data.map_manager import MapManager

class GameManager:
    def __init__(self, data_manager: DataManager, map_manager: MapManager):
        self.game_data = {}
        self.data_manager = data_manager
        self.map_manager = map_manager

    def load_game_data(self, filename: str):
        with open(filename, 'r') as file:
            self.game_data = json.load(file)
        
        # Convert map data to the format expected by MapManager
        map_data = self.game_data['map']
        converted_map_data = {}
        for region in map_data:
            coords = region['coordinates']
            key = f"{coords['x']},{coords['y']}"
            converted_map_data[key] = region
        
        self.map_manager.set_map_data(converted_map_data)
        
        # Load report data
        report_data = self.game_data['report']
        self.data_manager.set_report_data(report_data)

    def save_game_data(self, filename: str):
        map_data = self.map_manager.get_map_data()
        report_data = self.data_manager.get_report_data()
        
        # Convert map data back to list format for saving
        map_list = list(map_data.values())
        
        save_data = {
            'map': map_list,
            'report': report_data
        }
        
        with open(filename, 'w') as file:
            json.dump(save_data, file, indent=4)

    def get_game_data(self):
        return self.game_data

    def set_game_data(self, map_data, report_data):
        self.game_data['map'] = map_data
        self.game_data['report'] = report_data

    def get_map_data(self):
        map_data = self.map_manager.get_map_data()
        return list(map_data.values())

    def get_report_data(self):
        return self.data_manager.get_report_data()


