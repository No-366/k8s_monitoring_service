from flask import Blueprint, jsonify, request
from services.storage import storage_service
from services.compute import metrics_computer

pods_bp = Blueprint('pods', __name__)

@pods_bp.route('/api/pods', methods=['GET'])
def get_pods():
    """해당 클러스터에 존재하는 전체 파드 목록 및 리소스 사용량"""
    try:
        pods = storage_service.get_all_pods()
        # 계산된 필드 추가
        enhanced_pods = [metrics_computer.add_computed_fields(pod) for pod in pods]
        return jsonify(enhanced_pods), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pods_bp.route('/api/pods/<pod_name>', methods=['GET'])
def get_pod(pod_name):
    """특정 파드의 실시간 리소스 사용량 (모든 네임스페이스에서 검색)"""
    try:
        # 모든 파드에서 해당 이름의 파드들을 찾기
        matching_pods = []
        all_pods = storage_service.get_all_pods()
        
        for pod in all_pods:
            if pod.get('pod_name') == pod_name:
                # 계산된 필드 추가
                enhanced_pod = metrics_computer.add_computed_fields(pod)
                matching_pods.append(enhanced_pod)
        
        if not matching_pods:
            return jsonify({'error': f'Pod {pod_name} not found in any namespace'}), 404
        
        return jsonify(matching_pods), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pods_bp.route('/api/namespaces/<namespace>/pods/<pod_name>/metrics', methods=['POST'])
def post_pod_metrics(namespace, pod_name):
    """파드 메트릭 수집 (DaemonSet에서 전송)"""
    try:
        # JSON 데이터 검증
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        metrics = request.get_json()
        if not metrics:
            return jsonify({'error': 'Empty JSON body'}), 400
        
        # 필수 필드 검증
        required_fields = ['cpu_millicores', 'memory_bytes', 'disk_io', 'network_io', 'node_name']
        for field in required_fields:
            if field not in metrics:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 메트릭 저장
        success = storage_service.store_pod_metrics(namespace, pod_name, metrics)
        if success:
            return jsonify({'message': f'Pod {pod_name} metrics in namespace {namespace} stored successfully'}), 201
        else:
            return jsonify({'error': 'Failed to store metrics'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
