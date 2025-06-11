from flask import Blueprint, jsonify
from services.storage import storage_service
from services.compute import metrics_computer

deployments_bp = Blueprint('deployments', __name__)

@deployments_bp.route('/api/deployments', methods=['GET'])
def get_deployments():
    """전체 배포 목록 및 리소스 사용량 (파드들의 합계)"""
    try:
        deployments = storage_service.get_all_deployments()
        # 계산된 필드 추가
        enhanced_deployments = [metrics_computer.add_computed_fields(deployment) for deployment in deployments]
        return jsonify(enhanced_deployments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/api/namespaces/<namespace>/deployments', methods=['GET'])
def get_namespace_deployments(namespace):
    """특정 네임스페이스의 배포 목록 및 리소스 사용량 (파드들의 합계)"""
    try:
        all_deployments = storage_service.get_all_deployments()
        namespace_deployments = [d for d in all_deployments if d.get('namespace') == namespace]
        
        if not namespace_deployments:
            return jsonify({'error': f'No deployments found in namespace {namespace}'}), 404
        
        # 계산된 필드 추가
        enhanced_deployments = [metrics_computer.add_computed_fields(deployment) for deployment in namespace_deployments]
        return jsonify(enhanced_deployments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/api/namespaces/<namespace>/deployments/<deployment_name>', methods=['GET'])
def get_deployment(namespace, deployment_name):
    """특정 배포의 리소스 사용량 (파드들의 합계)"""
    try:
        deployment = storage_service.get_deployment_by_name(namespace, deployment_name)
        if deployment is None:
            return jsonify({'error': f'Deployment {deployment_name} not found in namespace {namespace}'}), 404
        
        # 계산된 필드 추가
        enhanced_deployment = metrics_computer.add_computed_fields(deployment)
        return jsonify(enhanced_deployment), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deployments_bp.route('/api/namespaces/<namespace>/deployments/<deployment_name>/pods', methods=['GET'])
def get_namespace_deployment_pods(namespace, deployment_name):
    """특정 네임스페이스의 디플로이먼트의 파드 목록 및 리소스 사용량"""
    try:
        # 해당 네임스페이스와 디플로이먼트에 속하는 파드들을 찾기
        deployment_pods = []
        for pod in storage_service.get_all_pods():
            # 파드가 해당 네임스페이스에 속하고, 디플로이먼트 이름이 포함되어 있는 경우
            if (pod.get('namespace') == namespace and 
                deployment_name in pod.get('pod_name', '')):
                # deployment_name 필드 추가
                pod_with_deployment = pod.copy()
                pod_with_deployment['deployment_name'] = deployment_name
                deployment_pods.append(pod_with_deployment)
        
        return jsonify(deployment_pods), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
