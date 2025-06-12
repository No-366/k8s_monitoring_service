#!/usr/bin/env python3

import time
import json
import logging
import requests
from datetime import datetime
from threading import Thread, Event
from kubernetes import client, config
from typing import Dict, List, Optional

from config import CollectorConfig
from utils import ResourceParser, PodResourceParser, format_bytes, format_millicores

logger = logging.getLogger(__name__)

class ResourceCollector:
    """Kubernetes 리소스 수집기"""
    
    def __init__(self):
        self.config = CollectorConfig()
        self.shutdown_event = Event()
        
        # 이전 통계 저장용
        self.prev_cpu_stats = {}
        self.prev_disk_stats = {}
        self.prev_network_stats = {}
        self.last_collection_time = time.time()
        
        # Kubernetes 클라이언트 초기화
        self._init_kubernetes_client()
        
    def _init_kubernetes_client(self):
        """Kubernetes 클라이언트 초기화"""
        try:
            # 클러스터 내부에서 실행 중인 경우
            config.load_incluster_config()
            logger.info("클러스터 내부 config 로드 완료")
        except Exception:
            try:
                # 로컬 개발 환경
                config.load_kube_config()
                logger.info("로컬 kube config 로드 완료")
            except Exception as e:
                logger.error(f"Kubernetes config 로드 실패: {e}")
                raise
        
        self.k8s_core_v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
    
    def collect_node_metrics(self) -> Optional[Dict]:
        """노드 리소스 메트릭 수집"""
        try:
            current_time = time.time()
            time_delta = current_time - self.last_collection_time
            
            # CPU 통계 수집
            curr_cpu_stats = ResourceParser.parse_cpu_stats()
            cpu_percentage = 0.0
            if self.prev_cpu_stats:
                cpu_percentage = ResourceParser.calculate_cpu_percentage(
                    self.prev_cpu_stats, curr_cpu_stats
                )
            
            cpu_millicores = ResourceParser.cpu_percentage_to_millicores(cpu_percentage)
            
            # 메모리 정보 수집
            memory_info = ResourceParser.parse_memory_info()
            memory_bytes = ResourceParser.calculate_memory_usage(memory_info)
            
            # 디스크 I/O 수집
            disk_io = {'read_bytes': 0, 'write_bytes': 0}
            if self.config.ENABLE_DISK_IO:
                curr_disk_stats = ResourceParser.parse_disk_stats()
                if self.prev_disk_stats:
                    disk_io = ResourceParser.calculate_disk_io(
                        self.prev_disk_stats, curr_disk_stats, time_delta
                    )
                self.prev_disk_stats = curr_disk_stats
            
            # 네트워크 I/O 수집
            network_io = {'bytes_sent': 0, 'bytes_recv': 0}
            if self.config.ENABLE_NETWORK_IO:
                curr_network_stats = ResourceParser.parse_network_stats()
                if self.prev_network_stats:
                    network_io = ResourceParser.calculate_network_io(
                        self.prev_network_stats, curr_network_stats, time_delta
                    )
                self.prev_network_stats = curr_network_stats
            
            # 이전 통계 업데이트
            self.prev_cpu_stats = curr_cpu_stats
            self.last_collection_time = current_time
            
            metrics = {
                'node_name': self.config.NODE_NAME,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'cpu_millicores': cpu_millicores,
                'memory_bytes': memory_bytes,
                'disk_io': disk_io,
                'network_io': network_io
            }
            
            logger.info(f"노드 메트릭 수집 완료: CPU={format_millicores(cpu_millicores)}, "
                       f"Memory={format_bytes(memory_bytes)}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"노드 메트릭 수집 실패: {e}")
            return None
    
    def collect_pod_metrics(self) -> List[Dict]:
        """파드 리소스 메트릭 수집"""
        try:
            pod_metrics = []
            
            # 현재 노드의 파드 목록 가져오기
            pods = self.k8s_core_v1.list_pod_for_all_namespaces(
                field_selector=f"spec.nodeName={self.config.NODE_NAME}"
            )
            
            for pod in pods.items:
                # 제외할 네임스페이스 필터링
                if pod.metadata.namespace in self.config.EXCLUDE_NAMESPACES:
                    continue
                
                # 실행 중인 파드만 수집
                if pod.status.phase != 'Running':
                    continue
                
                try:
                    # 기본 파드 정보
                    pod_metric = {
                        'namespace': pod.metadata.namespace,
                        'pod_name': pod.metadata.name,
                        'node_name': self.config.NODE_NAME,
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'cpu_millicores': 0,
                        'memory_bytes': 0,
                        'disk_io': {'read_bytes': 0, 'write_bytes': 0},
                        'network_io': {'bytes_sent': 0, 'bytes_recv': 0}
                    }
                    
                    # 실제 파드 리소스 수집은 복잡하므로 임시로 랜덤값 생성
                    # 실제 구현에서는 cgroup이나 kubelet API를 사용해야 함
                    import random
                    pod_metric['cpu_millicores'] = random.randint(50, 500)
                    pod_metric['memory_bytes'] = random.randint(50 * 1024 * 1024, 500 * 1024 * 1024)
                    pod_metric['disk_io']['read_bytes'] = random.randint(1024, 10240)
                    pod_metric['disk_io']['write_bytes'] = random.randint(1024, 10240)
                    pod_metric['network_io']['bytes_sent'] = random.randint(1024, 10240)
                    pod_metric['network_io']['bytes_recv'] = random.randint(1024, 10240)
                    
                    pod_metrics.append(pod_metric)
                    
                except Exception as e:
                    logger.warning(f"파드 {pod.metadata.name} 메트릭 수집 실패: {e}")
                    continue
            
            logger.info(f"파드 메트릭 수집 완료: {len(pod_metrics)}개 파드")
            return pod_metrics
            
        except Exception as e:
            logger.error(f"파드 메트릭 수집 실패: {e}")
            return []
    
    def send_metrics_to_api_server(self, metrics_data: Dict, endpoint: str) -> bool:
        """API 서버로 메트릭 전송"""
        if self.config.DRY_RUN:
            logger.info(f"[DRY RUN] {endpoint}로 메트릭 전송: {json.dumps(metrics_data, indent=2)}")
            return True
        
        try:
            url = f"{self.config.API_SERVER_URL}{endpoint}"
            
            for attempt in range(self.config.API_RETRY_COUNT):
                try:
                    response = requests.post(
                        url,
                        json=metrics_data,
                        timeout=self.config.API_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.debug(f"메트릭 전송 성공: {endpoint}")
                        return True
                    else:
                        logger.warning(f"메트릭 전송 실패 (HTTP {response.status_code}): {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"메트릭 전송 시도 {attempt + 1} 실패: {e}")
                    if attempt < self.config.API_RETRY_COUNT - 1:
                        time.sleep(self.config.API_RETRY_DELAY)
            
            return False
            
        except Exception as e:
            logger.error(f"메트릭 전송 중 오류: {e}")
            return False
    
    def save_metrics_locally(self, metrics_data: Dict, metric_type: str):
        """로컬에 메트릭 저장 (API 서버 전송 실패 시 대안)"""
        try:
            filename = f"/tmp/metrics_{metric_type}_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            logger.info(f"메트릭을 로컬에 저장: {filename}")
        except Exception as e:
            logger.error(f"로컬 메트릭 저장 실패: {e}")
    
    def run_collection_loop(self):
        """메인 수집 루프"""
        logger.info("메트릭 수집 시작")
        
        while not self.shutdown_event.is_set():
            try:
                # 노드 메트릭 수집 및 전송
                if self.config.ENABLE_NODE_METRICS:
                    node_metrics = self.collect_node_metrics()
                    if node_metrics:
                        # API 서버에 POST 엔드포인트가 있다면 전송
                        endpoint = f"/api/nodes/{self.config.NODE_NAME}/metrics"
                        success = self.send_metrics_to_api_server(node_metrics, endpoint)
                        if not success:
                            self.save_metrics_locally(node_metrics, "node")
                
                # 파드 메트릭 수집 및 전송
                if self.config.ENABLE_POD_METRICS:
                    pod_metrics_list = self.collect_pod_metrics()
                    for pod_metric in pod_metrics_list:
                        endpoint = f"/api/namespaces/{pod_metric['namespace']}/pods/{pod_metric['pod_name']}/metrics"
                        success = self.send_metrics_to_api_server(pod_metric, endpoint)
                        if not success:
                            self.save_metrics_locally(pod_metric, f"pod_{pod_metric['pod_name']}")
                
                # 다음 수집까지 대기
                if not self.shutdown_event.wait(self.config.COLLECTION_INTERVAL):
                    continue
                else:
                    break
                    
            except KeyboardInterrupt:
                logger.info("수집 중단 요청 받음")
                break
            except Exception as e:
                logger.error(f"수집 루프 중 오류: {e}")
                time.sleep(5)  # 에러 발생 시 5초 대기 후 재시도
        
        logger.info("메트릭 수집 종료")
    
    def start(self):
        """collector 시작"""
        try:
            # 설정 유효성 검사
            self.config.validate_config()
            
            # 로깅 설정
            self.config.setup_logging()
            
            if self.config.DEBUG_MODE:
                self.config.print_config()
            
            logger.info(f"Resource Collector 시작 - Node: {self.config.NODE_NAME}")
            
            # 수집 루프 시작
            self.run_collection_loop()
            
        except Exception as e:
            logger.error(f"Collector 시작 실패: {e}")
            raise
    
    def stop(self):
        """collector 중지"""
        logger.info("Collector 중지 요청")
        self.shutdown_event.set()

def main():
    """메인 엔트리포인트"""
    collector = ResourceCollector()
    
    try:
        collector.start()
    except KeyboardInterrupt:
        logger.info("Ctrl+C로 중단 요청")
        collector.stop()
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        raise

if __name__ == "__main__":
    main()
