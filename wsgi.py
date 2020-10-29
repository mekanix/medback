import os
from importlib import import_module

from freenit import create_app

from config import configs
from name import app_name

api = import_module(f'{app_name}.api')
config_name = os.getenv('FLASK_ENV') or 'default'
config = configs[config_name]
application = create_app(config)
api.create_api(application)

if __name__ == '__main__':
    port = os.environ.get('FLASK_PORT', 5000)
    application.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True,
    )
