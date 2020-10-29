import os
import socket
from importlib import import_module
from freenit import create_app

from config import configs
from name import app_name

api = import_module(f'{app_name}.api')
config = configs['development']
application = create_app(config)
api.create_api(application)

hostname = socket.gethostname()
port = os.environ.get('FLASK_PORT', 5000)
SWAGGER_PATH = f'{config.OPENAPI_URL_PREFIX}{config.OPENAPI_SWAGGER_UI_PATH}'
SWAGGER_URL = f'http://{hostname}:{port}{SWAGGER_PATH}'
print('*****************************************************')
print('')
print('   Swagger URL:', SWAGGER_URL)
print('')
print('*****************************************************')
