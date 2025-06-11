from .nodes import nodes_bp
from .pods import pods_bp
from .namespaces import namespaces_bp
from .deployments import deployments_bp
from .timeseries import timeseries_bp

def register_blueprints(app):
    """Flask 앱에 블루프린트 등록"""
    app.register_blueprint(nodes_bp)
    app.register_blueprint(pods_bp)
    app.register_blueprint(namespaces_bp)
    app.register_blueprint(deployments_bp)
    app.register_blueprint(timeseries_bp) 