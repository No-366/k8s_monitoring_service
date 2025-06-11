import os

class Config:
    """애플리케이션 설정"""
    # 서버 기본 설정
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # 메모리 저장 관련 설정
    MAX_DATA_POINTS = int(os.environ.get('MAX_DATA_POINTS', 1000))
    
    # 시계열 조회 기본 윈도우 (초)
    DEFAULT_TIME_WINDOW = int(os.environ.get('DEFAULT_TIME_WINDOW', 3600))
    
    # POST API 메트릭 수집 관련 설정
    MAX_METRICS_SIZE = int(os.environ.get('MAX_METRICS_SIZE', 1048576))  # 1MB
    METRICS_RETENTION_DAYS = int(os.environ.get('METRICS_RETENTION_DAYS', 7))
    
    # 실시간 계산 관련 설정
    ENABLE_REALTIME_AGGREGATION = os.environ.get('ENABLE_REALTIME_AGGREGATION', 'True').lower() == 'true'
    
    # 로깅 설정
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_METRICS_STORAGE = os.environ.get('LOG_METRICS_STORAGE', 'False').lower() == 'true'
