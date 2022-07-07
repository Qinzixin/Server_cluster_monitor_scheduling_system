# from crypt import methods
import json
from json import load, dump
from requests import session
from database.models import GPU, DBSession,Server
from flask import Flask, request, jsonify, render_template
# from flask_sqlalchemy import SQLAlchemy
from database.crud import GPUCrud, ServerCrud
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectField
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
# red.hset("client_info_1", "memory_used", 48325)
# red.hset("client_info_1", "hdd_used", 35225)
# red.hset("client_info_1", "uptime", 62356)
# print(red.hget("client_info_1", "hdd_used"))
# print(red.hget("client_info_1", "memory_used"))

app.secret_key = 'secret string'


class LoginForm(FlaskForm):
    select = SelectField(label="",choices=[('dayinfo', '天信息'),('weekinfo', '周信息'),('monthinfo', '月信息'),('yearinfo', '年信息')])
    submit = SubmitField('确认')


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
@app.route('/api/server/loginorup',methods=["POST"])
def report2():
    name = request.form.get("name")
    address = request.form.get("address")
    memory_limit = request.form.get("memory_limit")
    hdd_limit = request.form.get("hdd_limit")
    gpu_info = json.loads(request.form.get("gpu_info"))
    if isinstance(address,str) and address.startswith("127."):
        return "IP地址不能是以127开头的地址"
    session = DBSession()
    crud = ServerCrud(session)
    instance = crud.find_one(address=address)

    if instance is None:
        instance = Server(name=name, address=address,memory_limit=memory_limit,hdd_limit=hdd_limit,gpu_num=len(gpu_info),
                        cuda_version = gpu_info[0])
        instance = crud.add_from_model(instance)
        gpu_crud = GPUCrud(session)
        for gpu_ar in gpu_info[1:]:
            temp_gpu = GPU(name=gpu_ar[1],cuda_version=gpu_info[0],server_id=instance.pk)
            gpu_crud.add_from_model(temp_gpu)
    else:
        instance.name = name
        instance.gpu_num = len(gpu_info)-1
        instance.hdd_limit =hdd_limit
        instance.memory_limit =memory_limit
        instance.cuda_version = gpu_info[0]
        instance = crud.update_from_model(instance)
        if instance.gpus is None or len(instance.gpus)==0:
            gpu_crud = GPUCrud(session)
            for gpu_ar in gpu_info[1:]:
                temp_gpu = GPU(name=gpu_ar[1],cuda_version=gpu_info[0],server_id=instance.pk)
                gpu_crud.add_from_model(temp_gpu)
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
        #print(instance)
        #print(instance.name)
        #print(ServerReturn.from_orm(instance))
        pdm = ServerReturn.from_orm(instance)
        # pdj = pdm.json() # 返回json字符串
        # print(pdm.json())
        json_list.append(pdm)
    return json_list

class server_occupy:
    def __init__(self,pk,name,occupy,address,cuda,location):
        self.pk = pk
        self.name = name
        self.occupy = occupy
        self.address = address
        self.cuda_version = cuda
        self.location = location

# front page
@app.route('/')
def index():
    print(request.path)
    print(request.full_path)
    people = 0
    with open("people.json") as f:  # 打开json数据 并将访问量+1
        people = load(f) + 1
    with open("people.json", "w") as f:  # 再存储到文件中
        dump(people, f)
    server_infos = get_server()
    server_num = len(server_infos)
    server_occupy_list = []
    gpu_sum = 0
    for server in server_infos:
        # print(server)
        r = server.name
        session = DBSession()
        crud = ServerCrud(session)
        this = crud.find_one(name=r)
        if this is not None:
            score, gpu_cnt = recommendation(this)
            gpu_sum += gpu_cnt
            server_occupy_list.append(server_occupy(this.pk,this.name,score,this.address,this.cuda_version,this.location))
    def get_key(x):
        return x.occupy
    server_occupy_list.sort(key=get_key,reverse=True)

    # for server in server_infos:
    #    server_occupy_list.

    # 平台概况数据
    index_info = {
        'server_num': server_num,
        'gpu_num': gpu_sum,
        'click_num': people
    }
    # print(server_infos)
    # 推荐服务器，汇总数据
    recommend_infos = [
        {
            "name": server_occupy_list[-1].name,
            "server-type":"测试服务器",
            "link": "server?sid="+server_occupy_list[-1].name
        },
        {
            "name": server_occupy_list[-2].name,
            "server-type": "测试服务器",
            "link": "server?sid="+server_occupy_list[-2].name
        },
        {
            "name": server_occupy_list[-3].name,
            "server-type": "测试服务器",
            "link": "server?sid=" + server_occupy_list[-3].name
        }
    ]
    active = 1
    return render_template('index.html', page_title='首页 - INSIS GPU管理平台', info=index_info,
                           servers=server_occupy_list, r=recommend_infos, active=active)


# 服务器页面
@app.route('/server')
def server_detail():
    r = request.args.get('sid') # get sid or served
    if r == None:
        # do something
        return 'not found'
    session = DBSession()
    crud = ServerCrud(session)
    this = crud.find_one(name=r)
    server_dynamic = "client_info_" + str(this.pk) # server info
    if this is not None:
        from database.redis import Redis
        red = Redis()
        server_info = {"server": str(this.name), "ip": str(this.address), "cuda": str(this.cuda_version),
                       "location": str(this.location), "GPU_num": str(this.gpu_num)}
        # 实时数据
        hdd_used = red.hget(server_dynamic, "hdd_used")
        memory_used = red.hget(server_dynamic, "memory_used")
        # print(hdd_used,this.hdd_limit)
        # print(memory_used,this.memory_limit)
        if hdd_used is not None:
            hdd_rate = float(hdd_used) / float(this.hdd_limit)
            hdd_rate = format(hdd_rate, '.2%')
        else:
            hdd_rate = "-"
        if memory_used is not None:
            memory_rate = float(memory_used) / float(this.memory_limit)
            memory_rate = format(memory_rate, '.2%')
        else:
            memory_rate = "-"

        GPU_status = []
        available_gpu = 0
        for gpu in this.gpus:
            gpu_used = red.hget(server_dynamic, "gpu_" + str(gpu.pk)+ "_used")
            gpu_total = red.hget(server_dynamic, "gpu_" + str(gpu.pk) + "_total")
            state = "0"
            if gpu_total != None and float(gpu_used)/ float(gpu_total) < 0.90:
                state = "1"
                available_gpu +=1
            elif gpu_total != None:
                state = "2"
            gpu_info = {"GPU_id": gpu.pk, "availability": state, "type": gpu.name, "gpu_used": gpu_used,
                        "gpu_total": gpu_total}
            GPU_status.append(gpu_info)
        gpu_used, gpu_total = 0, 0
        service_status = {"status": "在线", "available_gpu_num": available_gpu, "CPU_rate": memory_rate, "HDD_rate": hdd_rate}
        for gpu in GPU_status:
            if gpu["gpu_used"] != None and gpu["gpu_total"] != None:
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
        return server(server_info, service_status, GPU_status, occupy_status)
    else:
        return "invalid key"

def recommendation(this):
    server_dynamic = "client_info_" + str(this.pk)  # server dynamic address
    from database.redis import Redis
    red = Redis()
    # basic info
    server_info = {"server": str(this.name), "ip": str(this.address), "cuda": str(this.cuda_version),
                   "location": str(this.location), "GPU_num": str(this.gpu_num)}
    # dynamic score
    score = 3

    hdd_used = red.hget(server_dynamic, "hdd_used")
    memory_used = red.hget(server_dynamic, "memory_used")

    if hdd_used is not None:
        hdd_rate = float(hdd_used) / float(this.hdd_limit)
        score += float(hdd_rate)

    else:
        score -= 0.5

    if memory_used is not None:
        memory_rate = float(memory_used) / float(this.memory_limit)
        score += float(memory_rate)
    else:
        score -= 0.5

    gpu_sum = 0
    for gpu in this.gpus:
        gpu_used = red.hget(server_dynamic, "gpu_" + str(gpu.pk) + "_used")
        gpu_total = red.hget(server_dynamic, "gpu_" + str(gpu.pk) + "_total")
        if gpu_total != None and float(gpu_used) / float(gpu_total) < 0.90:
            score +=  int(float(gpu_used) / float(gpu_total))
            gpu_sum += 1
        elif gpu_total != None:
            score += 0.25
    score = max(2,int(score))
    red.hset(server_dynamic,"score",score)
    return score,gpu_sum


@app.route('/server_test')
def server(server_info, service_status, GPU_status, occupy_status):
    print(request.path)
    print(request.full_path)
    return render_template('server.html', page_title='服务器 - INSIS GPU管理平台', server=server_info,
                           service_status=service_status,
                           GPUs=GPU_status, occupy_status=occupy_status)


# summary page
@app.route('/report',methods=['POST', 'GET'])
def report():
    active = "请选择要查看的数据时段，默认为本周数据"
    # 显存数据，磁盘数据，网络流量数据
    trend_day = [
        {
            'trend_id': 1,
            'y-axis': [12619.7, 12619.8, 12619.8, 12621.8, 12625.1, 12625.9, 13626.5],
            'x-axis': ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00']
        }, {
            'trend_id': 2,
            'y-axis': [720.2124, 720.2126, 720.2126, 720.2184, 720.2214, 720.2224, 722.2246],
            'x-axis': ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00']
        }, {
            'trend_id': 3,
            'y-axis': [3059,3059.2,3059.2,3059.8,3060.1, 3060.2,3060.5],
            'x-axis': ['0:00', '4:00', '8:00', '12:00', '16:00', '20:00', '24:00']
        }
    ]
    trend_week = [
        {
            'trend_id': 1,
            'y-axis': [12619.7, 13219.4, 12612.3, 12719.7, 11949.0, 13949.2, 13629.5],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }, {
            'trend_id': 2,
            'y-axis': [720.2124, 722.246, 720.3104, 720.3132, 720.4005, 720.4000, 720.418],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }, {
            'trend_id': 3,
            'y-axis': [3059.4673588105, 3059.4673589105, 3059.4673589805, 3059.4673580005, 3059.4673587105, 3059.4673569105, 3059.4673389105],
            'x-axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    ]
    trend_month = [
        {
            'trend_id': 1,
            'y-axis': [12619.7, 12719.7, 12949.0,  12989.5],
            'x-axis': [ '四周前', '三周前', '两周前', '上周' ]
        }, {
            'trend_id': 2,
            'y-axis': [721.0864, 719.7104, 720.0132,  720.4000],
            'x-axis': [ '四周前', '三周前', '两周前', '上周']
        }, {
            'trend_id': 3,
            'y-axis': [3059.4673589805, 3059.4673580005, 3059.4673569105,
                       3059.4673389105],
            'x-axis':[ '四周前', '三周前', '两周前', '上周' ]
        }
    ]
    trend_year = [
        {
            'trend_id': 1,
            'y-axis': [12619.7, 12719.7, 12949.0, 12989.5],
            'x-axis': ['四月前', '三月前', '两月前', '上月']
        }, {
            'trend_id': 2,
            'y-axis': [721.0864, 719.7104, 720.0132, 720.4000],
            'x-axis': ['四月前', '三月前', '两月前', '上月']
        }, {
            'trend_id': 3,
            'y-axis': [3059.4673589805, 3059.4673580005, 3059.4673569105,
                       3059.4673389105],
            'x-axis': ['四月前', '三月前', '两月前', '上月']
        }
    ]
    form = LoginForm()
    if form.validate_on_submit():
        tags = form.select
        print('select:{}'.format(tags.data))
        if tags.data == "weekinfo":
            return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=tags.data, form=form,trend = trend_week)
        elif tags.data == "dayinfo":
            return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=tags.data, form=form,
                                   trend=trend)
        elif tags.data == "monthinfo":
            return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=tags.data, form=form,
                                   trend=trend_month)
        elif tags.data == "yearinfo":
            return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=tags.data, form=form,
                                   trend=trend_year)
    return render_template('summary.html', page_title='服务器 - INSIS GPU管理平台', active=active,form=form,trend = trend_week)


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
