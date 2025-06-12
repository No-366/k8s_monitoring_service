#!/bin/bash

# API 서버 URL 설정
API_URL="http://localhost:30500"

echo "=========================================="
echo "📊 실시간 Kubernetes 모니터링 대시보드"
echo "=========================================="

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 화면 지우기 함수
clear_screen() {
    clear
    echo -e "${CYAN}=========================================="
    echo "📊 Kubernetes 모니터링 대시보드"
    echo "=========================================="
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "==========================================${NC}"
}

# 노드 상태 표시
show_nodes() {
    echo -e "\n${YELLOW}🖥️  노드 상태${NC}"
    echo "----------------------------------------"
    
    nodes_data=$(curl -s "${API_URL}/api/nodes" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$nodes_data" ]; then
        if command -v jq &> /dev/null; then
            echo "$nodes_data" | jq -r '.[] | "📍 \(.node_name // "Unknown") | CPU: \(.cpu_millicores // 0)m | Memory: \((.memory_bytes // 0) / 1024 / 1024 | floor)MB | Disk R/W: \(.disk_io.read_bytes // 0)/\(.disk_io.write_bytes // 0) bytes"' 2>/dev/null || echo "데이터 파싱 오류"
        else
            echo "$nodes_data"
        fi
    else
        echo -e "${RED}❌ 노드 데이터를 가져올 수 없습니다${NC}"
    fi
}

# 파드 상태 표시
show_pods() {
    echo -e "\n${BLUE}🚀 파드 상태 (상위 5개)${NC}"
    echo "----------------------------------------"
    
    pods_data=$(curl -s "${API_URL}/api/pods" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$pods_data" ]; then
        echo "$pods_data" | jq -r '.[] | "🔹 \(.namespace // "default")/\(.pod_name // "Unknown") | CPU: \(.cpu_millicores // 0)m | Memory: \((.memory_bytes // 0) / 1024 / 1024 | floor)MB | Node: \(.node_name // "Unknown")"' 2>/dev/null | head -5 || echo "데이터 파싱 오류"
    else
        echo -e "${RED}❌ 파드 데이터를 가져올 수 없습니다${NC}"
    fi
}

# 네임스페이스 상태 표시
show_namespaces() {
    echo -e "\n${GREEN}📁 네임스페이스 상태${NC}"
    echo "----------------------------------------"
    
    ns_data=$(curl -s "${API_URL}/api/namespaces" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$ns_data" ]; then
        echo "$ns_data" | jq -r '.[] | "📂 \(.namespace // "Unknown") | CPU: \(.cpu_millicores // 0)m | Memory: \((.memory_bytes // 0) / 1024 / 1024 | floor)MB"' 2>/dev/null || echo "데이터 파싱 오류"
    else
        echo -e "${RED}❌ 네임스페이스 데이터를 가져올 수 없습니다${NC}"
    fi
}

# 시계열 트렌드 표시
show_trends() {
    echo -e "\n${PURPLE}📈 최근 5분 트렌드${NC}"
    echo "----------------------------------------"
    
    # 노드 시계열 데이터 (최근 5분)
    trend_data=$(curl -s "${API_URL}/api/nodes/timeseries?window=300" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$trend_data" ]; then
        echo -e "${CYAN}노드 트렌드:${NC}"
        echo "$trend_data" | jq -r '.[-3:] | .[] | "  ⏰ \(.timestamp[11:19]) | CPU: \(.cpu_millicores // 0)m | Memory: \((.memory_bytes // 0) / 1024 / 1024 | floor)MB"' 2>/dev/null | tail -3 || echo "  트렌드 데이터 없음"
    else
        echo -e "${RED}❌ 트렌드 데이터를 가져올 수 없습니다${NC}"
    fi
}

# 시스템 요약 정보
show_summary() {
    echo -e "\n${YELLOW}📋 시스템 요약${NC}"
    echo "----------------------------------------"
    
    # 전체 통계 계산
    nodes_count=$(curl -s "${API_URL}/api/nodes" 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    pods_count=$(curl -s "${API_URL}/api/pods" 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    ns_count=$(curl -s "${API_URL}/api/namespaces" 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    
    echo "🖥️  총 노드 수: ${nodes_count}"
    echo "🚀 총 파드 수: ${pods_count}"
    echo "📁 총 네임스페이스 수: ${ns_count}"
    echo "🔄 API 서버: ${API_URL}"
}

# 메인 대시보드 루프
main_dashboard() {
    local refresh_interval=5
    
    echo -e "${GREEN}🚀 실시간 모니터링 시작 (${refresh_interval}초 간격)${NC}"
    echo -e "${BLUE}종료하려면 Ctrl+C를 누르세요${NC}"
    sleep 2
    
    while true; do
        clear_screen
        show_summary
        show_nodes
        show_pods
        show_namespaces
        show_trends
        
        echo -e "\n${CYAN}----------------------------------------"
        echo "🔄 ${refresh_interval}초 후 새로고침... (Ctrl+C로 종료)"
        echo -e "----------------------------------------${NC}"
        
        sleep $refresh_interval
    done
}

# 인터랙티브 메뉴
interactive_menu() {
    while true; do
        clear_screen
        echo -e "\n${BLUE}🎯 모니터링 옵션을 선택하세요:${NC}"
        echo "1) 실시간 대시보드 (자동 새로고침)"
        echo "2) 노드 상태 한번 보기"
        echo "3) 파드 상태 한번 보기"
        echo "4) 네임스페이스 상태 한번 보기"
        echo "5) 시계열 트렌드 보기"
        echo "6) 전체 상태 한번 보기"
        echo "0) 종료"
        
        read -p "선택 (0-6): " choice
        
        case $choice in
            1) main_dashboard ;;
            2) clear_screen; show_nodes; read -p "계속하려면 Enter를 누르세요..." ;;
            3) clear_screen; show_pods; read -p "계속하려면 Enter를 누르세요..." ;;
            4) clear_screen; show_namespaces; read -p "계속하려면 Enter를 누르세요..." ;;
            5) clear_screen; show_trends; read -p "계속하려면 Enter를 누르세요..." ;;
            6) 
                clear_screen
                show_summary
                show_nodes
                show_pods
                show_namespaces
                show_trends
                read -p "계속하려면 Enter를 누르세요..."
                ;;
            0) 
                echo -e "${GREEN}👋 모니터링 대시보드를 종료합니다.${NC}"
                exit 0
                ;;
            *) 
                echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
                sleep 1
                ;;
        esac
    done
}

# 스크립트 실행
interactive_menu 