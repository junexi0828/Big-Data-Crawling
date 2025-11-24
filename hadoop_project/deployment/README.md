# Hadoop 클러스터 배포 가이드

## 📋 개요

이 디렉토리는 Hadoop Multi-Node Cluster를 각 노드에 배포하기 위한 스크립트를 포함합니다.

**암호화폐 클러스터 프로젝트와 유사한 방식**으로, 로컬에서 개발한 후 각 노드에 배포하는 구조입니다.

## 📁 배포 스크립트

### `deploy_namenode.sh`

**NameNode (마스터 노드) 배포 스크립트**

**실행 위치**: NameNode (bigpie1)

**기능**:

- Hadoop 바이너리 다운로드
- `/opt/hadoop`에 설치
- 설정 파일 배포
- 환경 변수 설정
- JAVA_HOME 설정

**사용법**:

```bash
# NameNode에서 실행
cd hadoop_project
./deployment/deploy_namenode.sh
```

### `deploy_datanodes.sh`

**DataNode (워커 노드) 배포 스크립트**

**실행 위치**: NameNode (bigpie1)에서 실행하여 모든 DataNode에 배포

**기능**:

- NameNode의 Hadoop 파일을 각 DataNode로 복사 (rsync)
- 설정 파일 배포
- 환경 변수 배포

**사용법**:

```bash
# NameNode에서 실행
cd hadoop_project
./deployment/deploy_datanodes.sh
```

### `deploy_all.sh`

**전체 클러스터 배포 스크립트**

**실행 위치**: NameNode (bigpie1)

**기능**:

- NameNode 배포 → DataNode 배포 순차 실행

**사용법**:

```bash
# NameNode에서 실행
cd hadoop_project
./deployment/deploy_all.sh
```

## 🔄 배포 프로세스

### 1. 로컬 개발 (개발 PC)

```
hadoop_project/
├── config/              # 설정 파일 템플릿
├── scripts/             # 설정 스크립트
├── docs/                # 문서
└── deployment/          # 배포 스크립트
    ├── deploy_namenode.sh
    ├── deploy_datanodes.sh
    └── deploy_all.sh
```

### 2. NameNode 배포

```bash
# NameNode (bigpie1)에 접속
ssh bigpie1

# 프로젝트 복사 (개발 PC에서)
scp -r hadoop_project bigpie1:~/

# NameNode 배포
cd ~/hadoop_project
./deployment/deploy_namenode.sh
```

**결과**: NameNode에 `/opt/hadoop` 설치 완료

### 3. DataNode 배포

```bash
# NameNode에서 실행
./deployment/deploy_datanodes.sh
```

**결과**:

- bigpie2: `/opt/hadoop` 설치 완료
- bigpie3: `/opt/hadoop` 설치 완료
- bigpie4: `/opt/hadoop` 설치 완료

## 📊 배포 전후 비교

### 배포 전 (로컬 개발)

```
개발 PC
└── hadoop_project/
    ├── hadoop-3.4.1/    (로컬 테스트용)
    ├── config/          (설정 템플릿)
    ├── scripts/         (설정 스크립트)
    └── deployment/      (배포 스크립트)
```

### 배포 후 (실제 클러스터)

```
bigpie1 (NameNode)
└── /opt/hadoop/         (실제 설치)

bigpie2 (DataNode)
└── /opt/hadoop/         (rsync로 복사됨)

bigpie3 (DataNode)
└── /opt/hadoop/         (rsync로 복사됨)

bigpie4 (DataNode)
└── /opt/hadoop/         (rsync로 복사됨)
```

## 🔧 배포 자동화 예시

### 개발 PC에서 원격 배포

```bash
#!/bin/bash
# deploy_from_pc.sh (개발 PC에서 실행)

NAMENODE="bigpie1"
PROJECT_DIR="hadoop_project"

# 1. 프로젝트를 NameNode로 복사
echo "프로젝트를 NameNode로 복사 중..."
rsync -avz --exclude='hadoop-3.4.1' --exclude='*.tar.gz' \
    $PROJECT_DIR/ $NAMENODE:~/hadoop_project/

# 2. NameNode 배포 실행
echo "NameNode 배포 중..."
ssh $NAMENODE "cd ~/hadoop_project && ./deployment/deploy_namenode.sh"

# 3. DataNode 배포 실행
echo "DataNode 배포 중..."
ssh $NAMENODE "cd ~/hadoop_project && ./deployment/deploy_datanodes.sh"

echo "배포 완료!"
```

## ✅ 배포 확인

### 각 노드에서 Hadoop 버전 확인

```bash
# NameNode
ssh bigpie1 "hadoop version"

# DataNode
ssh bigpie2 "hadoop version"
ssh bigpie3 "hadoop version"
ssh bigpie4 "hadoop version"
```

### 파일 존재 확인

```bash
# NameNode
ssh bigpie1 "ls -la /opt/hadoop/bin/hadoop"

# DataNode
ssh bigpie2 "ls -la /opt/hadoop/bin/hadoop"
```

## 🔄 업데이트 배포

설정 파일이나 스크립트를 수정한 경우:

```bash
# 1. 개발 PC에서 NameNode로 복사
rsync -avz hadoop_project/config/ bigpie1:~/hadoop_project/config/

# 2. NameNode에서 설정 파일 업데이트
ssh bigpie1 "cp ~/hadoop_project/config/*.xml /opt/hadoop/etc/hadoop/"

# 3. DataNode로 설정 파일 배포
ssh bigpie1 "./deployment/deploy_datanodes.sh"
```

## 📝 주의사항

1. **네트워크 속도**: Hadoop 바이너리는 약 300MB이므로 배포에 시간이 걸릴 수 있습니다.
2. **SSH 인증**: 패스워드 없는 SSH 인증이 설정되어 있어야 합니다.
3. **권한**: 모든 노드에서 동일한 사용자로 실행해야 합니다.
4. **경로**: 모든 노드에서 동일한 경로(`/opt/hadoop`)를 사용합니다.

## 🔗 관련 문서

- [SETUP_GUIDE.md](../docs/SETUP_GUIDE.md) - 상세 설정 가이드
- [NODE_PREPARATION.md](../docs/NODE_PREPARATION.md) - 노드별 준비 상태
- [PROJECT_STRUCTURE.md](../docs/PROJECT_STRUCTURE.md) - 프로젝트 구조
