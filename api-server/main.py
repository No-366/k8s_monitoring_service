# API 서버 진입점
from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# CORS 설정
CORS(app)

# 블루프린트 등록
from routes import register_blueprints
register_blueprints(app)

@app.route('/', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return {
        'status': 'healthy',
        'service': 'Cloud Monitoring API Server',
        'version': '1.0.0',
        'description': 'Real-time API for Kubernetes resource monitoring with DaemonSet collection',
        'endpoints': {
            'nodes': {
                'list_all': 'GET /api/nodes',
                'get_single': 'GET /api/nodes/<node_name>',
                'get_pods': 'GET /api/nodes/<node_name>/pods',
                'post_metrics': 'POST /api/nodes/<node_name>/metrics'
            },
            'pods': {
                'list_all': 'GET /api/pods',
                'get_single': 'GET /api/pods/<pod_name> (searches all namespaces)',
                'post_metrics': 'POST /api/namespaces/<namespace>/pods/<pod_name>/metrics'
            },
            'namespaces': {
                'list_all': 'GET /api/namespaces',
                'get_single': 'GET /api/namespaces/<namespace_name>',
                'get_pods': 'GET /api/namespaces/<namespace_name>/pods'
            },
            'deployments': {
                'list_by_namespace': 'GET /api/namespaces/<namespace>/deployments',
                'get_single': 'GET /api/namespaces/<namespace>/deployments/<deployment_name>',
                'get_pods': 'GET /api/namespaces/<namespace>/deployments/<deployment_name>/pods'
            },
            'timeseries': {
                'nodes': 'GET /api/nodes/<node_name>/timeseries?window=<seconds>',
                'pods': 'GET /api/pods/<pod_name>/timeseries?namespace=<namespace>&window=<seconds>',
                'namespaces': 'GET /api/namespaces/<namespace_name>/timeseries?window=<seconds>',
                'deployments': 'GET /api/deployments/<deployment_name>/timeseries?namespace=<namespace>&window=<seconds>'
            }
        },
        'metrics_collection': {
            'description': 'DaemonSet pods collect metrics and send via POST endpoints',
            'data_aggregation': 'Namespaces and Deployments are calculated from Pod metrics in real-time'
        }
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.get('PORT', 5000), debug=app.config.get('DEBUG', True)) 