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

    @classmethod
    def add_player_to_room(cls, room_id, player_id):
        return db.rooms.update_one({"_id": room_id},
                                   {"$addToSet": {"players": player_id}})

    def delete_room(self, room_name, creator_id):
        room = db.rooms.find_one({"room_name": room_name})
        if room and room["creator_id"] == creator_id:
            result = db.rooms.delete_one({"room_name": room_name})
            return result
        else:
            return None

    @classmethod
    def get_room_by_id(cls, room_id):
        return db.rooms.find_one({"_id": room_id})


room_model = Room()
