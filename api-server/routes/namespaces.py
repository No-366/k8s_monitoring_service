from flask import Blueprint, jsonify
from services.storage import storage_service
from services.compute import metrics_computer

namespaces_bp = Blueprint('namespaces', __name__)

@namespaces_bp.route('/api/namespaces', methods=['GET'])
def get_namespaces():
    """전체 네임스페이스 목록 및 리소스 사용량 (파드들의 합계)"""
    try:
        namespaces = storage_service.get_all_namespaces()
        # 계산된 필드 추가
        enhanced_namespaces = [metrics_computer.add_computed_fields(ns) for ns in namespaces]
        return jsonify(enhanced_namespaces), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@namespaces_bp.route('/api/namespaces/<namespace_name>', methods=['GET'])
def get_namespace(namespace_name):
    """특정 네임스페이스의 리소스 사용량 (파드들의 합계)"""
    try:
        namespace_data = storage_service.get_namespace_by_name(namespace_name)
        if namespace_data is None:
            return jsonify({'error': f'Namespace {namespace_name} not found'}), 404
        
        # 계산된 필드 추가
        enhanced_namespace = metrics_computer.add_computed_fields(namespace_data)
        return jsonify(enhanced_namespace), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@namespaces_bp.route('/api/namespaces/<namespace_name>/pods', methods=['GET'])
def get_namespace_pods(namespace_name):
    """특정 네임스페이스의 모든 파드 목록 및 리소스 사용량"""
    try:
        pods = storage_service.get_pods_by_namespace(namespace_name)
        if not pods:
            return jsonify({'error': f'No pods found in namespace {namespace_name}'}), 404
        
        # 계산된 필드 추가
        enhanced_pods = [metrics_computer.add_computed_fields(pod) for pod in pods]
        return jsonify(enhanced_pods), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
