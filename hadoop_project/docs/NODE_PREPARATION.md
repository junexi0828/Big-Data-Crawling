# Hadoop Multi-Node Cluster 노드별 준비 가이드

## 📋 개요

이 문서는 Multi-Node Cluster 설정 시 각 노드에 필요한 파일과 준비 상태를 설명합니다.

## 🔍 현재 구조

### hadoop_project 폴더 (로컬 개발용)
```
hadoop_project/
├── hadoop-3.4.1/          # 로컬 테스트용 (단일 머신)
├── scripts/               # 설정 스크립트
├── config/                # 설정 파일 템플릿
└── docs/                  # 문서
```

**용도**:
- Local Mode 및 Single-Node Mode 테스트
- 설정 스크립트 및 템플릿 관리
- 문서화

### Multi-Node Cluster (실제 배포)

**가정**: 각 노드에 파일이 배포된다고 가정한 상태

**배포 방식**:
- NameNode(bigpie1)에서 스크립트 실행
- 자동으로 다른 노드로 파일 복사

## 🖥️ 노드별 파일 배포 상태

### NameNode (bigpie1)

**설치 위치**: `/opt/hadoop`

**파일 구조**:
```
/opt/hadoop/
├── bin/                   # 실행 파일
├── sbin/                  # 관리 스크립트
├── etc/hadoop/            # 설정 파일
│   ├── core-site.xml
│   ├── hdfs-site.xml
│   ├── mapred-site.xml
│   ├── yarn-site.xml
│   ├── master             # SecondaryNameNode
│   └── workers            # DataNode 목록
├── share/                 # 라이브러리 및 예제
└── lib/                   # 네이티브 라이브러리
```

**설정 파일**:
- `core-site.xml`: `fs.default.name=hdfs://bigpie1:9000`
- `hdfs-site.xml`: NameNode 및 DataNode 디렉토리 설정
- `mapred-site.xml`: MapReduce 설정
- `yarn-site.xml`: YARN 설정 (ResourceManager)

**환경 변수** (`~/.bashrc`):
```bash
export PDSH_RCMD_TYPE=ssh
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

### DataNode (bigpie2, bigpie3, bigpie4)

**설치 위치**: `/opt/hadoop` (NameNode와 동일)

**파일 구조**: NameNode와 동일 (rsync로 복사됨)

**설정 파일**: NameNode와 동일 (cluster_scp로 복사됨)

**환경 변수**: NameNode와 동일

**차이점**:
- `workers` 파일에는 자신이 포함되지 않음
- DataNode 및 NodeManager 데몬만 실행

## 📦 파일 배포 프로세스

### 1. NameNode에서 Hadoop 설치

```bash
# Step 6: Hadoop 설치 (bigpie1)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
sudo tar -zxvf hadoop-3.4.1.tar.gz -C /opt/
sudo mv /opt/hadoop-3.4.1 /opt/hadoop
sudo chown bigdata:bigdata -R /opt/hadoop
```

### 2. 다른 노드로 파일 복사

```bash
# Step 8: Hadoop 파일 복사
# 임시 디렉토리 생성
cluster_run sudo mkdir -p /opt/hadoop_tmp/hdfs
cluster_run sudo mkdir -p /opt/hadoop

# Hadoop 파일 복사 (rsync 사용)
for x in $(others); do
    rsync -avxP $HADOOP_HOME $x:/opt
done
```

### 3. 설정 파일 배포

```bash
# Step 13: 설정 파일 복사
cluster_scp /opt/hadoop/etc/hadoop/core-site.xml
cluster_scp /opt/hadoop/etc/hadoop/hdfs-site.xml
cluster_scp /opt/hadoop/etc/hadoop/mapred-site.xml
cluster_scp /opt/hadoop/etc/hadoop/yarn-site.xml
```

## ✅ 노드별 준비 체크리스트

### 모든 노드 공통

- [ ] Java JDK 8+ 설치
- [ ] SSH 설치 및 패스워드 없는 인증 설정
- [ ] `/etc/hosts` 파일에 모든 노드 IP 추가
- [ ] `~/.ssh/config` 파일 설정
- [ ] 클러스터 관리 함수 (`cluster_run`, `cluster_scp` 등) 추가

### NameNode (bigpie1) 전용

- [ ] Hadoop 다운로드 및 `/opt/hadoop`에 설치
- [ ] 환경 변수 설정 (`HADOOP_HOME`, `PATH`)
- [ ] `JAVA_HOME` 설정
- [ ] 설정 파일 편집 (core-site.xml, hdfs-site.xml 등)
- [ ] `master` 및 `workers` 파일 생성
- [ ] NameNode 포맷 (`hdfs namenode -format`)

### DataNode (bigpie2, bigpie3, bigpie4)

- [ ] Hadoop 파일이 `/opt/hadoop`에 복사됨 (자동)
- [ ] 설정 파일이 복사됨 (자동)
- [ ] 환경 변수가 설정됨 (자동)
- [ ] `/opt/hadoop_tmp/hdfs/datanode` 디렉토리 생성

## 🔄 자동 배포 vs 수동 배포

### 현재 방식: 자동 배포 (권장)

**장점**:
- 스크립트로 자동화
- 설정 일관성 보장
- 시간 절약

**방식**:
```bash
# NameNode에서 실행
./scripts/setup_multi_node_cluster.sh
```

### 수동 배포 (선택사항)

각 노드에 직접 접속하여 수동으로 설치:

```bash
# 각 노드에서 실행
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
sudo tar -zxvf hadoop-3.4.1.tar.gz -C /opt/
sudo mv /opt/hadoop-3.4.1 /opt/hadoop
sudo chown bigdata:bigdata -R /opt/hadoop
```

## 📝 주의사항

1. **파일 크기**: Hadoop 바이너리는 약 300MB이므로 네트워크 속도 고려
2. **권한**: 모든 노드에서 동일한 사용자(bigdata)로 실행
3. **경로**: 모든 노드에서 동일한 경로(`/opt/hadoop`) 사용
4. **설정 일관성**: 설정 파일은 모든 노드에서 동일해야 함

## 🔍 확인 방법

### 각 노드에서 Hadoop 버전 확인

```bash
# 모든 노드에서
hadoop version
```

### 파일 존재 확인

```bash
# NameNode에서
ls -la /opt/hadoop/bin/hadoop

# DataNode에서 (SSH로 확인)
ssh bigpie2 "ls -la /opt/hadoop/bin/hadoop"
```

### 설정 파일 확인

```bash
# NameNode에서
cat /opt/hadoop/etc/hadoop/core-site.xml

# DataNode에서
ssh bigpie2 "cat /opt/hadoop/etc/hadoop/core-site.xml"
```

## 📚 관련 문서

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 상세 설정 가이드
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 프로젝트 구조
- [scripts/setup_multi_node_cluster.sh](../scripts/setup_multi_node_cluster.sh) - 자동 배포 스크립트

