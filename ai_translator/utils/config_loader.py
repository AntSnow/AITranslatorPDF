import yaml


class ConfigLoader:
    config_path: str

    # 构造函数
    def __init__(self, config_path):
        self.config_path = config_path

    # 加载`yaml`配置文件
    def load_config(self):
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
