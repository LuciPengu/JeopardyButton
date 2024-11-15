# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow connections from any origin

# Store player buzzer data
players = {}
buzzer_order = []
is_active = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/host')
def host():
    return render_template('host.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('player_join')
def handle_join(data):
    print(f"Player joining: {data}")  # Debug print
    player_name = data['name']
    if player_name not in players:
        players[player_name] = {
            'timestamp': None,
            'buzzed': False
        }
        emit('player_joined', {'name': player_name}, broadcast=True)
        print(f"Players currently in game: {players}")  # Debug print

@socketio.on('buzz')
def handle_buzz(data):
    print(f"Buzz received from: {data}")  # Debug print
    global is_active
    player_name = data['name']

    if is_active and player_name in players and not players[player_name]['buzzed']:
        players[player_name]['buzzed'] = True
        players[player_name]['timestamp'] = datetime.now()
        buzzer_order.append(player_name)
        emit('buzz_received', {
            'name': player_name,
            'order': len(buzzer_order)
        }, broadcast=True)
        print(f"Current buzzer order: {buzzer_order}")  # Debug print

@socketio.on('reset_buzzers')
def handle_reset():
    print("Resetting buzzers")  # Debug print
    global is_active, buzzer_order
    for player in players:
        players[player]['buzzed'] = False
        players[player]['timestamp'] = None
    buzzer_order.clear()
    is_active = True
    emit('buzzers_reset', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)