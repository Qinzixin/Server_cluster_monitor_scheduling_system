# 监控器说明

## 需求：

```
python=3.8
pykafka
requests
```

## 启动

```bash
# 在项目的顶级目录上
export PYTHONPATH=$PWD

cd monitor_client

# 检查config.json中的web_url是否是web服务器的登陆地址

python main.py
```

如果不能成功，那么需要手动设置IP地址，即

```
python main.py --ip 地址

```