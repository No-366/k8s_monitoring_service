import os
import logging

class CollectorConfig:
    """Collector 설정 관리 클래스"""
    
    # API 서버 연결 설정
    API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api-server:5000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
    API_RETRY_COUNT = int(os.getenv('API_RETRY_COUNT', '3'))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', '2'))
    
    # 수집 주기 설정 (초 단위)
    COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '30'))
    NODE_METRICS_INTERVAL = int(os.getenv('NODE_METRICS_INTERVAL', '30'))
    POD_METRICS_INTERVAL = int(os.getenv('POD_METRICS_INTERVAL', '30'))
    
    # Kubernetes 설정
    NODE_NAME = os.getenv('NODE_NAME')  # DaemonSet에서 자동 주입
    NAMESPACE_FILTER = os.getenv('NAMESPACE_FILTER', '')  # 빈 문자열이면 모든 네임스페이스
    EXCLUDE_NAMESPACES = os.getenv('EXCLUDE_NAMESPACES', 'kube-system,kube-public').split(',')
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 디버그 및 개발 설정
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'  # 실제 전송하지 않고 로그만
    
    # 리소스 수집 설정
    ENABLE_NODE_METRICS = os.getenv('ENABLE_NODE_METRICS', 'true').lower() == 'true'
    ENABLE_POD_METRICS = os.getenv('ENABLE_POD_METRICS', 'true').lower() == 'true'
    ENABLE_DISK_IO = os.getenv('ENABLE_DISK_IO', 'true').lower() == 'true'
    ENABLE_NETWORK_IO = os.getenv('ENABLE_NETWORK_IO', 'true').lower() == 'true'
    
    @classmethod
    def setup_logging(cls):
        """로깅 설정 초기화"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )
        
        # Kubernetes 클라이언트 로그 레벨 조정
        logging.getLogger('kubernetes').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    @classmethod
    def validate_config(cls):
        """설정값 유효성 검사"""
        if not cls.NODE_NAME:
            raise ValueError("NODE_NAME 환경변수가 설정되지 않았습니다")
        
        if cls.COLLECTION_INTERVAL < 5:
            raise ValueError("COLLECTION_INTERVAL은 최소 5초 이상이어야 합니다")
        
        if not cls.API_SERVER_URL:
            raise ValueError("API_SERVER_URL이 설정되지 않았습니다")
    
    @classmethod
    def print_config(cls):
        """현재 설정값 출력 (디버깅용)"""
        print("=== Collector Configuration ===")
        print(f"API Server URL: {cls.API_SERVER_URL}")
        print(f"Node Name: {cls.NODE_NAME}")
        print(f"Collection Interval: {cls.COLLECTION_INTERVAL}s")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"Dry Run: {cls.DRY_RUN}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("===============================") 