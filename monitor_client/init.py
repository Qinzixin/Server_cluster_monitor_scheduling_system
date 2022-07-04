from monitor_client.main import init
import json


if __name__=="__main__":
    with open("config.json", "r") as f:
        config = json.load(f)
    pk = init(config)
    config["pk"]=pk
    with open("config.json", "w") as f:
        json.dump(config, f)