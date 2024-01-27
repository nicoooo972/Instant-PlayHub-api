class Game:
    def __init__(self, game_id, name, description, version, category):
        self.game_id = game_id
        self.name = name
        self.description = description
        self.version = version
        self.category = category

    def get_game_id(self):
        return self.game_id

    def get_game_name(self):
        return self.name
    
    def get_game_description(self):
        return self.description
    
    def get_game_category(self):
        return self.category
    
    def get_game_version(self):
        return self.version