import json
import requests
from flask import Blueprint,redirect,render_template,request,session,url_for,jsonify
from sqlite3 import IntegrityError


from ..models.model import *


controller = Blueprint('public',__name__)

@controller.route('/', methods=['GET','POST'])
def frontpage():
    if request.method == 'GET':
        # receive json with keys 'username' and 'password' based on input
        user_credentials = request.get_json()
        print(user_credentials)
        user = User(username=user_credentials['usernameLogin'], 
                    password=user_credentials['passwordLogin'])
        # if credentials are correct, return full user info
        if user:
            return jsonify({'user_info': {'username':user.username, 'pk':user.pk,
                            'display_name':user.display_name,
                            'email':user.email}})
        else:
            return jsonify({})


@controller.route('/registration', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        # receive json with key user info which contains a dict with keys
        # 'username', 'password', 'email', and 'display_name'
        user_credentials = request.get_json()
        user_dict = {'username':user_credentials['usernameRegister'],
                    'password':user_credentials['passwordRegister'],
                    'display_name':user_credentials['nickname'],
                    'email':user_credentials['email']}
        new_user = User(row=user_dict)
        # check whether username exists and return True/False status
        try:
            new_user.save()
            return jsonify({'status': True})
        except IntegrityError:
            return jsonify({'status': False})