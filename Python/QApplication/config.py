import os
import json


def read_or_create_config(config_path):
    # 默认的配置数据
    config = get_config()

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            old_config = json.load(file)
            config.update(old_config)

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
        'application': 'Pyside6',
        "width": 390,
        "height": 400
    }
    return config
