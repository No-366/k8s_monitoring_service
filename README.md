# Cloud Monitoring System

Kubernetes 클러스터의 리소스 사용량을 조회할 수 있는 간단한 REST API 시스템입니다.

## 프로젝트 구조

```
cloud-monitoring/
├── api-server/              # Flask API 서버
│   ├── main.py             # 앱 진입점
│   ├── routes/             # API 엔드포인트
│   ├── services/           # 비즈니스 로직
│   ├── models/             # 데이터 모델
│   └── config.py           # 설정
├── collector/              # DaemonSet 리소스 수집기
│   ├── collector.py        # 메인 수집기
│   └── utils.py           # 유틸리티 함수
├── manifests/              # Kubernetes 배포 파일
├── test/                   # 테스트 스크립트
└── data/                   # 로컬 데이터 저장소
```

## 주요 기능

- **리소스 조회**: 노드, 파드, 네임스페이스, 배포 정보 조회
- **시계열 데이터**: 시간대별 리소스 사용량 조회
- **RESTful API**: 표준 REST API를 통한 데이터 접근
- **샘플 데이터**: 즉시 테스트 가능한 샘플 데이터 제공

## API 엔드포인트

### 노드 리소스
- `GET /api/nodes` - 전체 노드 목록 및 리소스 사용량
- `GET /api/nodes/<node_name>` - 특정 노드의 리소스 사용량
- `GET /api/nodes/<node_name>/pods` - 특정 노드의 파드 목록

### 파드 리소스
- `GET /api/pods` - 전체 파드 목록 및 리소스 사용량
- `GET /api/pods/<pod_name>?namespace=<namespace>` - 특정 파드의 리소스 사용량

### 네임스페이스
- `GET /api/namespaces` - 전체 네임스페이스 목록 및 리소스 사용량
- `GET /api/namespaces/<namespace_name>` - 특정 네임스페이스의 리소스 사용량
- `GET /api/namespaces/<namespace_name>/pods` - 특정 네임스페이스의 파드 목록

### 배포
- `GET /api/deployments` - 전체 배포 목록 및 리소스 사용량
- `GET /api/deployments/<deployment_name>?namespace=<namespace>` - 특정 배포의 리소스 사용량

### 시계열 데이터
- `GET /api/nodes/<node_name>/timeseries?window=<seconds>` - 노드 시계열 데이터
- `GET /api/pods/<pod_name>/timeseries?namespace=<namespace>&window=<seconds>` - 파드 시계열 데이터
- `GET /api/namespaces/<namespace_name>/timeseries?window=<seconds>` - 네임스페이스 시계열 데이터
- `GET /api/deployments/<deployment_name>/timeseries?namespace=<namespace>&window=<seconds>` - 배포 시계열 데이터

## 로컬 개발 환경 설정

### 1. 의존성 설치

```bash
# API 서버 의존성
cd api-server
pip install -r requirements.txt
```

### 2. API 서버 실행

```bash
cd api-server
python3 main.py
```

API 서버가 `http://localhost:5000`에서 실행됩니다.

### 3. 헬스 체크

```bash
curl http://localhost:5000/
```

## Docker 빌드

### API 서버 이미지 빌드
```bash
cd api-server
docker build -t cloud-monitoring/api-server:latest .
```

## Kubernetes 배포

### API 서버 배포
```bash
kubectl apply -f manifests/api-server-deployment.yaml
kubectl apply -f manifests/api-server-service.yaml
```

## 테스트

### API 기능 테스트
```bash
cd test
chmod +x run_stress_test.sh
./run_stress_test.sh
```

### 커스텀 URL로 테스트
```bash
API_BASE_URL=http://localhost:5000 ./run_stress_test.sh
```

## 환경 변수

### API 서버
- `PORT`: 서버 포트 (기본값: 5000)
- `DEBUG`: 디버그 모드 (기본값: True)
- `MAX_DATA_POINTS`: 최대 데이터 포인트 수 (기본값: 1000)
- `DEFAULT_TIME_WINDOW`: 기본 시계열 조회 윈도우 (기본값: 3600초)

## 샘플 데이터

시스템 시작 시 다음과 같은 샘플 데이터가 자동으로 생성됩니다:

### 노드
- `node-1`, `node-2`

### 파드
- `web-server-1` (default 네임스페이스, node-1)
- `app-backend-1` (default 네임스페이스, node-2)
- `prometheus-1` (monitoring 네임스페이스, node-1)

### 네임스페이스
- `default`, `monitoring`

## 모니터링 및 로그

### API 서버 로그 확인
```bash
kubectl logs -f deployment/api-server
```

### 리소스 조회 예시
```bash
# 모든 노드 조회
curl http://localhost:5000/api/nodes | jq

# 특정 노드 조회
curl http://localhost:5000/api/nodes/node-1 | jq

# 시계열 데이터 조회 (최근 1시간)
curl "http://localhost:5000/api/nodes/node-1/timeseries?window=3600" | jq
```

## 문제 해결

### 일반적인 문제
1. **API 서버 연결 실패**: 서비스가 정상적으로 실행되고 있는지 확인
2. **404 오류**: 요청한 리소스 이름이 정확한지 확인
3. **빈 응답**: 샘플 데이터가 생성되었는지 확인

### 디버깅
```bash
# API 서버 상태 확인
curl http://localhost:5000/

# 헬스 체크
curl http://localhost:5000/ | jq
```

## 라이센스

MIT License
