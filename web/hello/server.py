# from crypt import methods
import json

from requests import session
from database.models import DBSession, Server
from flask import Flask, request, jsonify, render_template
# from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length

from database.crud import ServerCrud
from database.models import DBSession
from database.pdmodel import ServerReturn

app = Flask("my-app")

# test database
# db = SQLAlchemy(app)  # 创建一个对象，设置名为db

# 建立数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:admin4mysql@10.126.62.37:8843/monitor"

from database.redis import Redis

red = Redis()
red.hset("client_info_1", "memory_used", 48325)
red.hset("client_info_1", "hdd_used", 35225)
red.hset("client_info_1", "uptime", 62356)
print(red.hget("client_info_1", "hdd_used"))
print(red.hget("client_info_1", "memory_used"))

app.secret_key = 'secret string'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me')
    select = SelectMultipleField(
        label='标签', choices=[('Military', '军事'), ('New', '新闻'), ('Society', '社会'), ('Technology', '科技')])
    submit = SubmitField('Log in')


@app.route('/form', methods=['POST', 'GET'])
def form():
    form = LoginForm()
    if form.validate_on_submit():
        tags = form.select
        print('select:{}'.format(tags.data))
    return render_template('login.html', form=form)


# test
@app.route('/form3', methods=['GET'])
def form3():
    return render_template('login2.html')


@app.route('/respond', methods=['POST'])
def respond():  # Parse the JSON data included in the request
    data = json.loads(request.data)
    response = data.get('response')  # DO STUFF... Process the response here
    # Return a request to the JavaScript
    print(response)
    return render_template('summary.html')
    #json.dumps({'status': 'OK', 'response': response})


# 以post的方式
@app.route('/api/server/loginorup')
def report2(name, address, memory_limit, hdd_limit, gpu_num):
    session = DBSession()
    crud = ServerCrud(session)
    instance = crud.find_one(address=address)
    if instance is None:
        instance = Server(name=name, address=address, memory_limit=memory_limit, hdd_limit=hdd_limit, gpu_num=gpu_num)
        instance = crud.add_from_model(instance)
    else:
        instance.name = name
        instance.gpu_num = gpu_num
        instance.hdd_limit = hdd_limit
        nstance.memory_limit = memory_limit
        instance = crud.update_from_model(instance)
    return json.dumps({"pk": instance.pk})


# 验证是否连接成功
# @app.route('/database_server')
def get_server():
    session = DBSession()
    crud = ServerCrud(session)
    #
    instances = crud.find()
    json_list = []
    for instance in instances:
        print(instance)
        print(instance.name)
        print(ServerReturn.from_orm(instance))
        pdm = ServerReturn.from_orm(instance)
        # pdj = pdm.json() # 返回json字符串
        # print(pdm.json())
        json_list.append(pdm)
    return json_list


# front page
@app.route('/')
def index():
    print(request.path)
    print(request.full_path)
    index_info = {
        'server_num': 23,
        'user_num': 210,
        'click_num': 232243
    }
    '''
    server_infos = [
        {
            "name": "Lin-AI-26", "ip": "10.126.62.37", "cuda": "10.1", "location": "唐山机房",
            "further_info": ' <a href="server">服务器使用状况</a>'
        },
        {
            "name": "Lin-AI-27", "ip": "10.126.62.37", "cuda": "10.1", "location": "唐山机房",
            "further_info": '<a href="server">服务器使用状况</a>'
        }
    ]
    '''
    server_infos = get_server()
    # 推荐服务器，汇总数据
    recommend_infos = [
        {
            "name": "Lin-AI-26",
            "server-type": "测试服务器",
            "link": "server"
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
    return render_template('index.html', page_title='首页 - INSIS GPU管理平台', info=index_info,
                           servers=server_infos, r=recommend_infos, active=active)


# server status page, display 实时数据
@app.route('/server')
def server_detail():
    r = request.args.get('sid')
    if r == None:
        # do something
        return 'not found'
    session = DBSession()
    crud = ServerCrud(session)
    this = crud.find_one(name=r)
    if this is not None:
        from database.redis import Redis
        red = Redis()
        server_info = {"server": str(this.name), "ip": str(this.address), "cuda": str(this.cuda_version),
                       "location": str(this.location), "GPU_num": str(this.gpus)}
        # 实时数据
        hdd_used = red.hget("client_info_1", "hdd_used")
        memory_used = red.hget("client_info_1", "memory_used")
        print(this.hdd_limit)
        print(this.memory_limit)
        hdd_rate = float(hdd_used) / float(this.hdd_limit)
        memory_rate = float(memory_used) / float(this.memory_limit)
        hdd_rate = format(hdd_rate, '.2%')
        memory_rate = format(memory_rate, '.2%')
        service_status = {"status": "在线", "available_gpu_num": "实时数据", "CPU_rate": memory_rate, "HDD_rate": hdd_rate}
        GPU_status = [
            {"GPU_id": "0", "availability": "1", "type": "TITIAN Xp", "gpu_used": "7271", "gpu_total": "12196"},
            {"GPU_id": "1", "availability": "1", "type": "TITIAN Xp", "gpu_used": "7271", "gpu_total": "12196"}
        ]
        gpu_used, gpu_total = 0, 0
        for gpu in GPU_status:
            gpu_used += int(gpu["gpu_used"])
            gpu_total += int(gpu["gpu_total"])
        print("gpu_used:%d, gpu_total%d" % (gpu_used, gpu_total))
        occupy_status = [{
            "occupy_id": 1,
            "used": gpu_used,
            "total": gpu_total
        },
            {
                "occupy_id": 2,
                "used": hdd_used,
                "total": this.hdd_limit
            },
            {
                "occupy_id": 3,
                "used": memory_used,
                "total": this.memory_limit
            }
        ]
        active = 2
        return server(server_info, service_status, GPU_status, occupy_status)
    else:
        return "invalid key"


@app.route('/server_test')
def server(server_info, service_status, GPU_status, occupy_status):
    print(request.path)
    print(request.full_path)
    return render_template('server.html', page_title='服务器 - INSIS GPU管理平台', server=server_info,
                           service_status=service_status,
                           GPUs=GPU_status, occupy_status=occupy_status)


# summary page
@app.route('/report')
def report():
    active = 3
    trend = [
        {
            'trend_id': 1,
            'y-axis': [250, 130, 224, 212, 335, 143, 260],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }, {
            'trend_id': 2,
            'y-axis': [250, 130, 224, 212, 335, 143, 260],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }, {
            'trend_id': 3,
            'y-axis': [250, 130, 224, 212, 335, 143, 260],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    ]
    return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=active)


# 我希望是以post的方式
@app.route('/api/server/loginorup')
def add_server(name, address, memory_limit, hdd_limit, gpu_num):
    session = DBSession()
    crud = ServerCrud(session)
    instance = crud.find_one(address=address)
    if instance is None:
        instance = Server(name=name, address=address, memory_limit=memory_limit, hdd_limit=hdd_limit, gpu_num=gpu_num)
        instance = crud.add_from_model(instance)
    else:
        instance.name = name
        instance.gpu_num = gpu_num
        instance.hdd_limit = hdd_limit
        instance.memory_limit = memory_limit
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
