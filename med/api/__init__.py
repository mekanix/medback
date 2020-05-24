from freenit.api import register_endpoints


def create_api(app):
    from .gallery import blueprint as gallery
    register_endpoints(
        app,
        '/api/v0',
        [
            gallery,
        ],
    )
