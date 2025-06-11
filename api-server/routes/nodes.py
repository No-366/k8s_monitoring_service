from flask import Blueprint, jsonify, request
from services.storage import storage_service
from services.compute import metrics_computer

nodes_bp = Blueprint('nodes', __name__)

@nodes_bp.route('/api/nodes', methods=['GET'])
def get_nodes():
    """전체 노드 목록 및 리소스 사용량"""
    try:
        nodes = storage_service.get_all_nodes()
        # 계산된 필드 추가
        enhanced_nodes = [metrics_computer.add_computed_fields(node) for node in nodes]
        return jsonify(enhanced_nodes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('/api/nodes/<node_name>', methods=['GET'])
def get_node(node_name):
    """특정 노드의 리소스 사용량"""
    try:
        node = storage_service.get_node_by_name(node_name)
        if node is None:
            return jsonify({'error': f'Node {node_name} not found'}), 404
        
        # 계산된 필드 추가
        enhanced_node = metrics_computer.add_computed_fields(node)
        return jsonify(enhanced_node), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('/api/nodes/<node_name>/pods', methods=['GET'])
def get_node_pods(node_name):
    """해당 노드에 할당된 모든 파드 목록 및 리소스 사용량"""
    try:
        # 먼저 노드가 존재하는지 확인
        node = storage_service.get_node_by_name(node_name)
        if node is None:
            return jsonify({'error': f'Node {node_name} not found'}), 404
        
        pods = storage_service.get_pods_by_node(node_name)
        # 계산된 필드 추가
        enhanced_pods = [metrics_computer.add_computed_fields(pod) for pod in pods]
        return jsonify(enhanced_pods), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nodes_bp.route('/api/nodes/<node_name>/metrics', methods=['POST'])
def post_node_metrics(node_name):
    """노드 메트릭 수집 (DaemonSet에서 전송)"""
    try:
        # JSON 데이터 검증
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        metrics = request.get_json()
        if not metrics:
            return jsonify({'error': 'Empty JSON body'}), 400
        
        # 필수 필드 검증
        required_fields = ['cpu_millicores', 'memory_bytes', 'disk_io', 'network_io']
        for field in required_fields:
            if field not in metrics:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 메트릭 저장
        success = storage_service.store_node_metrics(node_name, metrics)
        if success:
            return jsonify({'message': f'Node {node_name} metrics stored successfully'}), 201
        else:
            return jsonify({'error': 'Failed to store metrics'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
