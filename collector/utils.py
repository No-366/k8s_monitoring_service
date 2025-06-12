import time
import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class ResourceParser:
    """시스템 리소스 파싱 및 변환 유틸리티"""
    
    @staticmethod
    def parse_cpu_stats() -> Dict[str, int]:
        """
        /proc/stat에서 CPU 사용량 통계 파싱
        Returns: CPU 시간 정보 (user, nice, system, idle, iowait, irq, softirq)
        """
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                fields = line.split()
                
            return {
                'user': int(fields[1]),
                'nice': int(fields[2]),
                'system': int(fields[3]),
                'idle': int(fields[4]),
                'iowait': int(fields[5]) if len(fields) > 5 else 0,
                'irq': int(fields[6]) if len(fields) > 6 else 0,
                'softirq': int(fields[7]) if len(fields) > 7 else 0,
            }
        except Exception as e:
            logger.error(f"CPU 통계 파싱 실패: {e}")
            return {}
    
    @staticmethod
    def calculate_cpu_percentage(prev_stats: Dict[str, int], curr_stats: Dict[str, int]) -> float:
        """
        두 CPU 통계 간의 CPU 사용률 계산 (백분율)
        """
        if not prev_stats or not curr_stats:
            return 0.0
        
        try:
            prev_total = sum(prev_stats.values())
            curr_total = sum(curr_stats.values())
            
            prev_idle = prev_stats.get('idle', 0)
            curr_idle = curr_stats.get('idle', 0)
            
            total_diff = curr_total - prev_total
            idle_diff = curr_idle - prev_idle
            
            if total_diff == 0:
                return 0.0
            
            cpu_percentage = ((total_diff - idle_diff) / total_diff) * 100
            return max(0.0, min(100.0, cpu_percentage))
        except Exception as e:
            logger.error(f"CPU 사용률 계산 실패: {e}")
            return 0.0
    
    @staticmethod
    def cpu_percentage_to_millicores(cpu_percentage: float, num_cores: int = None) -> int:
        """
        CPU 사용률(%)을 millicores로 변환
        1 core = 1000 millicores
        """
        if num_cores is None:
            num_cores = ResourceParser.get_cpu_count()
        
        # CPU 사용률 * 전체 코어 수 * 10 = millicores
        millicores = int(cpu_percentage * num_cores * 10)
        return millicores
    
    @staticmethod
    def get_cpu_count() -> int:
        """CPU 코어 수 반환"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cores = len([line for line in f if line.startswith('processor')])
            return cores if cores > 0 else 1
        except Exception:
            return 1
    
    @staticmethod
    def parse_memory_info() -> Dict[str, int]:
        """
        /proc/meminfo에서 메모리 정보 파싱
        Returns: 메모리 정보 (bytes 단위)
        """
        try:
            memory_info = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        # kB를 bytes로 변환
                        value_kb = int(re.findall(r'\d+', value)[0])
                        memory_info[key.strip()] = value_kb * 1024
            
            return memory_info
        except Exception as e:
            logger.error(f"메모리 정보 파싱 실패: {e}")
            return {}
    
    @staticmethod
    def calculate_memory_usage(memory_info: Dict[str, int]) -> int:
        """
        메모리 사용량 계산 (bytes)
        """
        if not memory_info:
            return 0
        
        total = memory_info.get('MemTotal', 0)
        free = memory_info.get('MemFree', 0)
        buffers = memory_info.get('Buffers', 0)
        cached = memory_info.get('Cached', 0)
        
        # 실제 사용 중인 메모리 = 전체 - (여유 + 버퍼 + 캐시)
        used = total - (free + buffers + cached)
        return max(0, used)
    
    @staticmethod
    def parse_disk_stats() -> Dict[str, Dict[str, int]]:
        """
        /proc/diskstats에서 디스크 I/O 통계 파싱
        Returns: 디바이스별 I/O 통계
        """
        try:
            disk_stats = {}
            with open('/proc/diskstats', 'r') as f:
                for line in f:
                    fields = line.split()
                    if len(fields) >= 14:
                        device = fields[2]
                        # 주요 디스크 장치만 필터링 (파티션 제외)
                        if re.match(r'^(sd[a-z]|nvme\d+n\d+|vd[a-z])$', device):
                            disk_stats[device] = {
                                'read_sectors': int(fields[5]),
                                'write_sectors': int(fields[9]),
                                'read_time': int(fields[6]),
                                'write_time': int(fields[10])
                            }
            return disk_stats
        except Exception as e:
            logger.error(f"디스크 통계 파싱 실패: {e}")
            return {}
    
    @staticmethod
    def calculate_disk_io(prev_stats: Dict[str, Dict[str, int]], 
                         curr_stats: Dict[str, Dict[str, int]],
                         time_delta: float) -> Dict[str, int]:
        """
        디스크 I/O 속도 계산 (bytes/sec -> 총 bytes)
        """
        if not prev_stats or not curr_stats or time_delta <= 0:
            return {'read_bytes': 0, 'write_bytes': 0}
        
        try:
            total_read_sectors = 0
            total_write_sectors = 0
            
            for device in curr_stats:
                if device in prev_stats:
                    read_diff = curr_stats[device]['read_sectors'] - prev_stats[device]['read_sectors']
                    write_diff = curr_stats[device]['write_sectors'] - prev_stats[device]['write_sectors']
                    
                    total_read_sectors += max(0, read_diff)
                    total_write_sectors += max(0, write_diff)
            
            # 섹터를 바이트로 변환 (1 섹터 = 512 바이트)
            read_bytes = total_read_sectors * 512
            write_bytes = total_write_sectors * 512
            
            return {
                'read_bytes': read_bytes,
                'write_bytes': write_bytes
            }
        except Exception as e:
            logger.error(f"디스크 I/O 계산 실패: {e}")
            return {'read_bytes': 0, 'write_bytes': 0}
    
    @staticmethod
    def parse_network_stats() -> Dict[str, Dict[str, int]]:
        """
        /proc/net/dev에서 네트워크 I/O 통계 파싱
        """
        try:
            network_stats = {}
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # 헤더 2줄 스킵
                
                for line in lines:
                    parts = line.split(':')
                    if len(parts) == 2:
                        interface = parts[0].strip()
                        # 루프백 인터페이스 제외, 실제 네트워크 인터페이스만
                        if interface != 'lo' and not interface.startswith('docker'):
                            values = parts[1].split()
                            if len(values) >= 16:
                                network_stats[interface] = {
                                    'rx_bytes': int(values[0]),
                                    'tx_bytes': int(values[8])
                                }
            return network_stats
        except Exception as e:
            logger.error(f"네트워크 통계 파싱 실패: {e}")
            return {}
    
    @staticmethod
    def calculate_network_io(prev_stats: Dict[str, Dict[str, int]], 
                           curr_stats: Dict[str, Dict[str, int]],
                           time_delta: float) -> Dict[str, int]:
        """
        네트워크 I/O 계산
        """
        if not prev_stats or not curr_stats or time_delta <= 0:
            return {'bytes_sent': 0, 'bytes_recv': 0}
        
        try:
            total_rx_bytes = 0
            total_tx_bytes = 0
            
            for interface in curr_stats:
                if interface in prev_stats:
                    rx_diff = curr_stats[interface]['rx_bytes'] - prev_stats[interface]['rx_bytes']
                    tx_diff = curr_stats[interface]['tx_bytes'] - prev_stats[interface]['tx_bytes']
                    
                    total_rx_bytes += max(0, rx_diff)
                    total_tx_bytes += max(0, tx_diff)
            
            return {
                'bytes_recv': total_rx_bytes,
                'bytes_sent': total_tx_bytes
            }
        except Exception as e:
            logger.error(f"네트워크 I/O 계산 실패: {e}")
            return {'bytes_recv': 0, 'bytes_sent': 0}

class PodResourceParser:
    """파드별 리소스 사용량 파싱"""
    
    @staticmethod
    def get_pod_cgroup_path(pod_uid: str, container_id: str) -> Optional[str]:
        """
        파드/컨테이너의 cgroup 경로 찾기
        """
        # 일반적인 cgroup 경로들
        possible_paths = [
            f"/sys/fs/cgroup/memory/kubepods/pod{pod_uid}/{container_id}",
            f"/sys/fs/cgroup/memory/kubepods.slice/kubepods-pod{pod_uid}.slice",
            f"/sys/fs/cgroup/cpu/kubepods/pod{pod_uid}/{container_id}",
        ]
        
        for path in possible_paths:
            try:
                import os
                if os.path.exists(path):
                    return path
            except:
                continue
        
        return None
    
    @staticmethod
    def parse_pod_memory_usage(cgroup_path: str) -> int:
        """
        cgroup에서 파드 메모리 사용량 파싱
        """
        try:
            memory_usage_path = f"{cgroup_path}/memory.usage_in_bytes"
            with open(memory_usage_path, 'r') as f:
                return int(f.read().strip())
        except Exception as e:
            logger.debug(f"파드 메모리 사용량 파싱 실패: {e}")
            return 0
    
    @staticmethod
    def parse_pod_cpu_usage(cgroup_path: str) -> int:
        """
        cgroup에서 파드 CPU 사용량 파싱 (nanoseconds)
        """
        try:
            cpu_usage_path = f"{cgroup_path}/cpuacct.usage"
            with open(cpu_usage_path, 'r') as f:
                return int(f.read().strip())
        except Exception as e:
            logger.debug(f"파드 CPU 사용량 파싱 실패: {e}")
            return 0

def format_bytes(bytes_value: int) -> str:
    """바이트 수를 사람이 읽기 쉬운 형태로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"

def format_millicores(millicores: int) -> str:
    """millicores를 사람이 읽기 쉬운 형태로 변환"""
    if millicores >= 1000:
        return f"{millicores/1000:.2f} cores"
    return f"{millicores}m"
