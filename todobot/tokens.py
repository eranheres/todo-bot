import yaml
import os.path


def get_tokens():
    if os.path.exists("token.yml"):
        with open(r'token.yml') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        return os.environ