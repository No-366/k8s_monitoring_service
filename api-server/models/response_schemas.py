# API Response Schemas
# API 응답 데이터 구조 정의

from typing import Dict, List, Any, Optional
from datetime import datetime

class ResponseSchema:
    """기본 응답 스키마"""
    
    @staticmethod
    def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """성공 응답 스키마"""
        return {
            'status': 'success',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
    
    @staticmethod
    def error_response(error: str, code: int = 500) -> Dict[str, Any]:
        """에러 응답 스키마"""
        return {
            'status': 'error',
            'error': error,
            'code': code,
            'timestamp': datetime.now().isoformat() + 'Z'
        }

class MetricsSchema:
    """메트릭 데이터 스키마"""
    
    @staticmethod
    def node_metrics_schema() -> Dict[str, str]:
        """노드 메트릭 스키마"""
        return {
            'node_name': 'string',
            'timestamp': 'ISO 8601 string',
            'cpu_millicores': 'integer',
            'cpu_cores': 'float (computed)',
            'memory_bytes': 'integer',
            'memory_gb': 'float (computed)',
            'disk_io': {
                'read_bytes': 'integer',
                'write_bytes': 'integer',
                'read_mb': 'float (computed)',
                'write_mb': 'float (computed)'
            },
            'network_io': {
                'bytes_sent': 'integer',
                'bytes_recv': 'integer',
                'mb_sent': 'float (computed)',
                'mb_recv': 'float (computed)'
            }
        }
    
    @staticmethod
    def pod_metrics_schema() -> Dict[str, str]:
        """파드 메트릭 스키마"""
        schema = MetricsSchema.node_metrics_schema()
        schema.update({
            'namespace': 'string',
            'pod_name': 'string',
            'node_name': 'string'
        })
        return schema
    
    @staticmethod
    def namespace_metrics_schema() -> Dict[str, str]:
        """네임스페이스 메트릭 스키마 (파드들의 집계)"""
        schema = MetricsSchema.node_metrics_schema()
        schema.update({
            'namespace': 'string'
        })
        schema.pop('node_name', None)
        return schema
    
    @staticmethod
    def deployment_metrics_schema() -> Dict[str, str]:
        """배포 메트릭 스키마 (파드들의 집계)"""
        schema = MetricsSchema.namespace_metrics_schema()
        schema.update({
            'deployment_name': 'string'
        })
        return schema

class TimeseriesSchema:
    """시계열 데이터 스키마"""
    
    @staticmethod
    def timeseries_query_params() -> Dict[str, str]:
        """시계열 쿼리 파라미터"""
        return {
            'window': 'integer (seconds, default: 3600)',
            'namespace': 'string (for pods and deployments)',
            'compress': 'boolean (auto-applied for optimization)'
        }
    
    @staticmethod
    def timeseries_response_schema() -> Dict[str, str]:
        """시계열 응답 스키마"""
        return {
            'data': 'array of metric objects',
            'compressed': 'boolean (indicates if data was compressed)',
            'total_points': 'integer',
            'time_range': {
                'start': 'ISO 8601 string',
                'end': 'ISO 8601 string'
            }
        }
