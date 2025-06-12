#!/bin/bash

# API 서버 URL 설정
API_URL="http://localhost:30500"

echo "=========================================="
echo "⚡ API 성능 벤치마크 테스트"
echo "=========================================="

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# API 응답 시간 측정 함수
measure_api_response() {
    local endpoint=$1
    local description=$2
    local iterations=${3:-10}
    
    echo -e "\n${BLUE}📊 테스트: ${description}${NC}"
    echo "엔드포인트: ${endpoint}"
    echo "반복 횟수: ${iterations}회"
    echo "----------------------------------------"
    
    local total_time=0
    local success=0
    local errors=0
    local min_time=999999
    local max_time=0
    
    for ((i=1; i<=iterations; i++)); do
        echo -n "테스트 ${i}/${iterations}... "
        
        # 시작 시간 기록
        start_time=$(date +%s.%N)
        
        # API 호출
        response=$(curl -s -w "HTTP_CODE:%{http_code}" "${API_URL}${endpoint}" 2>/dev/null)
        
        # 종료 시간 기록
        end_time=$(date +%s.%N)
        
        # 응답 시간 계산 (밀리초)
        response_time=$(echo "($end_time - $start_time) * 1000" | bc -l)
        response_time_int=$(printf "%.0f" "$response_time")
        
        # HTTP 상태 코드 확인
        http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
        
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✅ ${response_time_int}ms${NC}"
            ((success++))
            total_time=$(echo "$total_time + $response_time" | bc -l)
            
            # 최소/최대 시간 업데이트
            if (( $(echo "$response_time < $min_time" | bc -l) )); then
                min_time=$response_time
            fi
            if (( $(echo "$response_time > $max_time" | bc -l) )); then
                max_time=$response_time
            fi
        else
            echo -e "${RED}❌ HTTP $http_code${NC}"
            ((errors++))
        fi
        
        # 요청 간 간격
        sleep 0.1
    done
    
    # 통계 계산
    if [ $success -gt 0 ]; then
        avg_time=$(echo "scale=2; $total_time / $success" | bc -l)
        success_rate=$(echo "scale=2; $success * 100 / $iterations" | bc -l)
        
        echo -e "\n${YELLOW}📈 결과 요약:${NC}"
        echo "성공: ${success}/${iterations} (${success_rate}%)"
        echo "평균 응답시간: $(printf "%.2f" "$avg_time")ms"
        echo "최소 응답시간: $(printf "%.2f" "$min_time")ms"
        echo "최대 응답시간: $(printf "%.2f" "$max_time")ms"
        echo "오류: ${errors}회"
    else
        echo -e "\n${RED}❌ 모든 요청이 실패했습니다${NC}"
    fi
}

# 전체 API 엔드포인트 벤치마크
full_api_benchmark() {
    echo -e "\n${CYAN}🎯 전체 API 엔드포인트 벤치마크${NC}"
    
    # 기본 API 테스트
    measure_api_response "/api/nodes" "노드 목록 조회" 20
    measure_api_response "/api/pods" "파드 목록 조회" 20
    measure_api_response "/api/namespaces" "네임스페이스 목록 조회" 15
    
    # 시계열 API 테스트
    measure_api_response "/api/nodes/timeseries?window=3600" "노드 시계열 (1시간)" 10
    measure_api_response "/api/pods/timeseries?window=1800" "파드 시계열 (30분)" 10
}

# 메인 메뉴
main_menu() {
    echo -e "\n${BLUE}🎯 테스트 옵션을 선택하세요:${NC}"
    echo "1) 단일 엔드포인트 응답시간 측정"
    echo "2) 전체 API 벤치마크"
    echo "0) 종료"
    
    read -p "선택 (0-2): " choice
    
    case $choice in
        1)
            echo -e "\n${YELLOW}사용 가능한 엔드포인트:${NC}"
            echo "1) /api/nodes"
            echo "2) /api/pods"
            echo "3) /api/namespaces"
            echo "4) /api/nodes/timeseries?window=3600"
            
            read -p "엔드포인트 선택 (1-4): " ep_choice
            read -p "반복 횟수 (기본 10): " iterations
            iterations=${iterations:-10}
            
            case $ep_choice in
                1) measure_api_response "/api/nodes" "노드 목록" $iterations ;;
                2) measure_api_response "/api/pods" "파드 목록" $iterations ;;
                3) measure_api_response "/api/namespaces" "네임스페이스 목록" $iterations ;;
                4) measure_api_response "/api/nodes/timeseries?window=3600" "노드 시계열" $iterations ;;
                *) echo -e "${RED}잘못된 선택입니다${NC}" ;;
            esac
            ;;
        2)
            full_api_benchmark
            ;;
        0)
            echo -e "${GREEN}👋 벤치마크 테스트를 종료합니다.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
            ;;
    esac
}

# bc 설치 확인
if ! command -v bc &> /dev/null; then
    echo -e "${YELLOW}⚠️  bc 계산기를 설치합니다...${NC}"
    sudo apt-get update -qq && sudo apt-get install -y bc
fi

# 스크립트 실행
main_menu 