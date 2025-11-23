# Hadoop 설정 가이드

## 📋 목차

1. [사전 준비사항](#사전-준비사항)
2. [Local (Standalone) Mode Setup](#local-standalone-mode-setup)
3. [Single-Node Cluster Mode Setup (w/o YARN)](#single-node-cluster-mode-setup-wo-yarn)
4. [Single-Node Cluster Mode Setup (with YARN)](#single-node-cluster-mode-setup-with-yarn)
5. [Multi-Node Cluster Mode Setup](#multi-node-cluster-mode-setup)

---

## 사전 준비사항

### 필수 요구사항

- **JDK**: v8 이상 또는 v11 이상
- **OS**: Linux+ 또는 Windows with WSL
- **SSH**: 패스워드 없는 SSH 환경 구성

### 3가지 모드 비교

| 모드                                         | 설명                                            | 용도               |
| -------------------------------------------- | ----------------------------------------------- | ------------------ |
| **Local (Standalone)**                       | 단일 Java 프로세스로 실행                       | 디버깅용           |
| **Single-Node Cluster (Pseudo-Distributed)** | 단일 머신에서 모든 Hadoop 데몬 실행             | 학습, 개발, 테스트 |
| **Multi-Node Cluster (Fully-Distributed)**   | 프로덕션급 설정 (10 Gbps+ 대역폭, 16GB+ 메모리) | 프로덕션 환경      |

---

## Local (Standalone) Mode Setup

### 특징

- 다운로드한 바이너리의 기본 설정 모드
- 단일 Java 프로세스로 실행
- 디버깅에 유용

### 설정 단계

#### 1. Hadoop 다운로드 및 압축 해제

```bash
# Hadoop 다운로드 (예: 3.4.1)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz

# 압축 해제
tar -zxvf hadoop-3.4.1.tar.gz

# Hadoop 디렉토리로 이동
cd hadoop-3.4.1
```

#### 2. JAVA_HOME 설정

`./etc/hadoop/hadoop-env.sh` 또는 `hadoop-env.cmd` 파일 편집:

```bash
# 예시 (macOS)
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.0.12.jdk/Contents/Home

# 예시 (Linux)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
```

#### 3. 버전 확인

```bash
bin/hadoop version
```

### 예제 실행

#### Wordcount 예제

```bash
# 입력 디렉토리 생성
mkdir input

# 샘플 파일 생성
echo "Hello Hadoop Bye Bye This is a test for mapreduce" > input/file01.txt
echo "Hello Hadoop Bye Hadoop This is another test for hadoop" > input/file02.txt

# Wordcount 작업 실행
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar wordcount input output

# 결과 확인
cat ./output/part-r-00000
```

#### Pi 예제 (Monte Carlo 시뮬레이션)

```bash
# Pi 계산 (맵 수, 맵당 포인트 수)
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar pi 10 1000
```

---

## Single-Node Cluster Mode Setup (w/o YARN)

### 특징

- 단일 머신에서 모든 Hadoop 데몬 실행
- NameNode, DataNode만 실행 (YARN 없음)
- 학습 및 개발에 이상적

### 설정 단계

#### 1. Hadoop 다운로드 및 압축 해제

```bash
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
tar -zxvf hadoop-3.4.1.tar.gz
cd hadoop-3.4.1
```

#### 2. JAVA_HOME 설정

`./etc/hadoop/hadoop-env.sh` 편집:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
```

#### 3. 설정 파일 편집

##### core-site.xml

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```

##### hdfs-site.xml

```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
```

#### 4. 패스워드 없는 SSH 로그인 설정

```bash
# RSA 키 쌍 생성
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa

# 생성된 키 추가
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 키 파일 보호
chmod 0600 ~/.ssh/authorized_keys

# 로그인 테스트
ssh localhost
```

#### 5. 파일시스템 포맷

```bash
bin/hdfs namenode -format -force
```

#### 6. NameNode & DataNode 데몬 시작

```bash
sbin/start-dfs.sh
```

#### 7. NameNode 웹 인터페이스 확인

브라우저에서 접속:

```
http://localhost:9870/
```

#### 8. HDFS 디렉토리 생성

```bash
bin/hdfs dfs -mkdir -p /user/bigdata/input
bin/hdfs dfs -ls
```

#### 9. 샘플 파일을 HDFS에 업로드

```bash
bin/hdfs dfs -put *.txt input
bin/hdfs dfs -ls input
```

#### 10. Wordcount 예제 실행

```bash
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar wordcount input output

# 결과 확인 (로컬로 가져오기)
bin/hdfs dfs -get output result
cat result/*

# 또는 HDFS에서 직접 확인
bin/hdfs dfs -cat output/*
```

#### 11. 데몬 중지

```bash
sbin/stop-dfs.sh
```

### 프로세스 확인

```bash
jps
```

예상 출력:

```
93572 Jps
90792 DataNode
90922 SecondaryNameNode
90717 NameNode
```

---

## Single-Node Cluster Mode Setup (with YARN)

### 특징

- YARN을 포함한 완전한 클러스터 모드
- ResourceManager, NodeManager 추가 실행

### 추가 설정 단계

#### 1. JDK 설치 (v8 또는 v11)

```bash
# 예시: BellSoft JDK 8 설치
wget https://download.bell-sw.com/java/8u452+11/bellsoft-jdk8u452+11-linux-aarch64.deb
sudo apt install ./bellsoft-jdk8u452+11-linux-aarch64.deb
sudo update-alternatives --config java
```

#### 2. JAVA_HOME 설정

`./etc/hadoop/hadoop-env.sh` 편집:

```bash
export JAVA_HOME=/usr/lib/jvm/bellsoft-java8-aarch64
```

#### 3. 설정 파일 편집

##### mapred-site.xml

```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/home/bigdata/hadoop-3.4.1/share/hadoop/mapreduce/*</value>
    </property>
</configuration>
```

##### yarn-site.xml

```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>localhost</value>
    </property>
</configuration>
```

#### 4. ResourceManager 및 NodeManager 시작

```bash
sbin/start-yarn.sh
```

#### 5. ResourceManager 웹 인터페이스 확인

브라우저에서 접속:

```
http://localhost:8088/
```

#### 6. Wordcount 예제 실행

```bash
# 기존 output 폴더 삭제 (있는 경우)
bin/hdfs dfs -rm -r output

# Wordcount 실행
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar wordcount input output
```

#### 7. 모든 데몬 중지

```bash
sbin/stop-yarn.sh && sbin/stop-dfs.sh
```

### 프로세스 확인

```bash
jps
```

예상 출력:

```
3504 Jps
2883 NodeManager
2389 DataNode
2005 ResourceManager
2534 SecondaryNameNode
2313 NameNode
```

---

## Multi-Node Cluster Mode Setup

### 노드 구성 예시

- **NameNode**: bigpie1
- **DataNode**: bigpie2, bigpie3, bigpie4

### 설정 단계

#### 1. 사전 준비사항

```bash
# Java v8 (또는 v11), ssh, pdsh 설치 확인
sudo apt install ssh pdsh
```

#### 2. /etc/hosts 파일 편집

각 노드에서 `/etc/hosts` 파일 편집:

**bigpie1, bigpie2, bigpie3, bigpie4 모두 동일하게:**

```
# 기본 localhost 항목 주석 처리
#127.0.0.1 localhost
#::1 localhost ip6-localhost ip6-loopback
#ff02::1 ip6-allnodes
#ff02::2 ip6-allrouters

# 클러스터 IP 주소 및 호스트명
192.168.0.40 bigpie1
192.168.0.41 bigpie2
192.168.0.42 bigpie3
192.168.0.43 bigpie4
```

#### 3. SSH 별칭 설정 (bigpie1 ~ bigpie4)

**bigpie1에서:**

```bash
nano ~/.ssh/config
```

**config 파일 내용:**

```
Host bigpie1
    User bigdata
    Hostname 192.168.0.40

Host bigpie2
    User bigdata
    Hostname 192.168.0.41

Host bigpie3
    User bigdata
    Hostname 192.168.0.42

Host bigpie4
    User bigdata
    Hostname 192.168.0.43
```

**다른 노드로 복사:**

```bash
scp ~/.ssh/config bigpie2:~/.ssh/config
scp ~/.ssh/config bigpie3:~/.ssh/config
scp ~/.ssh/config bigpie4:~/.ssh/config
```

#### 4. 패스워드 없는 SSH 인증 설정

**bigpie1 ~ bigpie4에서 키 생성:**

```bash
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
```

**bigpie1에서 키 수집:**

```bash
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

**bigpie2 ~ bigpie4에서 bigpie1로 키 복사:**

```bash
ssh-copy-id bigpie1
```

**bigpie1에서 수집된 키를 다른 노드로 배포:**

```bash
scp ~/.ssh/authorized_keys bigpie2:~/.ssh/authorized_keys
scp ~/.ssh/authorized_keys bigpie3:~/.ssh/authorized_keys
scp ~/.ssh/authorized_keys bigpie4:~/.ssh/authorized_keys
```

**테스트:**

```bash
# bigpie2 ~ bigpie4에서
ssh bigpie1
```

#### 5. 클러스터 관리 명령어 추가 (bigpie1)

`~/.bashrc` 파일에 추가:

```bash
function others {
    grep "bigpie" /etc/hosts | awk '{print $2}' | grep -v $(hostname)
}

function cluster_run {
    for x in $(others); do ssh $x "$@"; done
    $@
}

function cluster_reboot {
    cluster_run sudo shutdown -r now
}

function cluster_shutdown {
    cluster_run sudo shutdown now
}

function cluster_scp {
    for x in $(others); do
        cat $1 | ssh $x "sudo tee $1" > /dev/null 2>&1
    done
}
```

**적용:**

```bash
source .bashrc
cluster_run date  # 테스트
```

**다른 노드로 복사:**

```bash
cluster_scp ~/.bashrc
# 또는 각 노드에서: source .bashrc
```

#### 6. Hadoop 설치 (bigpie1)

```bash
# Hadoop 다운로드 및 압축 해제
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
sudo tar -zxvf hadoop-3.4.1.tar.gz -C /opt/
sudo mv /opt/hadoop-3.4.1 /opt/hadoop
sudo chown bigdata:bigdata -R /opt/hadoop
```

#### 7. 환경 변수 설정 (bigpie1)

`~/.bashrc`에 추가:

```bash
export PDSH_RCMD_TYPE=ssh
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

**적용:**

```bash
source .bashrc
hadoop version
```

#### 8. JAVA_HOME 설정 (bigpie1)

`/opt/hadoop/etc/hadoop/hadoop-env.sh` 편집:

```bash
export JAVA_HOME=/usr/lib/jvm/bellsoft-java8-aarch64
```

#### 9. Hadoop 파일 및 설정 복사

```bash
# 임시 디렉토리 생성
cluster_run sudo mkdir -p /opt/hadoop_tmp/hdfs
cluster_run sudo chown bigdata:bigdata -R /opt/hadoop_tmp
cluster_run sudo mkdir -p /opt/hadoop
cluster_run sudo chown bigdata:bigdata -R /opt/hadoop

# Hadoop 파일 복사
for x in $(others); do rsync -avxP $HADOOP_HOME $x:/opt; done

# .bashrc 복사
cluster_scp ~/.bashrc
```

#### 10. 클러스터 재부팅

```bash
cluster_reboot
```

#### 11. 모든 노드에서 Hadoop 버전 확인

```bash
# bigpie2 ~ bigpie4에서
hadoop version
```

#### 12. 설정 파일 편집 (bigpie1)

##### core-site.xml

```xml
<configuration>
    <property>
        <name>fs.default.name</name>
        <value>hdfs://bigpie1:9000</value>
    </property>
</configuration>
```

##### hdfs-site.xml

```xml
<configuration>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/opt/hadoop_tmp/hdfs/datanode</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/opt/hadoop_tmp/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
</configuration>
```

##### mapred-site.xml

```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.env</name>
        <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
    </property>
    <property>
        <name>mapreduce.map.env</name>
        <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
    </property>
    <property>
        <name>mapreduce.reduce.env</name>
        <value>HADOOP_MAPRED_HOME=${HADOOP_HOME}</value>
    </property>
    <property>
        <name>mapreduce.jobhistory.address</name>
        <value>bigpie1:10020</value>
    </property>
    <property>
        <name>mapreduce.jobhistory.webapp.address</name>
        <value>bigpie1:19888</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.resource.mb</name>
        <value>256</value>
    </property>
    <property>
        <name>mapreduce.map.memory.mb</name>
        <value>256</value>
    </property>
    <property>
        <name>mapreduce.reduce.memory.mb</name>
        <value>256</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/opt/hadoop/share/hadoop/mapreduce/*:/opt/hadoop/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```

**⚠️ 참고**: "Java heap space" 오류 발생 시 메모리 크기 증가 (256 → 384 → 512)

##### yarn-site.xml

```xml
<configuration>
    <property>
        <name>yarn.acl.enable</name>
        <value>0</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>bigpie1</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>512</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>512</value>
    </property>
    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>256</value>
    </property>
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>
</configuration>
```

#### 13. 설정 파일 복사 (bigpie1)

```bash
cluster_scp /opt/hadoop/etc/hadoop/core-site.xml
cluster_scp /opt/hadoop/etc/hadoop/hdfs-site.xml
cluster_scp /opt/hadoop/etc/hadoop/mapred-site.xml
cluster_scp /opt/hadoop/etc/hadoop/yarn-site.xml
```

#### 14. Master 및 Workers 파일 생성 (bigpie1)

**master 파일** (SecondaryNameNode용):

```bash
nano /opt/hadoop/etc/hadoop/master
```

내용:

```
bigpie1
```

**workers 파일** (DataNode용):

```bash
nano /opt/hadoop/etc/hadoop/workers
```

내용:

```
bigpie2
bigpie3
bigpie4
```

#### 15. NameNode 초기화 및 시작 (bigpie1)

```bash
# 메타데이터 디렉토리 초기화
hdfs namenode -format -force

# 모든 데몬 시작
start-dfs.sh && start-yarn.sh
```

#### 16. 데몬 확인 및 HDFS 테스트

**bigpie1에서:**

```bash
jps
```

예상 출력:

```
3728 ResourceManager
3376 NameNode
4884 Jps
3525 SecondaryNameNode
```

**bigpie2 ~ bigpie4에서:**

```bash
jps
```

예상 출력:

```
966 DataNode
1051 NodeManager
1197 Jps
```

**HDFS 테스트:**

```bash
# 파일 복사
hdfs dfs -put /opt/hadoop/*.txt /
```

---

## 트러블슈팅

### Java heap space 오류

- `mapred-site.xml`에서 메모리 크기 증가:
  - `yarn.app.mapreduce.am.resource.mb`: 256 → 384 → 512
  - `mapreduce.map.memory.mb`: 256 → 384 → 512
  - `mapreduce.reduce.memory.mb`: 256 → 384 → 512

### SSH 연결 문제

- `~/.ssh/authorized_keys` 권한 확인: `chmod 0600 ~/.ssh/authorized_keys`
- SSH 설정 확인: `ssh -v localhost`

### 데몬이 시작되지 않음

- 로그 확인: `$HADOOP_HOME/logs/`
- JAVA_HOME 설정 확인
- 포트 충돌 확인: `netstat -tulpn | grep 9000`

---

## 참고 자료

- Apache Hadoop 공식 문서: https://hadoop.apache.org/docs/current/
- Hadoop 설정 가이드: https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/SingleCluster.html
