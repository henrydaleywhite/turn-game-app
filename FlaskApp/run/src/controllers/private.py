import json
import requests


from flask import Blueprint,redirect,render_template,request,session,url_for,jsonify


from ..models.model import *


controller = Blueprint('private',__name__)

@controller.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'GET':
        # receive json with key user_info which contains a dict with 
        # keys 'username', 'pk', 'email', and 'display_name'
        user_credentials = request.get_json()
        user = User(row=user_credentials['user_info'])
        # get list of games that can be created
        start_game_list = user.get_available_games()
        # get list of unfinished games user is involved with
        cur_game_list = user.get_user_active_games()
        # get list of finished games user has played
        fin_game_list = user.get_user_finished_games()
        return jsonify({'start_list':start_game_list,
                        'continue_list':cur_game_list,
                        'finished_list':fin_game_list})


@controller.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        # receive json with keys game_pk and user info :
        # user_info contains a dict with keys 'username', 'pk',
        # 'email', and 'display_name'.
        # game_pk is the pk of the game from the available_games table
        response = request.get_json()
        user = User(row=response['user_info'])
        game_params = dict(user.game_start_params(pk=response['game_pk']))
        return jsonify({'game_params': game_params})
    elif request.method == 'POST':
        # receive json with keys game_params and user info :
        # user_info contains a dict with keys 'username', 'pk',
        # 'email', and 'display_name'.
        # game_params contains a dict with keys game_pk and user_list
        # user_list has the pks of all users playing the game
        response = request.get_json()
        user = User(row=response['user_info'])
        user_list = response['game_params']['user_list']
        user_pk_list = [user.pk]
        for username in user_list:
            if username:
                player_pk = get_pk_from_username(username)
                user_pk_list.append(player_pk)
        game_pk = response['game_params']['game_pk']
        game_id = user.make_game(game_pk, user_pk_list)
        return jsonify({'game_id': game_id})


@controller.route('/select_continue', methods=['GET','POST'])
def continue_list():
    if request.method == 'GET':
        # receive json with keys game_id and user info :
        # user_info contains a dict with keys 'username', 'pk',
        # 'email', and 'display_name'.
        # game_pk is the unique id of the game from the available_games table
        response = request.get_json()
        user = User(row=response['user_info'])
        avlb_game_pk = response['game_pk']
        continue_games = user.get_user_active_instances_of_game(avlb_game_pk)
        started = []
        for i in range(len(continue_games)):
            if continue_games[i].game_state == 'START':
                started.append([continue_games[i], i])
        continued = []
        for i in range(len(continue_games)):
            if continue_games[i].game_state != 'START':
                continued.append([continue_games[i], i])
        print(continue_games)
        print(started)
        print(continued)
        save_states = []
        room_info = []
        for i in range(len(started)):
            host_username = get_username_from_pk(continue_games[i].playthrough_id.split('-')[0])
            print(started[i])
            try:
                room_info[i]['pk'] = continue_games[started[i][1]].pk
                room_info[i]['game_pk'] = continue_games[started[i][1]].game_pk
                room_info[i]['game_pk'] = continue_games[started[i][1]].game_pk
                room_info[i]['playthrough_id'] = continue_games[started[i][1]].playthrough_id
                room_info[i]['game_state'] = continue_games[started[i][1]].game_state
                room_info[i]['participant_pk'] = continue_games[started[i][1]].participant_pk
                room_info[i]['turn_order'] = continue_games[started[i][1]].turn_order
                room_info[i]['turn_number'] = continue_games[started[i][1]].turn_number
                room_info[i]['endpoint'] = continue_games[started[i][1]].get_avlb_game_info()['endpoint']
                room_info[i]['last_move'] = continue_games[started[i][1]].last_move
                room_info[i]['game_name'] = continue_games[started[i][1]].get_avlb_game_info()['game_name']
                room_info[i]['host_username'] = host_username
            except IndexError:
                room_info.append({})
                room_info[i]['pk'] = continue_games[started[i][1]].pk
                room_info[i]['game_pk'] = continue_games[started[i][1]].game_pk
                room_info[i]['playthrough_id'] = continue_games[started[i][1]].playthrough_id
                room_info[i]['game_state'] = continue_games[started[i][1]].game_state
                room_info[i]['participant_pk'] = continue_games[started[i][1]].participant_pk
                room_info[i]['turn_order'] = continue_games[started[i][1]].turn_order
                room_info[i]['turn_number'] = continue_games[started[i][1]].turn_number
                room_info[i]['endpoint'] = continue_games[started[i][1]].get_avlb_game_info()['endpoint']
                room_info[i]['last_move'] = continue_games[started[i][1]].last_move
                room_info[i]['game_name'] = continue_games[started[i][1]].get_avlb_game_info()['game_name']
                room_info[i]['host_username'] = host_username

        for i in range(len(continued)):
            host_username = get_username_from_pk(continue_games[i].playthrough_id.split('-')[0])
            try:
                save_states[i]['pk'] = continue_games[continued[i][1]].pk
                save_states[i]['game_pk'] = continue_games[continued[i][1]].game_pk
                save_states[i]['playthrough_id'] = continue_games[continued[i][1]].playthrough_id
                save_states[i]['game_state'] = continue_games[continued[i][1]].game_state
                save_states[i]['participant_pk'] = continue_games[continued[i][1]].participant_pk
                save_states[i]['turn_order'] = continue_games[continued[i][1]].turn_order
                save_states[i]['turn_number'] = continue_games[continued[i][1]].turn_number
                save_states[i]['endpoint'] = continue_games[continued[i][1]].get_avlb_game_info()['endpoint']
                save_states[i]['last_move'] = continue_games[continued[i][1]].last_move
                save_states[i]['game_name'] = continue_games[continued[i][1]].get_avlb_game_info()['game_name']
                save_states[i]['host_username'] = host_username
            except IndexError:
                save_states.append({})
                save_states[i]['pk'] = continue_games[continued[i][1]].pk
                save_states[i]['game_pk'] = continue_games[continued[i][1]].game_pk
                save_states[i]['playthrough_id'] = continue_games[continued[i][1]].playthrough_id
                save_states[i]['game_state'] = continue_games[continued[i][1]].game_state
                save_states[i]['participant_pk'] = continue_games[continued[i][1]].participant_pk
                save_states[i]['turn_order'] = continue_games[continued[i][1]].turn_order
                save_states[i]['turn_number'] = continue_games[continued[i][1]].turn_number
                save_states[i]['endpoint'] = continue_games[continued[i][1]].get_avlb_game_info()['endpoint']
                save_states[i]['last_move'] = continue_games[continued[i][1]].last_move
                save_states[i]['game_name'] = continue_games[continued[i][1]].get_avlb_game_info()['game_name']
                save_states[i]['host_username'] = host_username

        return jsonify({'room_info':room_info, 'save_states': save_states})


@controller.route('/gamepage', methods=['GET','POST'])
def gamepage():
    if request.method == 'GET':
        # receive json with keys game_id and user info :
        # user_info contains a dict with keys 'username', 'pk',
        # 'email', and 'display_name'.
        # game_id is the unique id of the game from the game_records table
        response = request.get_json()
        user = User(row=response['user_info'])
        game_pk = user.game_pk_from_id(response['game_id'])
        game = GameStatus(pk=game_pk)
        game_state = game.game_state
        turn_order = game.turn_order.split(',')
        num_players = len(turn_order)
        turn_number = game.turn_number
        user_turn_id = turn_order[(turn_number % num_players)]
        if user_turn_id == str(user.pk):
            user_turn = "Yes"
        else:
            user_turn = "No"
        endpoint = game.endpoint
        game_response = requests.get(f"{endpoint}get", 
                                    json = {
                                        'pk': user.pk,
                                        'state': game_state,
                                        'user_turn': user_turn,
                                        'players': turn_order,
                                        'turn_number': turn_number
                                    }
                                )
        html_to_pass = game_response.text
        return jsonify({'html': html_to_pass})
        
    elif request.method == 'POST':
        # receive json with keys game_params and user info :
        # user_info contains a dict with keys 'username', 'pk',
        # 'email', and 'display_name'.
        # game_params contains a dict with mandatory keys 'game_id' and
        # 'next_state' and optional key 'turn_number'
        # game_id is the unique id of the game from the available_games table
        # next_state is a string representing the state of the game after the
        # most recent move
        # turn_number is an integer for the turn number
        response = request.get_json()
        user = User(row=response['user_info'])
        game_pk = user.game_pk_from_id(response['game_params']['game_id'])
        game = GameStatus(pk=game_pk)
        endpoint = game.endpoint
        turn_number = response.get('turn_number')
        game.game_state = response['game_params']['next_state']
        if turn_number:
            game.turn_number = turn_number
        else:
            game.turn_number += 1
        # update DB for new info
        game.save()
        # win state will have the string "WIN -" in it
        if game.game_state.find("WIN -") > -1:
            return jsonify({'win': True})
        return jsonify({'win': False})