import numpy as np
import pandas as pd
import requests
import simplejson as json
from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from flask_table import Table, Col, LinkCol

class ItemTable(Table):
    rank = Col('Rank')
    name = Col('Name')

class GameTable(Table):
    col1 = Col('')
    col2 = Col('')
        
class Item(object):
    def __init__(self, rank, name):
        self.rank = rank
        self.name = name

class GameInfo(object):
    def __init__(self, col1, col2):
        self.col1 = col1
        self.col2 = col2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

class TickerForm(FlaskForm):
    game_id = StringField('To retreive game stats, please type in a Game ID:', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    url1 = 'https://api.twitch.tv/helix/games/top'
    params = {'Client-ID':'k1jkbn1hpx54d9feahntrqou29zndo'}
    response = requests.get(url1, headers=params)
    df1 = response.json()
    df1 = df1['data']
    items1 = []
    for i in range(len(df1)):
        name = df1[i]['name']
        items1.append(Item(rank=i+1, name=name))
    table1 = ItemTable(items1)

    url2 = 'https://steamspy.com/api.php'
    params = {'request': 'top100in2weeks'}
    response = requests.get(url2, params=params)
    df2 = response.json()
    df2 = [v['name'] for k, v in df2.items()]
    items2 = []
    for i in range(20):
        name = df2[i]
        items2.append(Item(rank=i+1, name=name))
    table2 = ItemTable(items2)

    params = {'request': 'top100forever'}
    response = requests.get(url2, params=params)
    df3 = response.json()
    df3 = [v['name'] for k, v in df3.items()]
    items3 = []
    for i in range(20):
        name = df3[i]
        items3.append(Item(rank=i+1, name=name))
    table3 = ItemTable(items3)

    form = TickerForm()
    if form.validate_on_submit():
        game_id = form.game_id.data
        game_link = 'https://steamdb.info/embed/?appid=' + game_id
        params = {'request': 'appdetails', 'appid' : game_id}
        response = requests.get(url2, params=params)
        df4 = response.json()
        game_info = [GameInfo('Name', df4['name']), GameInfo('Developer', df4['developer']), GameInfo('Rank', str(df4['score_rank'])+'%'),
        GameInfo('User Score', str(df4['userscore'])+'/100'), GameInfo('Number of Owners', df4['owners']), GameInfo('Price', '$'+str(int(df4['price'])/100))]
        game_info = GameTable(game_info)
        game_db = pd.read_csv('game_db.csv')[:10]

        return render_template('gamestats.html', game_link=game_link, game_info=game_info, game_db=game_db, current_time=datetime.utcnow())
    return render_template('index.html', table1=table1, table2=table2, table3=table3, form=form, current_time=datetime.utcnow())
