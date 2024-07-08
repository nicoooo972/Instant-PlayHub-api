from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from bson.objectid import ObjectId

from ..application.game_service import GameService
from ..domain.state import State
from ..domain.player import Player
from db import db

# Initialisation des structures de données globales
rooms = {}
chat_history = {}

# Création du service de jeu et de l'état
state = State()
game_service = GameService(state)


def get_user_id_from_sid(sid):
    user = db.user.find_one({"sid": sid})
    print(user)
    return str(user["_id"]) if user else None


def setup_uno_sockets(socketio: SocketIO):
    @socketio.on('connect')
    def on_connect():
        print("User connected to Uno")
        socketio.emit('connected',
                      {'message': 'Connected to Uno game server.'})

    @socketio.on('disconnect')
    def on_disconnect():
        print("User disconnected from Uno")
        user_id = get_user_id_from_sid(request.sid)
        for room, players in rooms.items():
            for player in players:
                if player['id'] == user_id:
                    players.remove(player)
                    if len(players) == 0:
                        del rooms[room]
                        if room in chat_history:
                            del chat_history[room]
                        state.delete_all(room)
                    break
        update_rooms()

    @socketio.on('create_room')
    def on_create_room(data):
        print(f"Create room event received with data: {data}")
        room = data['room']
        if room not in rooms:
            rooms[room] = []
            chat_history[room] = []
            print(f"Room {room} created")
            socketio.emit('room_created', {'room': room}, room=request.sid)
            update_rooms()
        else:
            print(f"Room {room} already exists")
            socketio.emit('error', {'message': 'Room already exists'},
                          room=request.sid)

    @socketio.on('join_room')
    def on_join_room(data):
        print(f"Join room event received with data: {data}")
        room = data['room']
        user_id = get_user_id_from_sid(request.sid)
        if user_id is None:
            socketio.emit('error', {'message': 'User not found'},
                          room=request.sid)
            return

        player = Player(user_id)

        allowed, message = state.allow_player('Join', room, player)
        if not allowed:
            print(f"Player not allowed to join: {message}")
            socketio.emit('error', {'message': message}, room=request.sid)
            return

        if room not in rooms:
            print(f"Room {room} does not exist")
            socketio.emit('error', {'message': 'Room does not exist'},
                          room=request.sid)
        elif len(rooms[room]) < 4:
            state.add_player_to_room(room, player)
            rooms[room].append({'id': user_id})
            join_room(room)
            socketio.emit('room_joined',
                          {'room': room, 'playerCount': len(rooms[room]),
                           'player': user_id}, room=request.sid)
            if state.get_game_by_room(room) is None and len(rooms[room]) >= 2:
                players = [p['id'] for p in rooms[room]]
                game_service.start_new_game(room, players)
            update_player_count(room)
            send_chat_history(room)
        else:
            print(f"Room {room} is full")
            socketio.emit('error', {'message': 'Room is full'},
                          room=request.sid)

    @socketio.on('start_game')
    def on_start_game(data):
        print(f"Start game event received with data: {data}")
        room = data['room']
        user_id = get_user_id_from_sid(request.sid)
        if room in rooms and any(
                player['id'] == user_id for player in rooms[room]):
            players = [p['id'] for p in rooms[room]]
            game_service.start_new_game(room, players)
            socketio.emit('game_started',
                          {'message': 'A new Uno game has started.'},
                          room=room)
            update_game_state(room)

    @socketio.on('draw_card')
    def on_draw_card(data):
        print(f"Draw card event received with data: {data}")
        room = data['room']
        user_id = data['player_id']
        if room in rooms and any(
                player['id'] == user_id for player in rooms[room]):
            game_service.draw_card(room, user_id)
            update_game_state(room)

    @socketio.on('play_card')
    def on_play_card(data):
        print(f"Play card event received with data: {data}")
        room = data['room']
        user_id = data['player_id']
        card_id = data['card_id']
        if room in rooms and any(
                player['id'] == user_id for player in rooms[room]):
            try:
                game_service.play_card(room, user_id, card_id)
                update_game_state(room)
            except ValueError as e:
                socketio.emit('error', {'message': str(e)}, room=request.sid)

    @socketio.on('send_message')
    def on_send_message(data):
        print(f"Send message event received with data: {data}")
        room = data['room']
        message = data['message']
        if room in chat_history:
            chat_history[room].append(message)
            socketio.emit('new_message', message, room=room)

    @socketio.on('get_rooms')
    def on_get_rooms():
        print("Get rooms event received")
        update_rooms()

    def update_rooms():
        print("Updating rooms")
        socketio.emit('update_rooms',
                      {room: len(players) for room, players in rooms.items()})

    def update_player_count(room):
        playerCount = len(rooms[room])
        socketio.emit('update_player_count',
                      {'room': room, 'playerCount': playerCount}, room=room)

    def update_game_state(room):
        game_state = game_service.get_game_state(room)
        if game_state:
            socketio.emit('update_state', game_state, room=room)
            if any(len(cards) == 0 for cards in game_state['hands'].values()):
                socketio.emit('game_over', {'message': "Game over"}, room=room)

    def send_chat_history(room):
        if room in chat_history:
            socketio.emit('chat_history', chat_history[room], room=request.sid)
