#!/bin/bash

# API 서버 URL 설정
API_URL="http://localhost:30500"

echo "=========================================="
echo "🚀 Kubernetes 모니터링 API 테스트 시작"
echo "=========================================="

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 함수
test_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -e "\n${BLUE}📡 테스트: ${description}${NC}"
    echo "GET ${API_URL}${endpoint}"
    
    response=$(curl -s -w "HTTP_CODE:%{http_code}" "${API_URL}${endpoint}")
    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ 성공 (HTTP $http_code)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ 실패 (HTTP $http_code)${NC}"
        echo "$body"
    fi
}

echo -e "\n${YELLOW}=== 노드 API 테스트 ===${NC}"
test_endpoint "/api/nodes" "모든 노드 조회"
test_endpoint "/api/nodes/timeseries?window=3600" "노드 시계열 데이터 (1시간)"

echo -e "\n${YELLOW}=== 파드 API 테스트 ===${NC}"
test_endpoint "/api/pods" "모든 파드 조회"
test_endpoint "/api/pods/timeseries?window=1800" "파드 시계열 데이터 (30분)"

echo -e "\n${YELLOW}=== 네임스페이스 API 테스트 ===${NC}"
test_endpoint "/api/namespaces" "모든 네임스페이스 조회"
test_endpoint "/api/namespaces/default" "default 네임스페이스 조회"
test_endpoint "/api/namespaces/timeseries?window=3600" "네임스페이스 시계열 데이터"

echo -e "\n${YELLOW}=== 디플로이먼트 API 테스트 ===${NC}"
test_endpoint "/api/namespaces/default/deployments" "default 네임스페이스 디플로이먼트"
test_endpoint "/api/deployments/timeseries?window=3600" "디플로이먼트 시계열 데이터"

echo -e "\n${GREEN}=========================================="
echo "✅ API 테스트 완료"
echo "==========================================${NC}"
