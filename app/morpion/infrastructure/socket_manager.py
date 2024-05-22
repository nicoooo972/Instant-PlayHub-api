# morpion/infrastructure/socket_manager.py
from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from app.morpion.application.game_service import GameService
from app.morpion.domain import board

board = board.Board()
game_service = GameService(board)

rooms = {}

def setup_morpion_sockets(socketio):
    @socketio.on('connect')
    def on_connect():
        print("User connected to Morpion")
        socketio.emit('connected', {'message': 'Connected to Morpion game server.'})

    @socketio.on('disconnect')
    def on_disconnect():
        print("User disconnected from Morpion")
        for room, players in rooms.items():
            for player in players:
                if player['sid'] == request.sid:
                    players.remove(player)
                    if len(players) == 0:
                        del rooms[room]
                    break
        update_rooms()

    @socketio.on('create_room')
    def on_create_room(data):
        room = data['room']
        if room not in rooms:
            rooms[room] = []
            socketio.emit('room_created', {'room': room}, room=request.sid)
            update_rooms()
        else:
            socketio.emit('error', {'message': 'Room already exists'}, room=request.sid)

    @socketio.on('join_room')
    def on_join_room(data):
        room = data['room']
        if room not in rooms:
            socketio.emit('error', {'message': 'Room does not exist'}, room=request.sid)
        elif len(rooms[room]) < 2:
            symbol = 'X' if len(rooms[room]) == 0 else 'O'
            rooms[room].append({'sid': request.sid, 'symbol': symbol})
            join_room(room)
            socketio.emit('room_joined', {'room': room, 'playerCount': len(rooms[room]), 'symbol': symbol}, room=request.sid)
            update_player_count(room)
        else:
            socketio.emit('error', {'message': 'Room is full'}, room=request.sid)

    @socketio.on('start_game')
    def on_start_game(data):
        room = data['room']
        if room in rooms and any(player['sid'] == request.sid for player in rooms[room]):
            game_service.start_new_game()
            socketio.emit('game_started', {'message': 'A new Morpion game has started.'}, room=room)
            update_game_state(room)

    @socketio.on('make_move')
    def on_make_move(data):
        row = data['row']
        col = data['col']
        player = data['player']
        room = data['room']
        if room in rooms and any(p['sid'] == request.sid for p in rooms[room]):
            success, message = game_service.make_move(player, row, col)
            if success:
                update_game_state(room)
            else:
                socketio.emit('error', {'message': message}, room=request.sid)

    @socketio.on('get_rooms')
    def on_get_rooms():
        update_rooms()

    def update_rooms():
        socketio.emit('update_rooms', rooms)

    def update_player_count(room):
        playerCount = len(rooms[room])
        socketio.emit('update_player_count', {'room': room, 'playerCount': playerCount}, room=room)

    def update_game_state(room):
        game_state = game_service.get_game_state()
        socketio.emit('update_state', game_state, room=room)
