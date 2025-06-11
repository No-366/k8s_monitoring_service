from collections import deque, defaultdict
from datetime import datetime, timedelta
import threading
from config import Config
from typing import List, Dict, Any, Optional
from .compute import metrics_computer

class StorageService:
    """메모리 기반 데이터 저장 서비스"""
    
    def __init__(self):
        self.max_data_points = Config.MAX_DATA_POINTS
        self.lock = threading.Lock()
        
        # 각 리소스별 시계열 데이터 저장소
        self.nodes_data = defaultdict(lambda: deque(maxlen=self.max_data_points))
        self.pods_data = defaultdict(lambda: deque(maxlen=self.max_data_points))
        self.namespaces_data = defaultdict(lambda: deque(maxlen=self.max_data_points))
        self.deployments_data = defaultdict(lambda: deque(maxlen=self.max_data_points))
        
        # 최신 데이터 캐시 (빠른 조회용)
        self.latest_nodes = {}
        self.latest_pods = {}
        self.latest_namespaces = {}
        self.latest_deployments = {}
        
        # 초기 샘플 데이터 생성
        self._create_sample_data()
    
    def _create_sample_data(self):
        """샘플 데이터 생성"""
        import random
        
        # 샘플 노드 데이터
        sample_nodes = ['node-1', 'node-2']
        for node in sample_nodes:
            data = {
                'node_name': node,
                'timestamp': datetime.now().isoformat() + 'Z',
                'cpu_millicores': random.randint(1500, 2500),
                'memory_bytes': random.randint(3000000000, 5000000000),
                'disk_io': {
                    'read_bytes': random.randint(80000000, 120000000),
                    'write_bytes': random.randint(300000000, 600000000)
                },
                'network_io': {
                    'bytes_sent': random.randint(10000000, 30000000),
                    'bytes_recv': random.randint(20000000, 40000000)
                }
            }
            self.latest_nodes[node] = data
            self.nodes_data[node].append(data.copy())
        
        # 샘플 파드 데이터
        sample_pods = [
            {'namespace': 'default', 'pod_name': 'web-server-1', 'node_name': 'node-1'},
            {'namespace': 'default', 'pod_name': 'app-backend-1', 'node_name': 'node-2'},
            {'namespace': 'monitoring', 'pod_name': 'prometheus-1', 'node_name': 'node-1'}
        ]
        
        for pod in sample_pods:
            data = {
                'namespace': pod['namespace'],
                'pod_name': pod['pod_name'],
                'node_name': pod['node_name'],
                'timestamp': datetime.now().isoformat() + 'Z',
                'cpu_millicores': random.randint(200, 600),
                'memory_bytes': random.randint(500000000, 1500000000),
                'disk_io': {
                    'read_bytes': random.randint(1000000, 5000000),
                    'write_bytes': random.randint(500000, 3000000)
                },
                'network_io': {
                    'bytes_sent': random.randint(100000, 500000),
                    'bytes_recv': random.randint(200000, 800000)
                }
            }
            pod_key = f"{pod['namespace']}/{pod['pod_name']}"
            self.latest_pods[pod_key] = data
            self.pods_data[pod_key].append(data.copy())
        
        # 샘플 네임스페이스 데이터
        sample_namespaces = ['default', 'monitoring']
        for ns in sample_namespaces:
            data = {
                'namespace': ns,
                'timestamp': datetime.now().isoformat() + 'Z',
                'cpu_millicores': random.randint(800, 1500),
                'memory_bytes': random.randint(1000000000, 3000000000),
                'disk_io': {
                    'read_bytes': random.randint(500000, 2000000),
                    'write_bytes': random.randint(1000000, 3000000)
                },
                'network_io': {
                    'bytes_sent': random.randint(5000000, 15000000),
                    'bytes_recv': random.randint(40000000, 90000000)
                }
            }
            self.latest_namespaces[ns] = data
            self.namespaces_data[ns].append(data.copy())
        
        # 샘플 디플로이먼트 데이터
        sample_deployments = [
            {'namespace': 'default', 'deployment_name': 'web-server'},
            {'namespace': 'default', 'deployment_name': 'app-backend'},
            {'namespace': 'monitoring', 'deployment_name': 'prometheus'}
        ]
        
        for deployment in sample_deployments:
            data = {
                'namespace': deployment['namespace'],
                'deployment_name': deployment['deployment_name'],
                'timestamp': datetime.now().isoformat() + 'Z',
                'cpu_millicores': random.randint(400, 800),
                'memory_bytes': random.randint(1000000000, 2500000000),
                'disk_io': {
                    'read_bytes': random.randint(2000000, 8000000),
                    'write_bytes': random.randint(1000000, 4000000)
                },
                'network_io': {
                    'bytes_sent': random.randint(500000, 1500000),
                    'bytes_recv': random.randint(400000, 800000)
                }
            }
            deployment_key = f"{deployment['namespace']}/{deployment['deployment_name']}"
            self.latest_deployments[deployment_key] = data
            self.deployments_data[deployment_key].append(data.copy())
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """모든 노드의 최신 데이터 조회"""
        with self.lock:
            return list(self.latest_nodes.values())
    
    def get_node_by_name(self, node_name: str) -> Optional[Dict[str, Any]]:
        """특정 노드의 최신 데이터 조회"""
        with self.lock:
            return self.latest_nodes.get(node_name)
    
    def get_all_pods(self) -> List[Dict[str, Any]]:
        """모든 파드의 최신 데이터 조회"""
        with self.lock:
            return list(self.latest_pods.values())
    
    def get_pod_by_name(self, namespace: str, pod_name: str) -> Optional[Dict[str, Any]]:
        """특정 파드의 최신 데이터 조회"""
        with self.lock:
            pod_key = f"{namespace}/{pod_name}"
            return self.latest_pods.get(pod_key)
    
    def get_pods_by_node(self, node_name: str) -> List[Dict[str, Any]]:
        """특정 노드의 파드들 조회"""
        with self.lock:
            return [pod for pod in self.latest_pods.values() 
                    if pod.get('node_name') == node_name]
    
    def get_pods_by_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        """특정 네임스페이스의 파드들 조회"""
        with self.lock:
            return [pod for pod in self.latest_pods.values() 
                    if pod.get('namespace') == namespace]
    
    def get_all_namespaces(self) -> List[Dict[str, Any]]:
        """모든 네임스페이스의 최신 데이터 조회 (소속 파드들의 합계 계산)"""
        with self.lock:
            namespaces = {}
            
            # 모든 파드를 순회하면서 네임스페이스별로 그룹화
            for pod in self.latest_pods.values():
                ns = pod.get('namespace')
                if ns not in namespaces:
                    namespaces[ns] = []
                namespaces[ns].append(pod)
            
            # 각 네임스페이스별로 집계 계산
            result = []
            for ns, pods in namespaces.items():
                aggregated = metrics_computer.aggregate_pod_metrics(pods)
                aggregated.update({
                    'namespace': ns,
                    'timestamp': datetime.now().isoformat() + 'Z'
                })
                result.append(aggregated)
            
            return result
    
    def get_namespace_by_name(self, namespace: str) -> Optional[Dict[str, Any]]:
        """특정 네임스페이스의 최신 데이터 조회 (소속 파드들의 합계 계산)"""
        with self.lock:
            # 해당 네임스페이스의 파드들을 찾기
            namespace_pods = [pod for pod in self.latest_pods.values() 
                            if pod.get('namespace') == namespace]
            
            if not namespace_pods:
                return None
            
            # 집계 계산
            aggregated = metrics_computer.aggregate_pod_metrics(namespace_pods)
            aggregated.update({
                'namespace': namespace,
                'timestamp': datetime.now().isoformat() + 'Z'
            })
            
            return aggregated
    
    def get_all_deployments(self) -> List[Dict[str, Any]]:
        """모든 배포의 최신 데이터 조회 (소속 파드들의 합계 계산)"""
        with self.lock:
            deployments = {}
            
            # 모든 파드를 순회하면서 디플로이먼트별로 그룹화
            for pod in self.latest_pods.values():
                pod_name = pod.get('pod_name', '')
                namespace = pod.get('namespace', '')
                
                # 파드 이름에서 디플로이먼트 이름 추출
                deployment_name = None
                if 'web-server' in pod_name:
                    deployment_name = 'web-server'
                elif 'app-backend' in pod_name:
                    deployment_name = 'app-backend'
                elif 'prometheus' in pod_name:
                    deployment_name = 'prometheus'
                
                if deployment_name:
                    deployment_key = f"{namespace}/{deployment_name}"
                    if deployment_key not in deployments:
                        deployments[deployment_key] = {
                            'namespace': namespace,
                            'deployment_name': deployment_name,
                            'pods': []
                        }
                    deployments[deployment_key]['pods'].append(pod)
            
            # 각 디플로이먼트별로 집계 계산
            result = []
            for deployment_key, deployment_info in deployments.items():
                aggregated = metrics_computer.aggregate_pod_metrics(deployment_info['pods'])
                aggregated.update({
                    'namespace': deployment_info['namespace'],
                    'deployment_name': deployment_info['deployment_name'],
                    'timestamp': datetime.now().isoformat() + 'Z'
                })
                result.append(aggregated)
            
            return result
    
    def get_deployment_by_name(self, namespace: str, deployment_name: str) -> Optional[Dict[str, Any]]:
        """특정 배포의 최신 데이터 조회 (소속 파드들의 합계 계산)"""
        with self.lock:
            # 해당 디플로이먼트의 파드들을 찾기
            deployment_pods = [pod for pod in self.latest_pods.values() 
                             if (pod.get('namespace') == namespace and 
                                 deployment_name in pod.get('pod_name', ''))]
            
            if not deployment_pods:
                return None
            
            # 집계 계산
            aggregated = metrics_computer.aggregate_pod_metrics(deployment_pods)
            aggregated.update({
                'namespace': namespace,
                'deployment_name': deployment_name,
                'timestamp': datetime.now().isoformat() + 'Z'
            })
            
            return aggregated
    
    def get_node_timeseries(self, node_name: str, window_seconds: int) -> List[Dict[str, Any]]:
        """노드 시계열 데이터 조회"""
        with self.lock:
            if node_name not in self.nodes_data:
                return []
            
            # compute.py 활용하여 필터링
            return metrics_computer.filter_timeseries_by_window(
                list(self.nodes_data[node_name]), window_seconds
            )
    
    def get_pod_timeseries(self, namespace: str, pod_name: str, window_seconds: int) -> List[Dict[str, Any]]:
        """파드 시계열 데이터 조회"""
        with self.lock:
            pod_key = f"{namespace}/{pod_name}"
            if pod_key not in self.pods_data:
                return []
            
            # compute.py 활용하여 필터링
            return metrics_computer.filter_timeseries_by_window(
                list(self.pods_data[pod_key]), window_seconds
            )
    
    def get_namespace_timeseries(self, namespace: str, window_seconds: int) -> List[Dict[str, Any]]:
        """네임스페이스 시계열 데이터 조회"""
        with self.lock:
            if namespace not in self.namespaces_data:
                return []
            
            # compute.py 활용하여 필터링
            return metrics_computer.filter_timeseries_by_window(
                list(self.namespaces_data[namespace]), window_seconds
            )
    
    def get_deployment_timeseries(self, namespace: str, deployment_name: str, window_seconds: int) -> List[Dict[str, Any]]:
        """디플로이먼트 시계열 데이터 조회"""
        with self.lock:
            deployment_key = f"{namespace}/{deployment_name}"
            if deployment_key not in self.deployments_data:
                return []
            
            # compute.py 활용하여 필터링
            return metrics_computer.filter_timeseries_by_window(
                list(self.deployments_data[deployment_key]), window_seconds
            )
    
    # ==================== POST 메트릭 저장 메서드들 ====================
    
    def store_node_metrics(self, node_name: str, metrics: Dict[str, Any]) -> bool:
        """노드 메트릭 저장 (POST용)"""
        try:
            with self.lock:
                # 타임스탬프 추가
                metrics['node_name'] = node_name
                metrics['timestamp'] = datetime.now().isoformat() + 'Z'
                
                # 최신 데이터 업데이트
                self.latest_nodes[node_name] = metrics.copy()
                
                # 시계열 데이터에 추가
                self.nodes_data[node_name].append(metrics.copy())
                
                return True
        except Exception as e:
            print(f"Error storing node metrics: {e}")
            return False
    
    def store_pod_metrics(self, namespace: str, pod_name: str, metrics: Dict[str, Any]) -> bool:
        """파드 메트릭 저장 (POST용)"""
        try:
            with self.lock:
                # 필수 필드 추가
                metrics['namespace'] = namespace
                metrics['pod_name'] = pod_name
                metrics['timestamp'] = datetime.now().isoformat() + 'Z'
                
                pod_key = f"{namespace}/{pod_name}"
                
                # 최신 데이터 업데이트
                self.latest_pods[pod_key] = metrics.copy()
                
                # 시계열 데이터에 추가
                self.pods_data[pod_key].append(metrics.copy())
                
                return True
        except Exception as e:
            print(f"Error storing pod metrics: {e}")
            return False

# 전역 인스턴스
storage_service = StorageService()
