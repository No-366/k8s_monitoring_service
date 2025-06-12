cloud-monitoring/
├── api-server/                      # API 서버 코드 (Flask or FastAPI)
│   ├── [main.py]                    # 앱 진입점
│   ├── routes/                      # API 엔드포인트
│   │   ├── [nodes.py]
│   │   ├── [pods.py]
│   │   ├── [namespaces.py]
│   │   └── [deployments.py]
│   ├── services/                    # 데이터 저장/계산 등 로직
│   │   ├── [storage.py]              # 메모리 저장 구조 (deque 등)
│   │   └── [compute.py]               # millicore 변환, 평균, 시계열 추출
│   ├── models/                      # 응답 JSON 스키마 (선택)
│   │   └── response_schemas.py
│   ├── [config.py]                 # 포트, 설정값 모음
│   ├── requirements.txt
│   └── Dockerfile
│
├── collector/                      # DaemonSet 수집기
│   ├── [collector.py]            # 리소스 수집 및 전송
│   ├── [utils.py]                # 측정 단위 변환, 파일 파싱 등
│   ├── requirements.txt
│   ├── [config.py]
│   └── Dockerfile
│
├── manifests/                      # Kubernetes YAML 정의
│   ├── api-server-deployment.yaml
│   ├── api-server-service.yaml
│   ├── collector-daemonset.yaml
│   └── test-pod.yaml               # 리소스 부하/테스트용 파드
│
├── test/                           # 테스트 및 디버깅 스크립트
│
│
├── [README.md]                      # 프로젝트 설명, 실행법
└── [report.md]                      # 디버깅 결과 작성, 메모역할