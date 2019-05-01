from flask import Flask, render_template, redirect, url_for, send_file
from flask_socketio import SocketIO
import config

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)

players = []
checkerboard = [[0 for col in range(19)] for row in range(19)]
turn_color = 1
finished = False

def output_board():
    count = 0
    for y in range(0, 19):
        for x in range(0, 19):
            if checkerboard[x][y] != 0:
                count += 1
            print(str(checkerboard[x][y]), end=",")
        print()
    print("There are " + str(count) + " stones on the board.")

def winning_judge(x, y, color):

    global finished

    horizontalAmount = 0        #-
    verticalAmount = 0          #|
    diagonal_LL_UR = 0          #/
    diagonal_UL_LR = 0          #\
 
    #-
    for i in range(x, -1, -1):
        if checkerboard[i][y] != color:
            break
        horizontalAmount += 1

    for i in range(x+1, 19):
        if checkerboard[i][y] != color:
            break
        horizontalAmount += 1

    #|
    for i in range(y, -1, -1):
        if checkerboard[x][i] != color:
            break
        verticalAmount += 1
    for i in range(y+1, 19):
        if checkerboard[x][i] != color:
            break
        verticalAmount += 1

    #\
    for i,j in zip(range(x, -1, -1), range(y, -1, -1)):
        if checkerboard[i][j] != color:
            break
        diagonal_LL_UR += 1
    for i,j in zip(range(x+1, 19), range(y+1, 19)):
        if checkerboard[i][j] != color:
            break
        diagonal_LL_UR += 1

    #/
    for i,j in zip(range(x, -1, -1), range(y, 19)):
        if checkerboard[i][j] != color:
            break
        diagonal_UL_LR += 1
    for i,j in zip(range(x+1, 19), range(y-1, -1, -1)):
        if checkerboard[i][j] != color:
            break
        diagonal_UL_LR += 1
 
    if horizontalAmount >= 5 or verticalAmount >= 5 or diagonal_LL_UR >= 5 or diagonal_UL_LR >= 5:
        finished = True
        return color

    return 0

@socketio.on('assign color')
def handle_assign_event(data):
    if data['color'] == 0:
        if len(players) == 2:
            socketio.emit('redirect', {'url': 'game_server/templates/error.html'})
        if len(players) == 0:
            players.append(1)
            socketio.emit("color res", 1)
        elif len(players) == 1:
            players.append(2)
            socketio.emit("color res", 2)
        

@socketio.on('place stone')
def handle_place_event(data):

    global finished
    global turn_color
    x = int(data['x'])
    y = int(data['y'])
    color = int(data['chessColor'])

    print(str(color) + " wants to place the stone at: (" + str(x) + "," + str(y) + ")")

    if finished:
        socketio.emit("finished", color)
        return

    elif len(players) == 1:
        socketio.emit("wait player to join")
        return

    elif color != turn_color:
        socketio.emit("wrong turn", color)
    else:
        if x >= 0 and x < 19 and y >= 0 and y < 19:
            if checkerboard[x][y] != 0:
                socketio.emit("wrong place", color)
            else:
                checkerboard[x][y] = color
                socketio.emit("draw stone", data)
                
                turn_color = 1 if color ==2 else 2

                if not winning_judge(x, y, color) == 0:
                    socketio.emit("winning res", color)
    output_board()

@socketio.on('clean checkerboard')
def handle_clean_event():
    global finished
    global turn_color
    turn_color = 1
    players.clear()
    for x in range(0, 19):
        for y in range(0, 19):
            checkerboard[x][y] = 0
    finished = False
    socketio.emit("cleaned")
                

@app.route('/', methods=['GET', 'POST'])
def home():
    return '<h1>Home</h1>'

if __name__ == '__main__':
    app.run()
    