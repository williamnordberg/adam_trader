from flask import render_template
from flask import redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import flask
from dash.dependencies import Input, Output
import configparser
import os


def load_configuration():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

    with open(config_path, 'r') as f:
        config_string = f.read()

    config.read_string(config_string)
    SERVER_SECRET_KEY = config.get('server_key', 'flask')

    return SERVER_SECRET_KEY


def setup_auth(app, server):
    login_manager = LoginManager()
    login_manager.init_app(server)

    users = {
        'user1': {
            'password': 'user1',
        },
        'user2': {
            'password': 'user2123',
        },
        'user3': {
            'password': 'user3123',
        },
    }

    class User(UserMixin):
        pass

    @login_manager.user_loader
    def user_loader(username):
        if username not in users:
            return
        user = User()
        user.id = username
        return user

    @server.route('/')
    def home():
        if not current_user.is_authenticated:
            return redirect(flask.url_for('login'))
        else:
            return flask.redirect('/protected_page')

    @app.server.before_request
    def protect_dash_views():
        if flask.request.path == '/' or flask.request.path.startswith('/_dash'):
            if not current_user.is_authenticated:
                return flask.redirect(flask.url_for('login'))

    @server.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if username in users and users[username]['password'] == password:
                user = User()
                user.id = username
                login_user(user)
                return redirect('/')
            else:
                return "Wrong username or password"
        else:
            return render_template('login.html')  # Render the HTML template

    @server.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')

    @server.route('/protected_page')
    @login_required
    def protected():
        return 'You are seeing this because you are logged in!'

    @app.callback(Output('logout', 'pathname'), [Input('logout-button', 'n_clicks')])
    def logout(n):
        if n is not None:
            return '/logout'
        return '/'

    @server.route('/logout')
    def routelogout():
        return redirect('http://192.168.1.178:8051/login')  # Redirection to an external site