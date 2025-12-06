# Config 파일 동적 생성 및 템플릿 관리 전수 조사 보고서

**작성 일시**: 2025-01-27
**최종 업데이트**: 2025-12-06
**목적**: 프로젝트 내 모든 동적 생성되는 config 파일 및 템플릿 파일 전수 조사 및 관리 체계 수립

---

## 📋 목차

1. [개요](#개요)
2. [조사 범위](#조사-범위)
3. [동적 생성 Config 파일 현황](#동적-생성-config-파일-현황)
4. [템플릿 파일 현황](#템플릿-파일-현황)
5. [생성 메커니즘 분석](#생성-메커니즘-분석)
6. [문제점 및 개선 방안](#문제점-및-개선-방안)
7. [관리 체계 제안](#관리-체계-제안)
8. [체크리스트](#체크리스트)

---

## 개요

본 보고서는 프로젝트 내에서 동적으로 생성되는 모든 config 파일(YAML, XML, Properties 등)과 템플릿 파일(.example, .template 등)을 전수 조사하고, 이를 체계적으로 관리할 수 있는 방안을 제시합니다.

### 조사 대상

- **동적 생성 파일**: 런타임에 코드로 생성되는 config 파일
- **템플릿 파일**: `.example`, `.template` 확장자를 가진 파일
- **생성 스크립트**: 배포 스크립트, 설정 스크립트 등

---

## 조사 범위

### 프로젝트 구조

```
bigdata/
├── PICU/
│   ├── cointicker/
│   │   ├── config/              # YAML config 파일들
│   │   │   ├── examples/        # 템플릿 파일들
│   │   └── gui/
│   │       └── modules/managers/
│   │           └── hdfs_manager.py  # XML 동적 생성
│   └── deployment/              # 배포 스크립트
├── hadoop_project/
│   ├── config/                  # XML 템플릿 파일들
│   └── deployment/              # 배포 스크립트
└── kafka_project/
    └── config/                  # Properties 템플릿 파일들
```

---

## 동적 생성 Config 파일 현황

### 1. PICU/cointicker 프로젝트

#### 1.1 YAML Config 파일 (자동 생성)

**위치**: `PICU/cointicker/config/`

| 파일명                 | 생성 방식   | 생성 코드 위치                       | 템플릿 위치                                    |
| ---------------------- | ----------- | ------------------------------------ | ---------------------------------------------- |
| `cluster_config.yaml`  | 자동 복사   | `gui/core/config_manager.py:96-117`  | `config/examples/cluster_config.yaml.example`  |
| `database_config.yaml` | 자동 복사   | `gui/core/config_manager.py:96-117`  | `config/examples/database_config.yaml.example` |
| `spider_config.yaml`   | 자동 복사   | `gui/core/config_manager.py:96-117`  | `config/examples/spider_config.yaml.example`   |
| `kafka_config.yaml`    | 자동 복사   | `gui/core/config_manager.py:96-117`  | `config/examples/kafka_config.yaml.example`    |
| `gui_config.yaml`      | 기본값 생성 | `gui/core/config_manager.py:233-283` | 없음 (코드 내 기본값)                          |

**생성 메커니즘**:

- `ConfigManager._load_config_from_file()`: 실제 config 파일이 없으면 example 파일에서 자동 복사
- `ConfigManager.create_default_configs()`: GUI 시작 시 기본 설정 파일 생성

**설정 파일 읽기 매핑 (2025-12-06 업데이트)**:

| 모듈                                           | 설정 파일              | 코드 위치                                            | 환경 변수 지원      |
| ---------------------------------------------- | ---------------------- | ---------------------------------------------------- | ------------------- |
| `backend/config.py`                            | `database_config.yaml` | `backend/config.py:13-52`                            | ✅ (환경 변수 우선) |
| `backend/config.py`                            | `cluster_config.yaml`  | `backend/config.py:47-70`                            | ✅ (환경 변수 우선) |
| `worker-nodes/cointicker/settings.py`          | `kafka_config.yaml`    | `worker-nodes/cointicker/settings.py:82-134`         | ✅ (환경 변수 우선) |
| `worker-nodes/cointicker/settings.py`          | `cluster_config.yaml`  | `worker-nodes/cointicker/settings.py:101-120`        | ✅ (환경 변수 우선) |
| `master-node/orchestrator.py`                  | `spider_config.yaml`   | `master-node/orchestrator.py:30-60`                  | ❌ (설정 파일만)    |
| `master-node/scheduler.py`                     | `spider_config.yaml`   | `master-node/scheduler.py:30-80`                     | ✅ (환경 변수 우선) |
| `worker-nodes/kafka/kafka_consumer_service.py` | `kafka_config.yaml`    | `worker-nodes/kafka/kafka_consumer_service.py:25-44` | ✅ (환경 변수 우선) |
| `gui/core/config_manager.py`                   | 모든 YAML 설정         | `gui/core/config_manager.py:172-228`                 | ✅ (환경 변수 우선) |

**환경 변수 우선순위 (2025-12-06 추가)**:
모든 모듈에서 다음 우선순위로 설정 값을 읽습니다:

1. **환경 변수** (최우선) - 예: `KAFKA_BOOTSTRAP_SERVERS`, `HDFS_NAMENODE`, `DATABASE_HOST`
2. **설정 파일** (fallback) - `config/*.yaml` 파일
3. **기본값** (최종 fallback) - 코드 내 하드코딩된 기본값

**레거시 하드코딩 제거 (2025-12-06)**:

- ❌ **이전**: `backend/config.py`에서 환경 변수만 사용, 설정 파일 미사용
- ✅ **현재**: `database_config.yaml`과 `cluster_config.yaml` 읽기 추가
- ❌ **이전**: `worker-nodes/cointicker/settings.py`에서 하드코딩된 Kafka/HDFS 설정
- ✅ **현재**: `kafka_config.yaml`과 `cluster_config.yaml` 읽기 추가
- ❌ **이전**: `master-node/orchestrator.py`에서 하드코딩된 Spider 목록
- ✅ **현재**: `spider_config.yaml`에서 활성화된 Spider 목록 로드
- ❌ **이전**: `master-node/scheduler.py`에서 하드코딩된 스케줄
- ✅ **현재**: `spider_config.yaml`에서 Spider 스케줄 정보 로드

**코드 위치**:

```96:117:PICU/cointicker/gui/core/config_manager.py
        # 실제 config 파일이 없으면 example에서 생성
        if not config_file.exists():
            example_file = (
                self.config_dir
                / "examples"
                / (self.config_files[config_name] + ".example")
            )
            if example_file.exists():
                try:
                    # example 파일을 config 파일로 복사 (자동 생성)
                    shutil.copy2(example_file, config_file)
                    logger.info(
                        f"예제 파일에서 설정 파일 생성: {config_name} ({config_file})"
                    )
                except Exception as e:
                    logger.error(f"설정 파일 생성 실패 {config_name}: {e}")
                    # 복사 실패 시 example 파일 읽기 (폴백)
                    logger.warning(f"예제 파일을 직접 사용합니다: {config_file}")
                    config_file = example_file
            else:
                logger.error(f"설정 파일을 찾을 수 없습니다: {config_file}")
                return None
```

#### 1.2 XML Config 파일 (동적 생성)

**위치**: `$HADOOP_HOME/etc/hadoop/` (런타임에 생성)

| 파일명          | 생성 방식       | 생성 코드 위치                                 | 생성 시점              |
| --------------- | --------------- | ---------------------------------------------- | ---------------------- |
| `core-site.xml` | f-string 템플릿 | `gui/modules/managers/hdfs_manager.py:422-432` | 단일 노드 모드 설정 시 |
| `core-site.xml` | f-string 템플릿 | `gui/modules/managers/hdfs_manager.py:558-568` | 클러스터 모드 설정 시  |
| `hdfs-site.xml` | f-string 템플릿 | `gui/modules/managers/hdfs_manager.py:451-469` | 단일 노드 모드 설정 시 |
| `hdfs-site.xml` | f-string 템플릿 | `gui/modules/managers/hdfs_manager.py:584-602` | 클러스터 모드 설정 시  |
| `workers`       | 동적 생성       | `gui/modules/managers/hdfs_manager.py:611`     | 클러스터 모드 설정 시  |
| `master`        | 동적 생성       | `gui/modules/managers/hdfs_manager.py:616`     | 클러스터 모드 설정 시  |

**생성 메커니즘**:

- `HDFSManager.setup_single_node_mode()`: 단일 노드 모드용 XML 생성
- `HDFSManager.setup_cluster_mode()`: 클러스터 모드용 XML 생성
- f-string을 사용한 템플릿 기반 동적 생성

**코드 예시**:

```422:432:PICU/cointicker/gui/modules/managers/hdfs_manager.py
            core_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>{namenode_url}</value>
    </property>
</configuration>
"""
            )
```

### 2. Hadoop 프로젝트

#### 2.1 XML Config 파일 (배포 스크립트로 복사)

**위치**: `hadoop_project/config/` → `$HADOOP_HOME/etc/hadoop/`

| 파일명            | 생성 방식     | 생성 스크립트                      | 템플릿 위치                      |
| ----------------- | ------------- | ---------------------------------- | -------------------------------- |
| `core-site.xml`   | 스크립트 복사 | `deployment/deploy_namenode.sh:49` | `config/core-site.xml.example`   |
| `hdfs-site.xml`   | 스크립트 복사 | `deployment/deploy_namenode.sh:50` | `config/hdfs-site.xml.example`   |
| `mapred-site.xml` | 스크립트 복사 | `deployment/deploy_namenode.sh:51` | `config/mapred-site.xml.example` |
| `yarn-site.xml`   | 스크립트 복사 | `deployment/deploy_namenode.sh:52` | `config/yarn-site.xml.example`   |

**생성 메커니즘**:

- 배포 스크립트에서 `.example` 파일을 실제 config 파일로 복사
- 수동으로 환경에 맞게 수정 필요

**스크립트 코드**:

```45:59:hadoop_project/deployment/deploy_namenode.sh
# 4. 설정 파일 배포
echo -e "\n${YELLOW}[3/5] 설정 파일 배포${NC}"
if [ -d "$PROJECT_ROOT/config" ]; then
    # 설정 파일 템플릿 복사
    cp "$PROJECT_ROOT/config/core-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml"
    cp "$PROJECT_ROOT/config/hdfs-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml"
    cp "$PROJECT_ROOT/config/mapred-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml"
    cp "$PROJECT_ROOT/config/yarn-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml"

    echo -e "${YELLOW}⚠️  설정 파일을 환경에 맞게 수정하세요:${NC}"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml"
fi
```

### 3. Kafka 프로젝트

#### 3.1 Properties Config 파일

**위치**: `kafka_project/config/`

| 파일명              | 생성 방식 | 템플릿 위치                        | 비고           |
| ------------------- | --------- | ---------------------------------- | -------------- |
| `server.properties` | 수동 복사 | `config/server.properties.example` | 자동 생성 없음 |

**생성 메커니즘**:

- 현재 자동 생성 메커니즘 없음
- 수동으로 `.example` 파일을 복사하여 사용

### 4. PICU/deployment 프로젝트

#### 4.1 Netplan Config 파일

**위치**: `PICU/deployment/`

| 파일명                | 생성 방식 | 생성 스크립트              | 템플릿 위치                   |
| --------------------- | --------- | -------------------------- | ----------------------------- |
| `netplan-config.yaml` | 수동 복사 | `deploy_netplan.sh` (참조) | `netplan-config.yaml.example` |

**생성 메커니즘**:

- 배포 스크립트에서 참조하지만 자동 생성은 없음
- 수동으로 `.example` 파일을 복사하여 사용

---

## 템플릿 파일 현황

### 1. PICU/cointicker/config/examples/

| 파일명                         | 용도                     | 실제 config 파일       |
| ------------------------------ | ------------------------ | ---------------------- |
| `cluster_config.yaml.example`  | 클러스터 설정 템플릿     | `cluster_config.yaml`  |
| `database_config.yaml.example` | 데이터베이스 설정 템플릿 | `database_config.yaml` |
| `spider_config.yaml.example`   | Spider 설정 템플릿       | `spider_config.yaml`   |
| `kafka_config.yaml.example`    | Kafka 설정 템플릿        | `kafka_config.yaml`    |
| `README.md`                    | 사용 방법 안내           | -                      |

**특징**:

- 모든 템플릿 파일은 `examples/` 디렉토리에 위치
- 자동 복사 메커니즘 구현됨 (`ConfigManager`)
- README.md에 사용 방법 문서화

### 2. hadoop_project/config/

| 파일명                    | 용도                    | 실제 config 파일  |
| ------------------------- | ----------------------- | ----------------- |
| `core-site.xml.example`   | Hadoop Core 설정 템플릿 | `core-site.xml`   |
| `hdfs-site.xml.example`   | HDFS 설정 템플릿        | `hdfs-site.xml`   |
| `mapred-site.xml.example` | MapReduce 설정 템플릿   | `mapred-site.xml` |
| `yarn-site.xml.example`   | YARN 설정 템플릿        | `yarn-site.xml`   |

**특징**:

- 배포 스크립트에서 복사
- 수동 수정 필요
- Single-Node와 Multi-Node 모드 주석으로 구분

### 3. kafka_project/config/

| 파일명                      | 용도                   | 실제 config 파일    |
| --------------------------- | ---------------------- | ------------------- |
| `server.properties.example` | Kafka 서버 설정 템플릿 | `server.properties` |

**특징**:

- 자동 생성 메커니즘 없음
- 수동 복사 필요
- 3-node 클러스터 설정 예시 포함

### 4. PICU/deployment/

| 파일명                        | 용도                         | 실제 config 파일      |
| ----------------------------- | ---------------------------- | --------------------- |
| `netplan-config.yaml.example` | Netplan 네트워크 설정 템플릿 | `netplan-config.yaml` |

**특징**:

- WiFi 및 유선 네트워크 설정 템플릿
- 배포 스크립트에서 참조

### 5. PICU/cointicker/frontend/

| 파일명         | 용도                        | 실제 config 파일 |
| -------------- | --------------------------- | ---------------- |
| `.env.example` | 프론트엔드 환경 변수 템플릿 | `.env`           |

**특징**:

- Vite 프론트엔드 환경 변수 템플릿
- 자동 생성 메커니즘 없음

---

## 생성 메커니즘 분석

### 1. 자동 복사 방식 (YAML Config)

**구현 위치**: `PICU/cointicker/gui/core/config_manager.py`

**장점**:

- ✅ 사용자 편의성: 파일이 없으면 자동 생성
- ✅ 일관성: 템플릿에서 항상 동일한 구조 보장
- ✅ 방어적 프로그래밍: 파일 누락 시 자동 처리

**단점**:

- ⚠️ 템플릿 파일이 없으면 실패
- ⚠️ 템플릿 파일 업데이트 시 기존 config 파일에 반영 안 됨

**개선 필요 사항**:

- 템플릿 파일 버전 관리
- 템플릿 업데이트 시 기존 config 파일 마이그레이션 로직

### 2. f-string 템플릿 방식 (XML Config)

**구현 위치**: `PICU/cointicker/gui/modules/managers/hdfs_manager.py`

**장점**:

- ✅ 동적 값 주입 가능
- ✅ 코드 내에서 완전한 제어
- ✅ 환경에 맞게 자동 생성

**단점**:

- ⚠️ 템플릿이 코드에 하드코딩됨
- ⚠️ 템플릿 수정 시 코드 수정 필요
- ⚠️ 유지보수 어려움

**개선 필요 사항**:

- 템플릿 파일 분리 (Jinja2 등 템플릿 엔진 사용)
- 템플릿 파일 버전 관리

### 3. 스크립트 복사 방식 (Hadoop Config)

**구현 위치**: `hadoop_project/deployment/deploy_namenode.sh`

**장점**:

- ✅ 배포 시 자동 복사
- ✅ 템플릿 파일 분리

**단점**:

- ⚠️ 수동 수정 필요
- ⚠️ 자동화 부족

**개선 필요 사항**:

- 환경 변수 기반 자동 설정
- 템플릿 변수 치환 로직 추가

---

## 문제점 및 개선 방안

### 문제점 0: 레거시 하드코딩 설정 (해결 완료 ✅)

**발견 일시**: 2025-12-06

**현상**:

- 여러 모듈에서 설정 파일이 존재함에도 불구하고 하드코딩된 값 사용
- `backend/config.py`: 환경 변수만 사용, `database_config.yaml` 미사용
- `worker-nodes/cointicker/settings.py`: 하드코딩된 Kafka/HDFS 설정
- `master-node/orchestrator.py`: 하드코딩된 Spider 목록
- `master-node/scheduler.py`: 하드코딩된 스케줄 및 Scrapyd URL

**해결 방안 (2025-12-06 적용)**:

1. ✅ `backend/config.py`에 `database_config.yaml`과 `cluster_config.yaml` 읽기 추가
2. ✅ `worker-nodes/cointicker/settings.py`에 `kafka_config.yaml`과 `cluster_config.yaml` 읽기 추가
3. ✅ `master-node/orchestrator.py`에 `spider_config.yaml` 읽기 추가
4. ✅ `master-node/scheduler.py`에 `spider_config.yaml` 읽기 추가
5. ✅ 모든 모듈에 환경 변수 우선순위 지원 추가 (환경 변수 > 설정 파일 > 기본값)

**환경 변수 매핑 예시**:

```bash
# Kafka 설정
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092,localhost:9093"
export KAFKA_TOPICS="cointicker.raw.*"
export KAFKA_GROUP_ID="cointicker-consumer"

# HDFS 설정
export HDFS_NAMENODE="hdfs://localhost:9000"

# 데이터베이스 설정
export DATABASE_TYPE="mariadb"
export DATABASE_HOST="localhost"
export DATABASE_PORT="3306"
export DATABASE_USER="cointicker"
export DATABASE_PASSWORD="your_password"
export DATABASE_NAME="cointicker"

# Scrapyd 설정
export SCRAPYD_URL="http://localhost:6800"
```

**결과**:

- ✅ 모든 모듈이 설정 파일과 환경 변수를 일관되게 사용
- ✅ 배포 환경에서 환경 변수로 쉽게 오버라이드 가능
- ✅ 개발 환경에서는 설정 파일 사용, 프로덕션에서는 환경 변수 사용 가능

### 문제점 1: 템플릿 파일과 실제 파일 동기화 부족

**현상**:

- 템플릿 파일이 업데이트되어도 기존 config 파일에 반영 안 됨
- 템플릿 파일과 실제 파일의 구조 차이 발생 가능

**개선 방안**:

1. 템플릿 파일 버전 관리
2. Config 파일 마이그레이션 로직 추가
3. 템플릿 파일 변경 감지 및 알림

### 문제점 2: XML 템플릿이 코드에 하드코딩됨

**현상**:

- `hdfs_manager.py`에 XML 템플릿이 문자열로 하드코딩
- 템플릿 수정 시 코드 수정 필요

**개선 방안**:

1. 템플릿 파일 분리 (`templates/` 디렉토리)
2. Jinja2 템플릿 엔진 사용
3. 템플릿 파일 버전 관리

### 문제점 3: 일관성 없는 생성 메커니즘

**현상**:

- YAML: 자동 복사
- XML: f-string 템플릿
- Properties: 수동 복사
- 각 프로젝트마다 다른 방식 사용

**개선 방안**:

1. 통합 Config 생성 유틸리티 클래스
2. 템플릿 엔진 통일 (Jinja2)
3. 생성 메커니즘 표준화

### 문제점 4: 템플릿 파일 문서화 부족

**현상**:

- 일부 템플릿 파일에 주석 있음
- 사용 방법 문서화 부족

**개선 방안**:

1. 각 템플릿 파일에 상세 주석 추가
2. README.md 파일로 사용 방법 문서화
3. 템플릿 변수 설명 추가

---

## 관리 체계 제안

### 1. 디렉토리 구조 표준화

```
프로젝트/
├── config/
│   ├── templates/           # 템플릿 파일 (새로 추가)
│   │   ├── *.yaml.template
│   │   ├── *.xml.template
│   │   └── *.properties.template
│   ├── examples/           # 예제 파일 (기존 유지)
│   │   └── *.example
│   └── generated/         # 생성된 파일 (gitignore)
│       └── *.yaml
└── scripts/
    └── generate_config.py  # Config 생성 스크립트
```

### 2. 템플릿 파일 명명 규칙

| 파일 타입  | 템플릿 확장자                                     | 예시                           |
| ---------- | ------------------------------------------------- | ------------------------------ |
| YAML       | `.yaml.template` 또는 `.yaml.example`             | `cluster_config.yaml.template` |
| XML        | `.xml.template` 또는 `.xml.example`               | `core-site.xml.template`       |
| Properties | `.properties.template` 또는 `.properties.example` | `server.properties.template`   |

### 3. Config 생성 유틸리티 클래스

```python
class ConfigGenerator:
    """통합 Config 생성 유틸리티"""

    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    def generate_from_template(self, template_name: str, variables: dict) -> Path:
        """템플릿에서 config 파일 생성"""
        template = self.env.get_template(template_name)
        content = template.render(**variables)
        output_path = self.output_dir / template_name.replace('.template', '')
        output_path.write_text(content)
        return output_path

    def copy_from_example(self, example_name: str) -> Path:
        """예제 파일에서 복사"""
        # 기존 로직
        pass
```

### 4. 템플릿 파일 버전 관리

각 템플릿 파일에 버전 정보 추가:

```yaml
# cluster_config.yaml.template
# Version: 1.2.0
# Last Updated: 2025-01-27
# Description: 클러스터 설정 템플릿

cluster:
  name: "{{ cluster_name }}"
  # ...
```

### 5. 마이그레이션 로직

템플릿 파일 업데이트 시 기존 config 파일 마이그레이션:

```python
def migrate_config(config_path: Path, template_path: Path) -> bool:
    """기존 config 파일을 새 템플릿 구조로 마이그레이션"""
    # 1. 기존 config 파일 읽기
    # 2. 새 템플릿 구조 확인
    # 3. 누락된 필드 추가
    # 4. 변경된 필드 업데이트
    # 5. 백업 생성
    pass
```

---

## 체크리스트

### 템플릿 파일 관리

- [ ] 모든 템플릿 파일이 `examples/` 또는 `templates/` 디렉토리에 위치하는가?
- [ ] 템플릿 파일에 버전 정보가 포함되어 있는가?
- [ ] 템플릿 파일에 사용 방법 주석이 있는가?
- [ ] 템플릿 파일과 실제 config 파일의 구조가 일치하는가?

### 생성 메커니즘

- [ ] 자동 생성 메커니즘이 구현되어 있는가?
- [ ] 생성 실패 시 적절한 에러 처리가 있는가?
- [ ] 생성된 파일이 gitignore에 포함되어 있는가?
- [ ] 템플릿 파일 변경 시 기존 config 파일 마이그레이션이 필요한가?

### 문서화

- [ ] 각 템플릿 파일의 용도가 문서화되어 있는가?
- [ ] Config 생성 방법이 README에 설명되어 있는가?
- [ ] 템플릿 변수 목록이 문서화되어 있는가?

### 일관성

- [ ] 모든 프로젝트에서 동일한 템플릿 명명 규칙을 사용하는가?
- [ ] Config 생성 방식이 표준화되어 있는가?
- [ ] 템플릿 파일 위치가 일관성 있는가?

---

## 권장 조치 사항

### 즉시 조치 (High Priority)

1. **템플릿 파일 목록 정리**

   - 모든 템플릿 파일 목록 작성
   - 각 템플릿 파일의 용도 문서화

2. **XML 템플릿 파일 분리**

   - `hdfs_manager.py`의 하드코딩된 XML 템플릿을 파일로 분리
   - Jinja2 템플릿 엔진 도입 검토

3. **통합 Config 생성 유틸리티 개발**
   - 모든 프로젝트에서 사용 가능한 공통 유틸리티
   - 템플릿 엔진 통일

### 중기 조치 (Medium Priority)

1. **템플릿 파일 버전 관리**

   - 각 템플릿 파일에 버전 정보 추가
   - 버전 변경 이력 관리

2. **마이그레이션 로직 구현**

   - 템플릿 업데이트 시 기존 config 파일 자동 마이그레이션
   - 백업 및 롤백 기능

3. **문서화 강화**
   - 각 템플릿 파일 사용 방법 상세 문서화
   - Config 생성 가이드 작성

### 장기 조치 (Low Priority)

1. **Config 관리 대시보드**

   - 템플릿 파일 상태 모니터링
   - Config 파일 생성 이력 추적

2. **자동 테스트**
   - 템플릿 파일 유효성 검사
   - 생성된 config 파일 검증

---

## 결론

본 전수 조사 결과, 프로젝트 내에서 다양한 방식으로 config 파일이 동적 생성되고 있음을 확인했습니다. 현재는 각 프로젝트마다 다른 방식을 사용하고 있어 일관성과 유지보수성 측면에서 개선이 필요합니다.

**주요 발견 사항**:

1. ✅ YAML config 파일은 자동 복사 메커니즘이 잘 구현되어 있음
2. ✅ **레거시 하드코딩 제거 완료 (2025-12-06)**: 모든 모듈이 설정 파일을 읽도록 수정
3. ✅ **환경 변수 우선순위 지원 추가 (2025-12-06)**: 모든 모듈에서 환경 변수 > 설정 파일 > 기본값 순서 적용
4. ⚠️ XML config 파일은 코드에 하드코딩되어 있어 개선 필요
5. ⚠️ Properties config 파일은 자동 생성 메커니즘 없음
6. ⚠️ 템플릿 파일과 실제 파일 동기화 메커니즘 부족

**권장 사항**:

1. 템플릿 파일을 별도 디렉토리로 분리
2. Jinja2 같은 템플릿 엔진 도입
3. 통합 Config 생성 유틸리티 개발
4. 템플릿 파일 버전 관리 및 마이그레이션 로직 구현

이러한 개선을 통해 config 파일 관리를 더욱 체계적이고 안정적으로 수행할 수 있을 것입니다.

---

## 부록: 전체 템플릿 파일 목록

### PICU/cointicker

| 파일명                         | 경로               | 타입 | 생성 대상              |
| ------------------------------ | ------------------ | ---- | ---------------------- |
| `cluster_config.yaml.example`  | `config/examples/` | YAML | `cluster_config.yaml`  |
| `database_config.yaml.example` | `config/examples/` | YAML | `database_config.yaml` |
| `spider_config.yaml.example`   | `config/examples/` | YAML | `spider_config.yaml`   |
| `kafka_config.yaml.example`    | `config/examples/` | YAML | `kafka_config.yaml`    |
| `.env.example`                 | `frontend/`        | ENV  | `.env`                 |

### hadoop_project

| 파일명                    | 경로      | 타입 | 생성 대상         |
| ------------------------- | --------- | ---- | ----------------- |
| `core-site.xml.example`   | `config/` | XML  | `core-site.xml`   |
| `hdfs-site.xml.example`   | `config/` | XML  | `hdfs-site.xml`   |
| `mapred-site.xml.example` | `config/` | XML  | `mapred-site.xml` |
| `yarn-site.xml.example`   | `config/` | XML  | `yarn-site.xml`   |

### kafka_project

| 파일명                      | 경로      | 타입       | 생성 대상           |
| --------------------------- | --------- | ---------- | ------------------- |
| `server.properties.example` | `config/` | Properties | `server.properties` |

### PICU/deployment

| 파일명                        | 경로          | 타입 | 생성 대상             |
| ----------------------------- | ------------- | ---- | --------------------- |
| `netplan-config.yaml.example` | `deployment/` | YAML | `netplan-config.yaml` |

---

## 환경 변수 및 설정 파일 사용 가이드 (2025-12-06 추가)

### 설정 우선순위

모든 모듈에서 다음 순서로 설정 값을 읽습니다:

1. **환경 변수** (최우선)
2. **설정 파일** (fallback)
3. **기본값** (최종 fallback)

### 환경 변수 목록

#### Kafka 설정

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka 브로커 주소 (예: `localhost:9092` 또는 `localhost:9092,localhost:9093`)
- `KAFKA_TOPICS`: 구독할 토픽 목록 (예: `cointicker.raw.*`)
- `KAFKA_GROUP_ID`: Consumer Group ID (예: `cointicker-consumer`)

#### HDFS 설정

- `HDFS_NAMENODE`: HDFS NameNode 주소 (예: `hdfs://localhost:9000`)

#### 데이터베이스 설정

- `DATABASE_TYPE`: 데이터베이스 타입 (예: `mariadb`, `postgresql`, `sqlite`)
- `DATABASE_HOST`: 데이터베이스 호스트 (예: `localhost`)
- `DATABASE_PORT`: 데이터베이스 포트 (예: `3306`, `5432`)
- `DATABASE_USER`: 데이터베이스 사용자명
- `DATABASE_PASSWORD`: 데이터베이스 비밀번호
- `DATABASE_NAME`: 데이터베이스 이름
- `USE_SQLITE`: SQLite 강제 사용 (`true`/`false`)

#### Scrapyd 설정

- `SCRAPYD_URL`: Scrapyd 서버 URL (예: `http://localhost:6800`)

#### API 설정

- `API_HOST`: API 서버 호스트 (예: `0.0.0.0`)
- `API_PORT`: API 서버 포트 (예: `5000`, `5001`)

#### 로깅 설정

- `LOG_LEVEL`: 로그 레벨 (예: `INFO`, `DEBUG`, `WARNING`, `ERROR`)

### 설정 파일 위치

모든 설정 파일은 `PICU/cointicker/config/` 디렉토리에 위치합니다:

- `kafka_config.yaml`: Kafka 설정
- `cluster_config.yaml`: 클러스터 및 HDFS 설정
- `database_config.yaml`: 데이터베이스 설정
- `spider_config.yaml`: Spider 스케줄 및 설정
- `gui_config.yaml`: GUI 설정

### 사용 예시

#### 개발 환경 (설정 파일 사용)

```bash
# 설정 파일 수정
vim PICU/cointicker/config/kafka_config.yaml
```

#### 프로덕션 환경 (환경 변수 사용)

```bash
# 환경 변수 설정
export KAFKA_BOOTSTRAP_SERVERS="kafka1:9092,kafka2:9092"
export HDFS_NAMENODE="hdfs://namenode:9000"
export DATABASE_HOST="db.example.com"
export DATABASE_PASSWORD="secure_password"

# 애플리케이션 실행
python -m gui.main
```

#### Docker/Kubernetes 환경

```yaml
# docker-compose.yml 또는 Kubernetes ConfigMap
environment:
  - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
  - HDFS_NAMENODE=hdfs://namenode:9000
  - DATABASE_HOST=postgres
  - DATABASE_PASSWORD=${DB_PASSWORD}
```

### 모듈별 설정 파일 매핑

| 모듈                                           | 읽는 설정 파일                                | 환경 변수 지원 |
| ---------------------------------------------- | --------------------------------------------- | -------------- |
| `backend/config.py`                            | `database_config.yaml`, `cluster_config.yaml` | ✅             |
| `worker-nodes/cointicker/settings.py`          | `kafka_config.yaml`, `cluster_config.yaml`    | ✅             |
| `master-node/orchestrator.py`                  | `spider_config.yaml`                          | ❌             |
| `master-node/scheduler.py`                     | `spider_config.yaml`                          | ✅             |
| `worker-nodes/kafka/kafka_consumer_service.py` | `kafka_config.yaml`                           | ✅             |
| `gui/core/config_manager.py`                   | 모든 YAML 설정                                | ✅             |

---

**보고서 작성 완료**
**최종 업데이트**: 2025-12-06 (레거시 하드코딩 제거 및 환경 변수 지원 추가)
