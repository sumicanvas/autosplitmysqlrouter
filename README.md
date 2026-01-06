
# MySQL Router의 Auto split 포트 : 똑똑한 트래픽 분산 (MySQL 8.4 기준)


과거에는 애플리케이션 코드 레벨에서 두 개의 커넥션 풀(RW용, RO용)을 관리하며 직접 분기 처리를 해야 했습니다. 하지만 MySQL Router의 기능을 잘 활용하면 이 복잡한 과정을 미들웨어단에서 간단하게 해결할 수 있습니다. 오늘은 MySQL Router가 InnoDB Cluster에서 수행하는 역할과, 그중에서도 Auto Split(자동 분산) 기능에 대해 테스트 코드와 함께 확인해 봅니다.
---

## InnoDB Cluster 

<img width="878" height="916" alt="image" src="https://github.com/user-attachments/assets/bf6b2f44-b859-4b8e-92cf-db9b7d418028" />  

InnoDB Cluster는 자동으로 다음을 제공합니다.

* Auto Failover
* 자동 멤버 관리
