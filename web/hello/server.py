from crypt import methods
import json

from requests import session
from database.models import DBSession,Server
from flask import Flask, request, jsonify, render_template
from main import ServerCrud

app = Flask("my-app")

# front page
@app.route('/')
def index():
    print(request.path)
    print(request.full_path)
    index_info = {
        'server_num':23,
        'user_num':210,
        'click_num':232243
    }
    server_infos=[
        {
            "name":"Lin-AI-26","ip":"10.126.62.37","cuda":"10.1","location":"唐山机房","further_info":' <a href="server">服务器使用状况</a>'
        },
        {
            "name": "Lin-AI-27", "ip": "10.126.62.37", "cuda": "10.1", "location": "唐山机房", "further_info": '<a href="server">服务器使用状况</a>'
        }
    ]
    recommend_infos = [
        {
            "name":"Lin-AI-26",
            "server-type":"测试服务器",
            "link":"server"
        },
        {
            "name": "Lin-AI-27",
            "server-type": "测试服务器",
            "link": "server"
        },
        {
            "name": "Lin-AI-28",
            "server-type": "测试服务器",
            "link": "server"
        }

    ]
    active = 1
    return render_template('index.html', page_title='首页 - INSIS GPU管理平台',info=index_info,
                           servers = server_infos,r= recommend_infos,active = active)

# server status page
@app.route('/server')
def server():
    print(request.path)
    print(request.full_path)
    server_info = {"server":"Lin-AI-27","ip":"10.126.62.37","cuda":"10.1","location":"唐山机房","GPU_num":"3"}
    service_status = {"status":"在线","available_gpu_num":"2","CPU_rate":"31.9%","HDD_rate":"39.8%"}
    GPU_status = [
        {
            "GPU_id":"0","availability":"1","type":"TITIAN Xp","gpu_rate":"7271","gpu_total":"12196"
        },
        {
            "GPU_id": "1", "availability": "1", "type": "TITIAN Xp", "gpu_rate": "7271", "gpu_total": "12196"
        }
    ]
    occupy_status = [
        {
            "occupy_id":1,
            "used":20,
            "total":150
        },
        {
            "occupy_id": 2,
            "used": 20,
            "total": 110
        },
        {
            "occupy_id": 3,
            "used": 20,
            "total": 130
        }
    ]
    active = 2
    return render_template('server.html', page_title='服务器 - INSIS GPU管理平台')

# summary page
@app.route('/report')
def report():
    active=3
    trend = [
        {
            'trend_id': 1,
            'y-axis':[250, 130, 224, 212, 335, 143, 260],
            'x-axis':['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }, {
            'trend_id': 2,
            'y-axis': [250, 130, 224, 212, 335, 143, 260],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },{
            'trend_id': 3,
            'y-axis':[250, 130, 224, 212, 335, 143, 260],
            'x-axis':['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    ]
    return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台',active = active)

# 我希望是以post的方式
@app.route('/api/server/loginorup')
def report(name,address,memory_limit,hdd_limit,gpu_num):
    session = DBSession()
    crud = ServerCrud(session)
    instance = crud.find_one(address=address)
    if instance is None:
        instance = Server(name=name, address=address,memory_limit=memory_limit,hdd_limit=hdd_limit,gpu_num=gpu_num)
        instance = crud.add_from_model(instance)
    else:
        instance.name = name
        instance.gpu_num = gpu_num
        instance.hdd_limit =hdd_limit
        instance.memory_limit =memory_limit
        instance = crud.update_from_model(instance)

    return json.dumps({"pk": instance.pk})


'''
@app.route('/add', methods=['POST'])
def add():
    result = {'sum': request.json['a'] + request.json['b']}
    return jsonify(result)

@app.route('/user')
def user():
    user_info = {
        'name': 'letian',
        'email': '123@aa.com',
        'age':0,
        'github': 'https://github.com/letiantian'
    }
    return render_template('userinfo.html', page_title='letian\'s info', user_info=user_info)
'''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)