import random


from flask import Flask, redirect, render_template, request, url_for, jsonify


app = Flask(__name__)


DIE_REF = {
            'R': {
                'color': 'R',
                'faces': {
                        1: 'shotgun',
                        2: 'shotgun',
                        3: 'shotgun',
                        4: 'footprints',
                        5: 'footprints',
                        6: 'brain'
                        }
                },
            'Y': {
                'color': 'Y', 
                'faces': {
                        1: 'shotgun',
                        2: 'shotgun',
                        3: 'footprints',
                        4: 'footprints',
                        5: 'brain',
                        6: 'brain'
                        }
                },
            'G': {
                'color': 'G',
                'faces': {
                        1: 'shotgun',
                        2: 'footprints',
                        3: 'footprints',
                        4: 'brain',
                        5: 'brain',
                        6: 'brain'
                        }
                }
            }


FACE_IMAGE_DICT = {
    'gb': 'https://imgoat.com/uploads/644a684f98/199655.png',
    'gf': 'https://imgoat.com/uploads/644a684f98/199656.png',
    'gs': 'https://imgoat.com/uploads/644a684f98/199657.png',
    'rb': 'https://imgoat.com/uploads/644a684f98/199658.png',
    'rs': 'https://imgoat.com/uploads/644a684f98/199659.png',
    'rf': 'https://imgoat.com/uploads/644a684f98/199660.png',
    'yb': 'https://imgoat.com/uploads/644a684f98/199661.png',
    'yf': 'https://imgoat.com/uploads/644a684f98/199662.png',
    'ys': 'https://imgoat.com/uploads/644a684f98/199663.png'
}


class ZombieDice():
    """TODO class docstring"""
    def __init__(self, game_state, user_pk, players):
        self.results_for_image = []
        self.get_attr_from_str(game_state)
        self.user_pk = user_pk
        self.players = players


    def get_attr_from_str(self, game_state):
        """parse the current game state to get class attributes"""
        split_game_state = game_state.split('?')
        raw_dice_cup = split_game_state[0]
        self.raw_player_scores = split_game_state[1]
        raw_current_hand = split_game_state[4]
        raw_last_move = split_game_state[5]
        self.player_turn = split_game_state[6]
        if raw_last_move:
            self.last_move = self.format_last_move(raw_last_move)
        else:
            self.last_move = ''
        self.round_score = int(split_game_state[2])
        self.round_shotguns = int(split_game_state[3])
        self.dice_cup = self.format_dice_cup(raw_dice_cup)
        self.current_hand = self.format_current_hand(raw_current_hand)
        self.player_scores = self.format_player_scores(self.raw_player_scores)

    
    def format_last_move(self, last_move):
        """take last move from state string and reformat to be used"""
        last_move_split = last_move.split(',')
        if last_move_split[0] == 'roll':
            # for result in last_move_split:
            for i in range(len(last_move_split)):
                if i != 0:
                    last_move_split[i] = last_move_split[i].split('-')
                    if last_move_split[i][0] == 'R':
                        last_move_split[i][0] = 'red die'
                    elif last_move_split[i][0] == 'Y':
                        last_move_split[i][0] = 'yellow die'
                    else:
                        last_move_split[i][0] = 'green die'
            die_1 = last_move_split[1]
            die_2 = last_move_split[2]
            die_3 = last_move_split[3]
            for die in (die_1, die_2, die_3):
                self.results_for_image.append(die[0][0] + die[1][0])
            message = (f'Previous roll was a {die_1[0]} with a result '
                        f'of {die_1[1]}, a {die_2[0]} with a result of '
                        f'{die_2[1]}, and a {die_3[0]} with a result of '
                        f'{die_3[1]}')
            return message
        else:
            return (f"Previous player banked {last_move_split[1]} points")


    def format_dice_cup(self, dice_cup):
        """take dice cup from state string and reformat to be used"""
        dice_cup_list = []
        for character in dice_cup:
            dice_cup_list.append(character)
        return dice_cup_list


    def format_player_scores(self, player_scores):
        """take player scores from state string and reformat to be used"""
        player_score_list = player_scores.split(',')
        for i in range(len(player_score_list)):
            player_score_list[i] = player_score_list[i].split(':')
            player_score_list[i][0] = int(player_score_list[i][0])
            player_score_list[i][1] = int(player_score_list[i][1])
        return player_score_list


    def format_current_hand(self, current_hand):
        """take current hand from state string and reformat to be used"""
        hand_list = []
        for character in current_hand:
            hand_list.append(character)
        return hand_list


    def roll_sequence(self):
        """full sequence of methods for a player choosing to roll"""
        self.pull_dice()
        roll_results = self.roll_dice()
        str_results = self.roll_results_to_str(roll_results)
        self.evaluate_roll(roll_results)
        string_state = self.return_to_string_state(str_results)
        return string_state


    def bank_sequence(self):
        """full sequence of methods for a player choosing to bank"""
        str_results = self.bank_score()
        if self.check_win():
            return f'WIN - {self.user_pk}'
        string_state = self.return_to_string_state(str_results)
        return string_state

    
    def check_win(self):
        """check if a player has reached or exceeded 13 points after bank"""
        return int(self.banked_score) >= 13


    def pull_dice(self):
        """draw from cup until player has 3 dice in hand"""
        for i in range(3 - len(self.current_hand)):
            die_index = random.randint(0, len(self.dice_cup) - 1)
            drawn_die = self.dice_cup.pop(die_index)
            self.current_hand.append(drawn_die)


    def roll_dice(self):
        """roll three dice and return results"""
        roll_results = [[], [], []]
        for i in range(len(self.current_hand)):
            roll_int = random.randint(1, 6)
            die_color = DIE_REF[self.current_hand[i]]['color']
            die_result = DIE_REF[self.current_hand[i]]['faces'][roll_int]
            roll_results[i] = (die_color, die_result)
        self.current_hand = []
        return roll_results


    def roll_results_to_str(self, roll_results):
        """convert roll results to a string with format
        roll,color-result,color-result,color-result
        """
        result_str = 'roll'
        for result in roll_results:
            color = result[0]
            face = result[1]
            result_str += (',' + color + '-' + face)
        return result_str

    
    def evaluate_roll(self, roll_results):
        """update round points/shotguns/hand post-roll"""
        for result in roll_results:
            if result[1] == 'shotgun':
                self.round_shotguns += 1
                if self.round_shotguns >= 3:
                    self.reset_round_state()
                    try:
                        next_index = self.players.index(self.player_turn)+1
                        self.player_turn = self.players[next_index]
                    except IndexError:
                        self.player_turn = self.players[0]
                    break
            elif result[1] == 'footprints':
                self.current_hand.append(result[0])
            else:
                self.round_score += 1

    
    def bank_score(self):
        """bank current round score, returns string with 'bank, points'"""
        for player_score in self.player_scores:
            if player_score[0] == self.user_pk:
                player_score[1] += self.round_score
                self.banked_score = player_score[1]
                score_for_last_move = self.round_score
                self.reset_round_state()
                try:
                    next_index = self.players.index(self.player_turn)+1
                    self.player_turn = self.players[next_index]
                except IndexError:
                    self.player_turn = self.players[0]
        return ("bank," + str(score_for_last_move))

    
    def reset_round_state(self):
        """reset round state (points, shotguns, hand, cup) to initial
        state after either a bank action or a player exceeding 3 shotguns
        """
        self.round_score = 0
        self.round_shotguns = 0
        self.dice_cup = 'GGGGGGYYYYRRR'
        self.current_hand = []

    
    def return_to_string_state(self, last_move):
        """return a string representation of the next game state. Format is
        cup?player:score,etc.?round pts?round shotguns?round hand?last move
        """
        dice_cup_str = ''
        current_hand_str = ''
        player_scores_str = ''
        for character in self.dice_cup:
            dice_cup_str += character
        for character in self.current_hand:
            current_hand_str += character
        # for player_score_list in self.player_scores
        if last_move[0:4] == 'roll':
            player_scores_str = self.raw_player_scores
        else:
            for player_score in self.player_scores:
                player_scores_str += f'{player_score[0]}:{player_score[1]},'
            player_scores_str = player_scores_str[:len(player_scores_str)-1:]
        string_state = (f'{dice_cup_str}?{player_scores_str}?'
                        f'{self.round_score}?{self.round_shotguns}'
                        f'?{current_hand_str}?{last_move}?{self.player_turn}')
        return string_state


def create_start_state(player_list, user_pk):
    """create a string of the starting state given a list of player pks"""
    start_players_scores = ''
    for player in player_list:
        start_players_scores += (str(player) + ':0,')
    start_players_scores = start_players_scores[:len(start_players_scores)-1:]
    # state is cup?player:score?round score?round shotguns?
    # leftover dice?last move?player turn
    game_state = f'GGGGGGYYYYRRR?{start_players_scores}?0?0???{user_pk}'
    return game_state


@app.route('/get', methods=['GET'])
def get_point():
    if request.method == 'GET':
        state = request.get_json()
        user_turn = state['user_turn']
        turn_number = state['turn_number']
        players = state['players']
        user_pk = state['pk']
        # set state to base if the game has just been initialized
        if state['state'] == 'START':
            game_state = create_start_state(players, user_pk)
        elif state['state'].find("WIN -") > -1:
            return state['state']
        else:
            game_state = state['state']
        # instantiate a class to return the result of a 'bank' action
        bank = ZombieDice(game_state=game_state, user_pk=user_pk, players=players)
        bank_results = bank.bank_sequence()
        # instantiate a class to return the result of a 'roll' action
        roll = ZombieDice(game_state=game_state, user_pk=user_pk, players=players)
        last_turn_str = roll.last_move
        round_score = roll.round_score
        shotguns = roll.round_shotguns
        game_score = roll.player_scores
        if str(user_pk) == str(roll.player_turn):
            player_turn = "Yes"
        else:
            player_turn = "No"
        roll_results = roll.roll_sequence()
        results_for_image = roll.results_for_image
        for i in range(len(results_for_image)):
            results_for_image[i] = FACE_IMAGE_DICT[results_for_image[i]]


        return render_template(
            'index.html', 
            roll_results = roll_results,
            shotguns = shotguns,
            game_score = game_score,
            round_score = round_score,
            bank_results = bank_results,
            turn_number = turn_number,
            user_turn = user_turn,
            player_turn = player_turn,
            last_turn_str = last_turn_str,
            image_list = results_for_image)