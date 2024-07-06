from flask import request
from flask_socketio import SocketIO, join_room, leave_room

from ..application.game_service import GameService
from ..domain.state import State

# Initialisation des structures de données globales
rooms = {}
chat_history = {}

# Création du service de jeu et de l'état
state = State()
game_service = GameService(state)


def setup_uno_sockets(socketio: SocketIO):
    @socketio.on('connect')
    def on_connect():
        print("User connected to Uno")
        socketio.emit('connected',
                      {'message': 'Connected to Uno game server.'})

    @socketio.on('disconnect')
    def on_disconnect():
        print("User disconnected from Uno")
        for room, players in rooms.items():
            for player in players:
                if player['sid'] == request.sid:
                    players.remove(player)
                    if len(players) == 0:
                        del rooms[room]
                        if room in chat_history:
                            del chat_history[room]
                        game_service.games.pop(room, None)
                    break
        update_rooms()

    @socketio.on('create_room')
    def on_create_room(data):
        room = data['room']
        if room not in rooms:
            rooms[room] = []
            chat_history[room] = []
            socketio.emit('room_created', {'room': room}, room=request.sid)
            update_rooms()
        else:
            socketio.emit('error', {'message': 'Room already exists'},
                          room=request.sid)

    @socketio.on('join_room')
    def on_join_room(data):
        room = data['room']
        if room not in rooms:
            socketio.emit('error', {'message': 'Room does not exist'},
                          room=request.sid)
        elif len(rooms[room]) < 4:
            player = {'sid': request.sid}
            rooms[room].append(player)
            join_room(room)
            socketio.emit('room_joined',
                          {'room': room, 'playerCount': len(rooms[room]),
                           'player': request.sid}, room=request.sid)
            if room not in game_service.games and len(rooms[room]) >= 2:
                players = [p['sid'] for p in rooms[room]]
                game_service.start_new_game(room, players)
            update_player_count(room)
            send_chat_history(room)
        else:
            socketio.emit('error', {'message': 'Room is full'},
                          room=request.sid)

    @socketio.on('start_game')
    def on_start_game(data):
        room = data['room']
        if room in rooms and any(
                player['sid'] == request.sid for player in rooms[room]):
            players = [p['sid'] for p in rooms[room]]
            game_service.start_new_game(room, players)
            socketio.emit('game_started',
                          {'message': 'A new Uno game has started.'},
                          room=room)
            update_game_state(room)

    @socketio.on('draw_card')
    def on_draw_card(data):
        room = data['room']
        player_id = data['player_id']
        if room in rooms and any(
                player['sid'] == request.sid for player in rooms[room]):
            game_service.draw_card(room, player_id)
            update_game_state(room)

    @socketio.on('play_card')
    def on_play_card(data):
        room = data['room']
        player_id = data['player_id']
        card_id = data['card_id']
        if room in rooms and any(
                player['sid'] == request.sid for player in rooms[room]):
            try:
                game_service.play_card(room, player_id, card_id)
                update_game_state(room)
            except ValueError as e:
                socketio.emit('error', {'message': str(e)}, room=request.sid)

    @socketio.on('send_message')
    def on_send_message(data):
        room = data['room']
        message = data['message']
        if room in chat_history:
            chat_history[room].append(message)
            socketio.emit('new_message', message, room=room)

    @socketio.on('get_rooms')
    def on_get_rooms():
        update_rooms()

    def update_rooms():
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
