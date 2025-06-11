from flask import Blueprint, jsonify, request
from services.storage import storage_service
from services.compute import metrics_computer
from config import Config

timeseries_bp = Blueprint('timeseries', __name__)

@timeseries_bp.route('/api/nodes/timeseries', methods=['GET'])
@timeseries_bp.route('/api/nodes/<node_name>/timeseries', methods=['GET'])
def get_node_timeseries(node_name=None):
    """특정 노드 리소스 시계열 조회"""
    try:
        # window 파라미터 가져오기 (기본값: 1시간)
        window = request.args.get('window', Config.DEFAULT_TIME_WINDOW, type=int)
        
        if node_name is None:
            # 모든 노드의 시계열 데이터
            all_nodes_data = []
            for node in storage_service.latest_nodes.keys():
                node_data = storage_service.get_node_timeseries(node, window)
                all_nodes_data.extend(node_data)
            
            # 시간순 정렬 및 압축
            all_nodes_data.sort(key=lambda x: x.get('timestamp', ''))
            compressed_data = metrics_computer.compress_timeseries(all_nodes_data)
            return jsonify(compressed_data), 200
        else:
            # 특정 노드의 시계열 데이터
            node_data = storage_service.get_node_timeseries(node_name, window)
            if not node_data:
                return jsonify({'error': f'No timeseries data found for node {node_name}'}), 404
            
            # 데이터 압축 적용
            compressed_data = metrics_computer.compress_timeseries(node_data)
            return jsonify(compressed_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timeseries_bp.route('/api/pods/timeseries', methods=['GET'])
@timeseries_bp.route('/api/pods/<pod_name>/timeseries', methods=['GET'])
def get_pod_timeseries(pod_name=None):
    """특정 파드 리소스 시계열 조회"""
    try:
        # window 파라미터 가져오기 (기본값: 1시간)
        window = request.args.get('window', Config.DEFAULT_TIME_WINDOW, type=int)
        namespace = request.args.get('namespace', 'default')
        
        if pod_name is None:
            # 모든 파드의 시계열 데이터
            all_pods_data = []
            for pod_key in storage_service.latest_pods.keys():
                if '/' in pod_key:
                    ns, pname = pod_key.split('/', 1)
                    pod_data = storage_service.get_pod_timeseries(ns, pname, window)
                    all_pods_data.extend(pod_data)
            
            # 시간순 정렬 및 압축
            all_pods_data.sort(key=lambda x: x.get('timestamp', ''))
            compressed_data = metrics_computer.compress_timeseries(all_pods_data)
            return jsonify(compressed_data), 200
        else:
            # 특정 파드의 시계열 데이터
            pod_data = storage_service.get_pod_timeseries(namespace, pod_name, window)
            if not pod_data:
                return jsonify({'error': f'No timeseries data found for pod {pod_name} in namespace {namespace}'}), 404
            
            # 데이터 압축 적용
            compressed_data = metrics_computer.compress_timeseries(pod_data)
            return jsonify(compressed_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timeseries_bp.route('/api/namespaces/timeseries', methods=['GET'])
@timeseries_bp.route('/api/namespaces/<namespace_name>/timeseries', methods=['GET'])
def get_namespace_timeseries(namespace_name=None):
    """특정 네임스페이스 리소스 시계열 조회"""
    try:
        # window 파라미터 가져오기 (기본값: 1시간)
        window = request.args.get('window', Config.DEFAULT_TIME_WINDOW, type=int)
        
        if namespace_name is None:
            # 모든 네임스페이스의 시계열 데이터
            all_ns_data = []
            for ns in storage_service.latest_namespaces.keys():
                ns_data = storage_service.get_namespace_timeseries(ns, window)
                all_ns_data.extend(ns_data)
            
            # 시간순 정렬 및 압축
            all_ns_data.sort(key=lambda x: x.get('timestamp', ''))
            compressed_data = metrics_computer.compress_timeseries(all_ns_data)
            return jsonify(compressed_data), 200
        else:
            # 특정 네임스페이스의 시계열 데이터
            ns_data = storage_service.get_namespace_timeseries(namespace_name, window)
            if not ns_data:
                return jsonify({'error': f'No timeseries data found for namespace {namespace_name}'}), 404
            
            # 데이터 압축 적용
            compressed_data = metrics_computer.compress_timeseries(ns_data)
            return jsonify(compressed_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timeseries_bp.route('/api/deployments/timeseries', methods=['GET'])
@timeseries_bp.route('/api/deployments/<deployment_name>/timeseries', methods=['GET'])
def get_deployment_timeseries(deployment_name=None):
    """특정 디플로이먼트 리소스 시계열 조회"""
    try:
        # window 파라미터 가져오기 (기본값: 1시간)
        window = request.args.get('window', Config.DEFAULT_TIME_WINDOW, type=int)
        namespace = request.args.get('namespace', 'default')
        
        if deployment_name is None:
            # 모든 배포의 시계열 데이터
            all_deployments_data = []
            for deployment_key in storage_service.deployments_data.keys():
                if '/' in deployment_key:
                    ns, dname = deployment_key.split('/', 1)
                    deployment_data = list(storage_service.deployments_data[deployment_key])
                    
                    # compute.py를 활용한 시간 필터링
                    filtered_data = metrics_computer.filter_timeseries_by_window(deployment_data, window)
                    all_deployments_data.extend(filtered_data)
            
            # 시간순 정렬 및 압축
            all_deployments_data.sort(key=lambda x: x.get('timestamp', ''))
            compressed_data = metrics_computer.compress_timeseries(all_deployments_data)
            return jsonify(compressed_data), 200
        else:
            # 특정 배포의 시계열 데이터
            deployment_key = f"{namespace}/{deployment_name}"
            if deployment_key not in storage_service.deployments_data:
                return jsonify({'error': f'No timeseries data found for deployment {deployment_name} in namespace {namespace}'}), 404
            
            # compute.py를 활용한 시간 필터링
            deployment_data = list(storage_service.deployments_data[deployment_key])
            filtered_data = metrics_computer.filter_timeseries_by_window(deployment_data, window)
            
            # 데이터 압축 적용
            compressed_data = metrics_computer.compress_timeseries(filtered_data)
            return jsonify(compressed_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
