from flask import Flask,redirect,render_template,request,session,url_for, jsonify


app = Flask(__name__)
app.secret_key = 'very secret123'


def horizontal_win_check(new_state, user_token):
    """check new_state to see if it would make 3
    in a horizontal row of user's token"""
    three_row = user_token * 3
    if (new_state[0:3] == three_row
            or new_state[3:6] == three_row
            or new_state[6:9] == three_row):
        return True
    

def vertical_win_check(new_state, user_token):
    """check new_state to see if it would make 3
    in a vertical row of user's token"""
    three_row = user_token * 3
    if (new_state[0] + new_state[3] + new_state[6] == three_row
            or new_state[1] + new_state[4] + new_state[7] == three_row
            or new_state[2] + new_state[5] + new_state[8] == three_row):
        return True

def diagonal_win_check(new_state, user_token):
    """check new_state to see if it would make 3
    in a diagonal row of user's token"""
    three_row = user_token * 3
    if (new_state[0] + new_state[4] + new_state[8] == three_row
            or new_state[2] + new_state[4] + new_state[6] == three_row):
        return True


@app.route('/get', methods=['GET'])
def get_point():
    if request.method == 'GET':
        state = request.get_json()
        user_turn = state['user_turn']
        turn_number = state['turn_number']
        # assign X/O token
        if turn_number % 2 == 0:
            user_token = 'X'
        else:
            user_token = 'O'
        # set state to base if the game has just been initialized
        if state['state'] == 'START':
            game_state = '123456789'
        elif state['state'].find("WIN -") > -1:
            return state['state']
        else:
            game_state = state['state']
        # create resulting game state for possible moves
        new_states = {}
        for i in range(1,10):
            if game_state[i-1].isnumeric():
                new_states[str(i)] = game_state.replace(str(i), user_token)
        # starting with turn 10, the game is done and there is no winner
        if turn_number > 9:
            # TODO code draw
            pass
        # starting with the fifth turn, it is possible for a user to win
        if turn_number >= 5:
            # for all possible moves
            for position, move in new_states.items():
                # check if that move would win
                if (horizontal_win_check(move, user_token) or
                    vertical_win_check(move, user_token) or
                    diagonal_win_check(move, user_token)):
                    # move's potential state changed to 'WIN -' if it would win
                    new_states[position] = 'WIN - ' + user_token
        print(new_states)
        return render_template('index.html', game_state=game_state, 
                                             new_states = new_states,
                                             user_turn = user_turn,
                                             user_token = user_token)
