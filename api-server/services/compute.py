"""
컴퓨팅 및 계산 유틸리티 모듈
메트릭 계산, 집계, 단위 변환, 시계열 처리 등을 담당
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics


class MetricsComputer:
    """메트릭 계산 및 처리 유틸리티 클래스"""
    
    @staticmethod
    def millicores_to_cores(millicores: int) -> float:
        """밀리코어를 코어로 변환"""
        return round(millicores / 1000.0, 3)
    
    @staticmethod
    def cores_to_millicores(cores: float) -> int:
        """코어를 밀리코어로 변환"""
        return int(cores * 1000)
    
    @staticmethod
    def bytes_to_human_readable(bytes_value: int) -> Dict[str, Any]:
        """바이트를 사람이 읽기 쉬운 단위로 변환"""
        units = [
            ('TB', 1024**4),
            ('GB', 1024**3),
            ('MB', 1024**2),
            ('KB', 1024),
            ('B', 1)
        ]
        
        for unit, size in units:
            if bytes_value >= size:
                value = round(bytes_value / size, 2)
                return {
                    'value': value,
                    'unit': unit,
                    'bytes': bytes_value
                }
        
        return {'value': 0, 'unit': 'B', 'bytes': 0}
    
    @staticmethod
    def calculate_cpu_percentage(millicores: int, total_millicores: int = 4000) -> float:
        """CPU 사용률 계산 (기본 4코어 기준)"""
        if total_millicores <= 0:
            return 0.0
        return round((millicores / total_millicores) * 100, 2)
    
    @staticmethod
    def calculate_memory_percentage(used_bytes: int, total_bytes: int) -> float:
        """메모리 사용률 계산"""
        if total_bytes <= 0:
            return 0.0
        return round((used_bytes / total_bytes) * 100, 2)
    
    @staticmethod
    def aggregate_pod_metrics(pods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """파드들의 메트릭을 집계하여 합계 계산"""
        if not pods:
            return {
                'cpu_millicores': 0,
                'memory_bytes': 0,
                'disk_io': {'read_bytes': 0, 'write_bytes': 0},
                'network_io': {'bytes_sent': 0, 'bytes_recv': 0}
            }
        
        total_cpu = 0
        total_memory = 0
        total_disk_read = 0
        total_disk_write = 0
        total_net_sent = 0
        total_net_recv = 0
        
        for pod in pods:
            total_cpu += pod.get('cpu_millicores', 0)
            total_memory += pod.get('memory_bytes', 0)
            
            disk_io = pod.get('disk_io', {})
            total_disk_read += disk_io.get('read_bytes', 0)
            total_disk_write += disk_io.get('write_bytes', 0)
            
            network_io = pod.get('network_io', {})
            total_net_sent += network_io.get('bytes_sent', 0)
            total_net_recv += network_io.get('bytes_recv', 0)
        
        return {
            'cpu_millicores': total_cpu,
            'memory_bytes': total_memory,
            'disk_io': {
                'read_bytes': total_disk_read,
                'write_bytes': total_disk_write
            },
            'network_io': {
                'bytes_sent': total_net_sent,
                'bytes_recv': total_net_recv
            }
        }
    
    @staticmethod
    def calculate_average_metrics(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """메트릭 리스트의 평균값 계산"""
        if not metrics_list:
            return {}
        
        cpu_values = [m.get('cpu_millicores', 0) for m in metrics_list]
        memory_values = [m.get('memory_bytes', 0) for m in metrics_list]
        
        disk_read_values = [m.get('disk_io', {}).get('read_bytes', 0) for m in metrics_list]
        disk_write_values = [m.get('disk_io', {}).get('write_bytes', 0) for m in metrics_list]
        
        net_sent_values = [m.get('network_io', {}).get('bytes_sent', 0) for m in metrics_list]
        net_recv_values = [m.get('network_io', {}).get('bytes_recv', 0) for m in metrics_list]
        
        return {
            'cpu_millicores': int(statistics.mean(cpu_values)) if cpu_values else 0,
            'memory_bytes': int(statistics.mean(memory_values)) if memory_values else 0,
            'disk_io': {
                'read_bytes': int(statistics.mean(disk_read_values)) if disk_read_values else 0,
                'write_bytes': int(statistics.mean(disk_write_values)) if disk_write_values else 0
            },
            'network_io': {
                'bytes_sent': int(statistics.mean(net_sent_values)) if net_sent_values else 0,
                'bytes_recv': int(statistics.mean(net_recv_values)) if net_recv_values else 0
            }
        }
    
    @staticmethod
    def filter_timeseries_by_window(data: List[Dict[str, Any]], window_seconds: int) -> List[Dict[str, Any]]:
        """시계열 데이터를 시간 윈도우로 필터링"""
        if not data or window_seconds <= 0:
            return []
        
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        filtered_data = []
        
        for item in data:
            try:
                timestamp_str = item.get('timestamp', '')
                # ISO 포맷 파싱 (Z 제거)
                data_time = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                if data_time >= cutoff_time:
                    filtered_data.append(item)
            except (ValueError, TypeError):
                # 잘못된 타임스탬프는 건너뛰기
                continue
        
        return sorted(filtered_data, key=lambda x: x.get('timestamp', ''))
    
    @staticmethod
    def compress_timeseries(data: List[Dict[str, Any]], max_points: int = 100) -> List[Dict[str, Any]]:
        """시계열 데이터 압축 (너무 많은 포인트일 때 샘플링)"""
        if not data or len(data) <= max_points:
            return data
        
        # 균등하게 샘플링
        step = len(data) // max_points
        compressed = []
        
        for i in range(0, len(data), step):
            compressed.append(data[i])
        
        # 마지막 포인트도 포함
        if data[-1] not in compressed:
            compressed.append(data[-1])
        
        return compressed
    
    @staticmethod
    def calculate_resource_trend(data: List[Dict[str, Any]], metric_key: str) -> Dict[str, Any]:
        """리소스 사용 트렌드 계산 (증가/감소/안정)"""
        if len(data) < 2:
            return {'trend': 'insufficient_data', 'change_rate': 0}
        
        # 첫 번째와 마지막 값 비교
        first_value = data[0].get(metric_key, 0)
        last_value = data[-1].get(metric_key, 0)
        
        if first_value == 0:
            return {'trend': 'insufficient_data', 'change_rate': 0}
        
        change_rate = ((last_value - first_value) / first_value) * 100
        
        if abs(change_rate) < 5:  # 5% 미만은 안정
            trend = 'stable'
        elif change_rate > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'change_rate': round(change_rate, 2),
            'first_value': first_value,
            'last_value': last_value
        }
    
    @staticmethod
    def add_computed_fields(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """메트릭에 계산된 필드들 추가 (사용률, 사람이 읽기 쉬운 단위 등)"""
        enhanced_metrics = metrics.copy()
        
        # CPU 관련
        if 'cpu_millicores' in metrics:
            enhanced_metrics['cpu_cores'] = MetricsComputer.millicores_to_cores(metrics['cpu_millicores'])
            enhanced_metrics['cpu_percentage'] = MetricsComputer.calculate_cpu_percentage(metrics['cpu_millicores'])
        
        # 메모리 관련
        if 'memory_bytes' in metrics:
            enhanced_metrics['memory_human'] = MetricsComputer.bytes_to_human_readable(metrics['memory_bytes'])
        
        # 디스크 I/O 관련
        if 'disk_io' in metrics:
            disk_io = metrics['disk_io']
            enhanced_metrics['disk_io_human'] = {
                'read': MetricsComputer.bytes_to_human_readable(disk_io.get('read_bytes', 0)),
                'write': MetricsComputer.bytes_to_human_readable(disk_io.get('write_bytes', 0))
            }
        
        # 네트워크 I/O 관련
        if 'network_io' in metrics:
            network_io = metrics['network_io']
            enhanced_metrics['network_io_human'] = {
                'sent': MetricsComputer.bytes_to_human_readable(network_io.get('bytes_sent', 0)),
                'recv': MetricsComputer.bytes_to_human_readable(network_io.get('bytes_recv', 0))
            }
        
        return enhanced_metrics


# 전역 인스턴스
metrics_computer = MetricsComputer()
