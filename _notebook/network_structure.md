| 항목 (Item)        | 사용 위치 (Usage Location)       | 예시 값 (Example Value)            | 설명 (Description)                               |
| :----------------- | :----------------------------- | :------------------------------- | :----------------------------------------------- |
| API 서버 컨테이너 포트 | API 서버 내부                  | 5000                             | Flask에서 사용하는 포트                          |
| Service ClusterIP 포트 | Service 내부 포트                | 5000                             | 클러스터 내 접근 시 사용                         |
| Service NodePort 포트 | 외부 노출용                      | 30500                            | 클러스터 외부 접근용 포트                        |
| Service 이름       | DNS 주소                       | api-server-service               | 클러스터 내 DNS로 자동 등록됨                    |
| Collector 접근 주소 | collector.py 내 API URL        | http://api-server-service:5000   | 내부 통신용                                      |
| 외부 접속 주소     | 브라우저나 curl에서 접근         | http://\<NodeIP\>:30500            | 클러스터 외부에서 API 테스트 시 사용             |
| 호스트 이름 추출용 | collector 노드 이름 식별         | /etc/hostname 내용               | POST 경로에 사용됨                               |