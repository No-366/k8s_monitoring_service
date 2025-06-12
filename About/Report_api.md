# k8s-monitor3 API 문서

## 📋 개요

**Base URL**: `http://<NodeIP>:30500`  
**예시**: `http://localhost:30500`  
**Content-Type**: `application/json`  
**인증**: 불필요 (개발/테스트 환경)  

## 🎯 구현된 API 엔드포인트 총괄

### **총 18개 엔드포인트 구현**

| 번호 | 카테고리 | 메서드 | 엔드포인트 | 설명 |
|------|----------|--------|------------|------|
| 1 | Health Check | GET | `/` | 서비스 상태 및 전체 API 목록 |
| 2 | 노드 | GET | `/api/nodes` | 전체 노드 목록 |
| 3 | 노드 | GET | `/api/nodes/<node_name>` | 특정 노드 조회 |
| 4 | 노드 | GET | `/api/nodes/<node_name>/pods` | 노드별 파드 목록 |
| 5 | 노드 | POST | `/api/nodes/<node_name>/metrics` | 노드 메트릭 저장 |
| 6 | 파드 | GET | `/api/pods` | 전체 파드 목록 |
| 7 | 파드 | GET | `/api/pods/<pod_name>` | 특정 파드 조회 |
| 8 | 파드 | POST | `/api/namespaces/<namespace>/pods/<pod_name>/metrics` | 파드 메트릭 저장 |
| 9 | 네임스페이스 | GET | `/api/namespaces` | 전체 네임스페이스 목록 |
| 10 | 네임스페이스 | GET | `/api/namespaces/<namespace>` | 특정 네임스페이스 조회 |
| 11 | 네임스페이스 | GET | `/api/namespaces/<namespace>/pods` | 네임스페이스별 파드 목록 |
| 12 | 디플로이먼트 | GET | `/api/namespaces/<namespace>/deployments` | 네임스페이스별 디플로이먼트 목록 |
| 13 | 디플로이먼트 | GET | `/api/namespaces/<namespace>/deployments/<deployment_name>` | 특정 디플로이먼트 조회 |
| 14 | 디플로이먼트 | GET | `/api/namespaces/<namespace>/deployments/<deployment_name>/pods` | 디플로이먼트별 파드 목록 |
| 15 | 시계열 | GET | `/api/nodes/<node_name>/timeseries` | 노드 시계열 데이터 |
| 16 | 시계열 | GET | `/api/pods/<pod_name>/timeseries` | 파드 시계열 데이터 |
| 17 | 시계열 | GET | `/api/namespaces/<namespace>/timeseries` | 네임스페이스 시계열 데이터 |
| 18 | 시계열 | GET | `/api/deployments/<deployment_name>/timeseries` | 디플로이먼트 시계열 데이터 |

## 🧪 전체 API 테스트 명령어

### **1. Health Check API**
```bash
# 서비스 상태 및 전체 API 목록 확인
curl -s http://localhost:30500/
```

### **2. 노드 APIs (4개)**
```bash
# 전체 노드 목록
curl -s http://localhost:30500/api/nodes

# 특정 노드 조회
curl -s http://localhost:30500/api/nodes/code2-32201345

# 노드별 파드 목록
curl -s http://localhost:30500/api/nodes/code2-32201345/pods

# 노드 메트릭 저장 (POST)
curl -X POST http://localhost:30500/api/nodes/code2-32201345/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_millicores": 250,
    "memory_bytes": 2750000000,
    "disk_io": {
      "read_bytes": 1000,
      "write_bytes": 2000
    },
    "network_io": {
      "bytes_recv": 5000,
      "bytes_sent": 3000
    }
  }'
```

### **3. 파드 APIs (3개)**
```bash
# 전체 파드 목록
curl -s http://localhost:30500/api/pods

# 특정 파드 조회 (모든 네임스페이스 검색)
curl -s http://localhost:30500/api/pods/web-server-1

# 파드 메트릭 저장 (POST)
curl -X POST http://localhost:30500/api/namespaces/default/pods/web-server-1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_millicores": 100,
    "memory_bytes": 500000000,
    "node_name": "code2-32201345",
    "disk_io": {
      "read_bytes": 500,
      "write_bytes": 1000
    },
    "network_io": {
      "bytes_recv": 2000,
      "bytes_sent": 1500
    }
  }'
```

### **4. 네임스페이스 APIs (3개)**
```bash
# 전체 네임스페이스 목록
curl -s http://localhost:30500/api/namespaces

# 특정 네임스페이스 조회
curl -s http://localhost:30500/api/namespaces/default

# 네임스페이스별 파드 목록
curl -s http://localhost:30500/api/namespaces/default/pods
```

### **5. 디플로이먼트 APIs (3개)**
```bash
# 네임스페이스별 디플로이먼트 목록
curl -s http://localhost:30500/api/namespaces/default/deployments

# 특정 디플로이먼트 조회
curl -s http://localhost:30500/api/namespaces/default/deployments/web-server

# 디플로이먼트별 파드 목록
curl -s http://localhost:30500/api/namespaces/default/deployments/web-server/pods
```

### **6. 시계열 APIs (4개)**
```bash
# 노드 시계열 데이터 (최근 5분)
curl -s "http://localhost:30500/api/nodes/code2-32201345/timeseries?window=300"

# 파드 시계열 데이터 (최근 5분)
curl -s "http://localhost:30500/api/pods/web-server-1/timeseries?namespace=default&window=300"

# 네임스페이스 시계열 데이터 (최근 5분)
curl -s "http://localhost:30500/api/namespaces/default/timeseries?window=300"

# 디플로이먼트 시계열 데이터 (최근 5분)
curl -s "http://localhost:30500/api/deployments/web-server/timeseries?namespace=default&window=300"
```

## 🔍 에러 케이스 테스트

### **404 Not Found 테스트**
```bash
# 존재하지 않는 노드
curl -s http://localhost:30500/api/nodes/nonexistent-node

# 존재하지 않는 파드
curl -s http://localhost:30500/api/pods/nonexistent-pod

# 존재하지 않는 네임스페이스
curl -s http://localhost:30500/api/namespaces/nonexistent-namespace

# 존재하지 않는 디플로이먼트
curl -s http://localhost:30500/api/namespaces/default/deployments/nonexistent-deployment
```

### **400 Bad Request 테스트**
```bash
# 잘못된 JSON 형식
curl -X POST http://localhost:30500/api/nodes/code2-32201345/metrics \
  -H "Content-Type: application/json" \
  -d '{"invalid": "json"'

# 필수 필드 누락
curl -X POST http://localhost:30500/api/nodes/code2-32201345/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "memory_bytes": 2750000000
  }'
```

## 📊 예상 응답 형식

### **성공 응답 (200 OK)**
모든 GET API는 다음과 같은 기본 메트릭 구조를 반환합니다:

```json
{
  "timestamp": "2025-06-12T12:35:42.565158Z",
  "cpu_millicores": 163,
  "cpu_cores": 0.163,
  "cpu_percentage": 4.08,
  "memory_bytes": 2748268544,
  "memory_human": {
    "bytes": 2748268544,
    "unit": "GB",
    "value": 2.56
  },
  "disk_io": {
    "read_bytes": 0,
    "write_bytes": 229376
  },
  "disk_io_human": {
    "read": {
      "bytes": 0,
      "unit": "B",
      "value": 0
    },
    "write": {
      "bytes": 229376,
      "unit": "KB",
      "value": 224.0
    }
  },
  "network_io": {
    "bytes_recv": 31154,
    "bytes_sent": 18150
  },
  "network_io_human": {
    "recv": {
      "bytes": 31154,
      "unit": "KB",
      "value": 30.42
    },
    "sent": {
      "bytes": 18150,
      "unit": "KB",
      "value": 17.72
    }
  }
}
```

### **생성 성공 응답 (201 Created)**
```json
{
  "message": "Node code2-32201345 metrics stored successfully"
}
```

### **에러 응답 (404 Not Found)**
```json
{
  "error": "Node nonexistent-node not found"
}
```

### **에러 응답 (400 Bad Request)**
```json
{
  "error": "Missing required field: cpu_millicores"
}
```

## 🚀 배치 테스트 스크립트

### **모든 GET API 한번에 테스트**
```bash
#!/bin/bash

echo "=== k8s-monitor3 API 전체 테스트 ==="
echo

# Health Check
echo "1. Health Check:"
curl -s http://localhost:30500/ | head -5
echo -e "\n"

# 노드 APIs
echo "2. 노드 APIs:"
echo "  - 전체 노드 목록:"
curl -s http://localhost:30500/api/nodes | head -3
echo "  - 특정 노드:"
curl -s http://localhost:30500/api/nodes/code2-32201345 | head -3
echo -e "\n"

# 파드 APIs
echo "3. 파드 APIs:"
echo "  - 전체 파드 목록:"
curl -s http://localhost:30500/api/pods | head -3
echo -e "\n"

# 네임스페이스 APIs
echo "4. 네임스페이스 APIs:"
echo "  - 전체 네임스페이스:"
curl -s http://localhost:30500/api/namespaces | head -3
echo "  - default 네임스페이스:"
curl -s http://localhost:30500/api/namespaces/default | head -3
echo -e "\n"

# 디플로이먼트 APIs
echo "5. 디플로이먼트 APIs:"
echo "  - default 네임스페이스 디플로이먼트:"
curl -s http://localhost:30500/api/namespaces/default/deployments | head -3
echo -e "\n"

# 시계열 APIs
echo "6. 시계열 APIs:"
echo "  - 노드 시계열 (최근 5분):"
curl -s "http://localhost:30500/api/nodes/code2-32201345/timeseries?window=300" | head -3
echo -e "\n"

echo "=== 테스트 완료 ==="
```

## 📝 테스트 체크리스트

### **기본 기능 확인**
- [ ] Health Check API 응답 확인
- [ ] 전체 노드 목록 조회
- [ ] 특정 노드 상세 정보 조회
- [ ] 전체 파드 목록 조회
- [ ] 전체 네임스페이스 목록 조회
- [ ] 특정 네임스페이스 상세 정보 조회

### **집계 기능 확인**
- [ ] 네임스페이스별 디플로이먼트 목록
- [ ] 특정 디플로이먼트 상세 정보
- [ ] 노드별 파드 목록
- [ ] 네임스페이스별 파드 목록
- [ ] 디플로이먼트별 파드 목록

### **시계열 기능 확인**
- [ ] 노드 시계열 데이터 (다양한 window 값)
- [ ] 파드 시계열 데이터
- [ ] 네임스페이스 시계열 데이터
- [ ] 디플로이먼트 시계열 데이터

### **메트릭 저장 확인**
- [ ] 노드 메트릭 POST 요청
- [ ] 파드 메트릭 POST 요청
- [ ] 잘못된 데이터 POST 시 에러 응답

### **에러 처리 확인**
- [ ] 존재하지 않는 리소스 조회 시 404 응답
- [ ] 잘못된 JSON 형식 POST 시 400 응답
- [ ] 필수 필드 누락 시 400 응답

---

**API 문서 버전**: 1.0.0  
**마지막 업데이트**: 2025-06-12 13:00 UTC  
**테스트 환경**: k8s-monitor3 운영 환경
