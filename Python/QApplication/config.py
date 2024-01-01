import os
import json


def read_or_create_config(file):
    # 设定文件路径
    config_path = os.path.join(os.path.dirname(__file__), file)

    # 默认的配置数据
    config = get_config()

    if os.path.exists(config_path):
        # 如果存在，读取并返回内容
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

    config['width'] = config['width'] if is_positive_integer(config.get('width')) else 390
    config['height'] = config['height'] if is_positive_integer(config.get('height')) else 400

    try:
        # 创建一个新的配置文件
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        config['exception'] = str(e)

    return config


def is_positive_integer(value):
    # 检查值是否为整数且大于0
    return isinstance(value, int) and value > 0


def get_config():
    config = {
        "width": 390,
        "height": 400
    }
    return config
