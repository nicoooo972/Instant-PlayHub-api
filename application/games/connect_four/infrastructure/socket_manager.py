from flask import request
from flask_socketio import SocketIO, join_room, leave_room, emit

from application.games.connect_four.application.game_service import GameService
from application.infrastructure.user import User

game_service = GameService()
rooms = {}
user_sessions = {}


def setup_connect_four_sockets(socketio):

    @socketio.on('connect_connect4')
    def on_connect():
        print(f"User connected to Connect Four with SID: {request.sid}")
        emit('connected_connect4', {'message': 'Connected to Connect Four game server.'})

    @socketio.on('disconnect_connect4')
    def on_disconnect():
        print(f"User disconnected from Connect Four with SID: {request.sid}")
        user_id = next((u_id for u_id, s_id in user_sessions.items() if s_id == request.sid), None)
        if user_id:
            del user_sessions[user_id]
        for room, players in rooms.items():
            for player in players:
                if player['sid'] == request.sid:
                    players.remove(player)
                    print(f"Removed player {request.sid} from room {room}")
                    if len(players) == 0:
                        del rooms[room]
                        print(f"Deleted room {room} as it became empty")
                    break

    @socketio.on('join_room_connect4')
    def on_join_room_connect4(data):
        room_name = data['room']
        user_id = data['user_id']
        room_id = data['room_id']

        if user_id is None:
            emit('error_connect4', {'message': 'User ID is required to join a room'}, room=request.sid)
            return

        if room_id not in rooms:
            rooms[room_id] = []

        if len(rooms[room_id]) < 2 and user_id not in [p['user_id'] for p in rooms[room_id]]:
            user_sessions[user_id] = request.sid
            symbol = 'X' if len(rooms[room_id]) == 0 else 'O'
            rooms[room_id].append({'user_id': user_id, 'sid': request.sid, 'symbol': symbol})
            join_room(room_id)
            emit('room_joined_connect4', {'room': room_id, 'symbol': symbol}, room=request.sid)
            if len(rooms[room_id]) == 2:
                start_game(room_id)
        else:
            emit('error_connect4', {'message': 'Room is full or user already in room'}, room=request.sid)

    def start_game(room_id):
        game_service.__init__()  # Reset the game state
        emit('game_started_connect4', {'message': 'A new Connect Four game has started.'}, room=room_id)
        update_game_state(room_id)

    @socketio.on('make_move_connect4')
    def on_make_move(data):
        column = data['column']
        room = data['room']
        if room in rooms and any(p['sid'] == request.sid for p in rooms[room]):
            game_state = game_service.get_board()
            current_player_sid = next((p['sid'] for p in rooms[room] if p['symbol'] == game_state['current_player']), None)
            if current_player_sid != request.sid:
                emit('error_connect4', {'message': "It's not your turn!"}, room=request.sid)
                return

            result = game_service.drop_piece(column)
            if 'error' in result:
                emit('error_connect4', result, room=request.sid)
            else:
                update_game_state(room)
                if 'winner' in result:
                    emit('game_over_connect4', {'message': f"{result['winner']} wins!"}, room=room)
                elif 'draw' in result:
                    emit('game_over_connect4', {'message': "It's a draw!"}, room=room)

    def update_game_state(room):
        game_state = game_service.get_board()
        current_player = next((p for p in rooms[room] if p['symbol'] == game_state['current_player']), None)
        emit('update_state_connect4', {**game_state, 'current_player_info': current_player}, room=room)

    @socketio.on('send_message_connect4')
    def on_send_message(data):
        room = data['room']
        message = data['message']
        user_id = next((u_id for u_id, s_id in user_sessions.items() if s_id == request.sid), None)
        if user_id:
            user = User().get_one_user(user_id)
            emit('new_message_connect4', {'user': user['username'], 'message': message}, room=room)
