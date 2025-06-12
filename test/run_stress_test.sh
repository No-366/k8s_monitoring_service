#!/bin/bash

# API 서버 URL 설정
API_URL="http://localhost:30500"

echo "=========================================="
echo "🔥 시스템 부하 테스트 및 모니터링 검증"
echo "=========================================="

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 필수 도구 설치 확인
check_tools() {
    echo -e "${BLUE}🔧 필수 도구 설치 확인...${NC}"
    
    # jq 설치 확인
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq 설치 중...${NC}"
        sudo apt-get install -y jq
    fi
    
    # stress 설치 확인
    if ! command -v stress &> /dev/null; then
        echo -e "${YELLOW}⚠️  stress 설치 중...${NC}"
        sudo apt-get update -qq && sudo apt-get install -y stress
    fi
    
    # iperf3 설치 확인
    if ! command -v iperf3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  iperf3 설치 중...${NC}"
        sudo apt-get install -y iperf3
    fi
    
    echo -e "${GREEN}✅ 모든 도구 준비 완료${NC}"
}

# API 호출 함수
call_api() {
    local endpoint=$1
    local description=$2
    
    echo -e "${PURPLE}📊 API 호출: ${description}${NC}"
    response=$(curl -s "${API_URL}${endpoint}")
    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.[] | select(.node_name or .pod_name or .namespace or .deployment_name) | "\(.timestamp // "N/A") - CPU: \(.cpu_millicores // 0)m, Memory: \((.memory_bytes // 0) / 1024 / 1024 | floor)MB"' | head -3
    else
        echo "$response" | head -3
    fi
}

# CPU 부하 테스트
cpu_stress_test() {
    echo -e "\n${YELLOW}=== 🔥 CPU 부하 테스트 ===${NC}"
    
    echo -e "${BLUE}📈 부하 테스트 전 상태 확인${NC}"
    call_api "/api/nodes" "노드 CPU 상태"
    
    echo -e "\n${RED}🚀 CPU 부하 생성 (4코어, 30초)${NC}"
    stress --cpu 4 --timeout 30s &
    STRESS_PID=$!
    
    # 10초 후 중간 상태 확인
    sleep 10
    echo -e "\n${PURPLE}📊 부하 중 상태 확인${NC}"
    call_api "/api/nodes/timeseries?window=300" "노드 시계열 데이터"
    
    # stress 완료 대기
    wait $STRESS_PID
    
    echo -e "\n${GREEN}✅ CPU 부하 테스트 완료${NC}"
    sleep 5
    call_api "/api/nodes" "부하 후 노드 상태"
}

# 메모리 부하 테스트
memory_stress_test() {
    echo -e "\n${YELLOW}=== 🧠 메모리 부하 테스트 ===${NC}"
    
    echo -e "${BLUE}📈 부하 테스트 전 메모리 상태${NC}"
    call_api "/api/pods" "파드 메모리 상태"
    
    echo -e "\n${RED}🚀 메모리 부하 생성 (1GB, 30초)${NC}"
    stress --vm 1 --vm-bytes 1G --timeout 30s &
    STRESS_PID=$!
    
    # 10초 후 중간 상태 확인
    sleep 10
    echo -e "\n${PURPLE}📊 부하 중 메모리 상태${NC}"
    call_api "/api/pods/timeseries?window=300" "파드 시계열 데이터"
    
    # stress 완료 대기
    wait $STRESS_PID
    
    echo -e "\n${GREEN}✅ 메모리 부하 테스트 완료${NC}"
    sleep 5
    call_api "/api/pods" "부하 후 파드 상태"
}

# 디스크 I/O 테스트
disk_io_test() {
    echo -e "\n${YELLOW}=== 💾 디스크 I/O 테스트 ===${NC}"
    
    echo -e "${BLUE}📈 디스크 I/O 테스트 전 상태${NC}"
    call_api "/api/nodes" "노드 디스크 상태"
    
    echo -e "\n${RED}🚀 디스크 쓰기 테스트 (500MB)${NC}"
    dd if=/dev/zero of=/tmp/stress_test_file bs=1M count=500 2>/dev/null &
    DD_PID=$!
    
    # 진행 중 상태 확인
    sleep 5
    echo -e "\n${PURPLE}📊 디스크 I/O 중 상태${NC}"
    call_api "/api/nodes/timeseries?window=300" "노드 시계열 (디스크 I/O)"
    
    # dd 완료 대기
    wait $DD_PID
    
    echo -e "\n${RED}🚀 디스크 읽기 테스트${NC}"
    dd if=/tmp/stress_test_file of=/dev/null bs=1M 2>/dev/null
    
    # 정리
    rm -f /tmp/stress_test_file
    
    echo -e "\n${GREEN}✅ 디스크 I/O 테스트 완료${NC}"
    call_api "/api/nodes" "디스크 테스트 후 상태"
}

# 네트워크 테스트
network_test() {
    echo -e "\n${YELLOW}=== 🌐 네트워크 테스트 ===${NC}"
    
    echo -e "${BLUE}📈 네트워크 테스트 전 상태${NC}"
    call_api "/api/nodes" "노드 네트워크 상태"
    
    echo -e "\n${RED}🚀 네트워크 다운로드 테스트${NC}"
    # 큰 파일 다운로드로 네트워크 부하 생성
    wget -q --progress=dot:mega -O /tmp/network_test_file http://speedtest.ftp.otenet.gr/files/test100Mb.db 2>&1 &
    WGET_PID=$!
    
    # 진행 중 상태 확인
    sleep 10
    echo -e "\n${PURPLE}📊 네트워크 사용 중 상태${NC}"
    call_api "/api/nodes/timeseries?window=300" "노드 시계열 (네트워크)"
    
    # wget 완료 대기 (최대 30초)
    timeout 30s wait $WGET_PID 2>/dev/null || kill $WGET_PID 2>/dev/null
    
    # 정리
    rm -f /tmp/network_test_file
    
    echo -e "\n${GREEN}✅ 네트워크 테스트 완료${NC}"
    call_api "/api/nodes" "네트워크 테스트 후 상태"
}

# 종합 부하 테스트
combined_stress_test() {
    echo -e "\n${YELLOW}=== 🔥🧠💾 종합 부하 테스트 ===${NC}"
    
    echo -e "${RED}🚀 CPU + 메모리 + 디스크 동시 부하 (20초)${NC}"
    
    # 동시 부하 생성
    stress --cpu 2 --vm 1 --vm-bytes 512M --timeout 20s &
    dd if=/dev/zero of=/tmp/combined_test bs=1M count=200 2>/dev/null &
    
    # 5초마다 상태 확인
    for i in {1..4}; do
        sleep 5
        echo -e "\n${PURPLE}📊 종합 부하 ${i}차 상태 확인${NC}"
        call_api "/api/nodes/timeseries?window=300" "실시간 노드 상태"
        call_api "/api/pods/timeseries?window=300" "실시간 파드 상태"
    done
    
    # 정리
    rm -f /tmp/combined_test
    
    echo -e "\n${GREEN}✅ 종합 부하 테스트 완료${NC}"
}

# 메인 실행
main() {
    check_tools
    
    echo -e "\n${BLUE}🎯 어떤 테스트를 실행하시겠습니까?${NC}"
    echo "1) CPU 부하 테스트"
    echo "2) 메모리 부하 테스트" 
    echo "3) 디스크 I/O 테스트"
    echo "4) 네트워크 테스트"
    echo "5) 종합 부하 테스트"
    echo "6) 전체 테스트 실행"
    
    read -p "선택 (1-6): " choice
    
    case $choice in
        1) cpu_stress_test ;;
        2) memory_stress_test ;;
        3) disk_io_test ;;
        4) network_test ;;
        5) combined_stress_test ;;
        6) 
            cpu_stress_test
            memory_stress_test
            disk_io_test
            network_test
            combined_stress_test
            ;;
        *) echo -e "${RED}❌ 잘못된 선택입니다.${NC}" ;;
    esac
    
    echo -e "\n${GREEN}=========================================="
    echo "🎉 부하 테스트 완료!"
    echo "📊 시계열 API로 변화를 확인해보세요:"
    echo "   curl ${API_URL}/api/nodes/timeseries?window=1800"
    echo "==========================================${NC}"
}

# 스크립트 실행
main
