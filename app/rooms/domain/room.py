import uuid

from db import db


class Room:
    def create_room(self, room_name, game_type, creator_id):
        room = {
            "_id": uuid.uuid4().hex,
            "room_name": room_name,
            "game_type": game_type,
            "players": [],
            "creator_id": creator_id
        }
        return db.rooms.insert_one(room)

    def get_all_rooms(self):
        return list(db.rooms.find())

    def get_rooms_by_game(self, game_type):
        return list(db.rooms.find({"game_type": game_type}))

    def add_player_to_room(self, room_name, player_id):
        return db.rooms.update_one({"room_name": room_name},
                                   {"$push": {"players": player_id}})

    def delete_room(self, room_name, creator_id):
        room = db.rooms.find_one({"room_name": room_name})
        if room and room["creator_id"] == creator_id:
            return db.rooms.delete_one({"room_name": room_name})
        else:
            return None


room_model = Room()
