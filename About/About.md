cloud-monitoring/
├── api-server/                      # API 서버 코드 (Flask or FastAPI)
│   ├── [main.py](http://main.py/)                      # 앱 진입점
│   ├── routes/                      # API 엔드포인트
│   │   ├── [nodes.py](http://nodes.py/)
│   │   ├── [pods.py](http://pods.py/)
│   │   ├── [namespaces.py](http://namespaces.py/)
│   │   └── [deployments.py](http://deployments.py/)
│   ├── services/                    # 데이터 저장/계산 등 로직
│   │   ├── [storage.py](http://storage.py/)               # 메모리 저장 구조 (deque 등)
│   │   └── [compute.py](http://compute.py/)               # millicore 변환, 평균, 시계열 추출
│   ├── models/                      # 응답 JSON 스키마 (선택)
│   │   └── response_schemas.py
│   ├── [config.py](http://config.py/)                    # 포트, 설정값 모음
│   ├── requirements.txt
│   └── Dockerfile
│
├── collector/                      # DaemonSet 수집기
│   ├── [collector.py](http://collector.py/)                # 리소스 수집 및 전송
│   ├── [utils.py](http://utils.py/)                    # 측정 단위 변환, 파일 파싱 등
│   ├── requirements.txt
│   └── Dockerfile
│
├── manifests/                      # Kubernetes YAML 정의
│   ├── api-server-deployment.yaml
│   ├── api-server-service.yaml
│   ├── collector-daemonset.yaml
│   └── test-pod.yaml               # 리소스 부하/테스트용 파드
│
├── test/                           # 테스트 및 디버깅 스크립트
│   ├── run_stress_test.sh → API 기능 확인용 : 실제 수집기가 데이터를 보내기 전에 curl로 POST 요청 시뮬레이션, GET 요청의 응답 포맷/정상 동작 여부 확인
│   └── curl_test.sh → 부하 테스트용 : 반복적이고 빠른 POST 요청으로 API 서버에 시계열 데이터가 누적되는 상황 테스트, 메모리 저장 구조(deque)가 잘 작동하는지 확인, 성능 병목, 시간 간격 계산 등의 문제 조기 발견
│
├── data/                           # (선택) 로컬 수집 데이터 저장
│   └── resource_log.json
│
├── [README.md](http://readme.md/)                       # 프로젝트 설명, 실행법
└── [report.md](http://report.md/)                       # 과제용 보고서 (또는 report 디렉토리)