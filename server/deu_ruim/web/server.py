import json
import traceback
import time as timelib
import requests

from flask import Flask, request, jsonify

from deu_ruim.web.repositories.in_memory.story_repository import *
from deu_ruim.web.repositories.in_memory.user_repository import *
from deu_ruim.domain.application_services.story_service import *
from deu_ruim.domain.application_services.user_service import *

def render_story(story):
    story_d = story.__dict__.copy()
    story_d['location'] = story_d['location'].__dict__.copy()
    story_d['tags'] = list(story_d['tags'])
    return story_d

def render_stories(stories):
    return {'stories': list(map(render_story, stories))}

def render_user(user):
    user_d = user.__dict__.copy()
    return user_d

def render_users(users):
    return {'users': list(map(render_story, users))}

app = Flask(__name__)

if __name__ == '__main__': path = './'
elif __name__ == 'deu_ruim.web.server': path =  './deu_ruim/web/repositories/in_memory/'
else: raise ExecutionPathError

story_repository = PersistentStoryRepository(path)
story_service = StoryService(story_repository)
user_repository = PersistentUserRepository(path)
user_service = UserService(user_repository)

server_url = '0.0.0.0'
server_port = '80'

#Objeto JSON recebido deve conter:
# id          :  int
# title       :  string
# description :  string
# location    :  list<Int>
# tags        :  list<Strings>

@app.route('/',defaults={'path':''})
@app.route('/<path:path>')
def catch_all(path):
    response = requests.get('http://'+server_url+':1337/'+path)
    return response.content

@app.route('/stories/<time>', methods=['GET'])
def get_stories(time):
    try:
        if time == 'all':
            stories = story_service.get_all_stories()
            return 'var data = '+json.dumps(render_stories(stories))+';'

        if time == 'now':
            time = timelib.time()
        stories = story_service.get_stories(time)
        return jsonify(render_stories(stories))
    except:
        traceback.print_exc()
        return 'Erro interno do servidor'


def parse_data(data):
    if len(data['location']) != 2: data['location'] = [1337, 1337]
    return data

@app.route('/stories', methods=['POST'])
def create_story():
    try:
        print(request.data)
        loadedData = json.loads(request.data)
        loadedData = parse_data(loadedData)
        story = story_service.create_story(
                loadedData['title'],
                loadedData['description'],
                loadedData['location'][0],
                loadedData['location'][1],
                loadedData['category'],
                loadedData['tags'])
        return jsonify(render_story(story))
    except:
        traceback.print_exc()
        return 'Erro interno do servidor'


@app.route('/stories/search', methods=['POST'])
def search_stories():
    try:
        data = json.loads(request.data)
        if 'tags' not in data.keys(): data['tags'] = []
        stories = story_service.search_story(data['tags'])
        return jsonify(render_stories(stories))
    except:
        traceback.print_exc()
        return 'Erro interno do servidor'

@app.route('/stories/disqualify', methods=['POST'])
def disqualify_story():
    try:
        data = json.loads(request.data)
        if 'id' not in data.keys():
            data['id'] = None
        story = story_service.disqualify_story(data['id'])
    except:
        traceback.print_exc()
        return 'Erro interno do servidor'


def run():
    app.run(host=server_url, port=server_port)
