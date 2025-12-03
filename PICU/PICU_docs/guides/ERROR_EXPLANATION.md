# GUI 오류 설명 가이드

## 📋 오류 종류별 설명

### 1. SSH 연결 실패 (정상 - 클러스터 미구성 시)

```
ERROR - SSH 연결 실패 192.168.1.100: timed out
ERROR - SSH 연결 실패 192.168.1.101: timed out
ERROR - SSH 연결 실패 192.168.1.102: timed out
ERROR - SSH 연결 실패 192.168.1.103: timed out
```

**원인:**

- 라즈베리파이 클러스터가 아직 구성되지 않았거나
- 클러스터 노드가 네트워크에 연결되지 않았거나
- SSH 접근이 불가능한 상태

**해결 방법:**

- 라즈베리파이 클러스터를 구성하지 않았다면 **정상적인 오류**입니다
- 클러스터를 구성한 후에는 `config/cluster_config.yaml`에서 IP 주소를 확인하세요
- SSH 키 설정이 필요할 수 있습니다

**영향:**

- 클러스터 모니터링 기능만 사용 불가
- 나머지 기능(백엔드, 프론트엔드, 로컬 스파이더 등)은 정상 작동

---

### 2. Tier2 서버 403 오류 (백엔드 미실행)

```
ERROR - 헬스 체크 실패: 403 Client Error: Forbidden for url: http://localhost:5000/health
ERROR - 대시보드 요약 가져오기 실패: 403 Client Error: Forbidden
```

**원인:**

- 백엔드 서버가 실행되지 않았거나
- CORS 설정 문제 또는
- 포트가 다른 프로세스에 의해 사용 중

**해결 방법:**

1. **백엔드 서버 실행:**

   ```bash
   cd PICU/cointicker/backend
   bash run_server.sh
   ```

2. **포트 확인:**

   ```bash
   lsof -i :5000
   ```

3. **백엔드가 다른 포트로 실행 중인 경우:**
   - `config/gui_config.yaml`에서 `tier2.base_url` 수정
   - 또는 백엔드 포트를 5000으로 변경

**영향:**

- Tier2 대시보드 모니터링 기능 사용 불가
- 프론트엔드 웹 대시보드 사용 불가

---

### 3. Kafka Consumer 의존성 실패 (정상 - Kafka 미설치 시)

```
WARNING - 프로세스 시작 실패: kafka_consumer - 의존성 확인 실패: ['kafka_broker']
INFO - kafka_consumer의 의존성 시작 대기: ['kafka_broker']
```

**원인:**

- Kafka 브로커가 설치되지 않았거나
- Kafka 브로커가 실행되지 않았거나
- 포트 9092가 사용 불가능

**해결 방법:**

1. **Kafka 설치 및 실행 (선택적):**

   ```bash
   # Kafka 프로젝트 디렉토리에서
   cd PICU/kafka_project
   # Kafka 설치 및 실행 가이드 참조
   ```

2. **Kafka 없이 사용하려면:**
   - Kafka Consumer는 선택적 모듈입니다
   - Kafka 없이도 백엔드, 프론트엔드, 스파이더는 정상 작동합니다

**영향:**

- Kafka 기반 데이터 파이프라인만 사용 불가
- 나머지 기능은 정상 작동

---

### 4. Spider 직접 실행 불가 (정상)

```
WARNING - 프로세스 시작 실패: spider - 직접 실행 불가: spider
```

**원인:**

- Spider는 GUI에서 직접 실행할 수 없도록 설계됨
- Spider는 별도의 스크립트나 명령어로 실행해야 함

**해결 방법:**

1. **Spider를 GUI에서 실행하려면:**

   - `SpiderModule`이 제대로 등록되어 있어야 함
   - `gui/module_mapping.json`에 SpiderModule이 포함되어 있어야 함

2. **Spider를 직접 실행:**
   ```bash
   cd PICU/cointicker/worker-nodes
   scrapy crawl <spider_name>
   ```

**영향:**

- GUI에서 Spider 시작/중지 버튼이 작동하지 않을 수 있음
- 명령어로 직접 실행하면 정상 작동

---

## ✅ 정상 작동 조건

### 최소 구성 (클러스터 없이)

다음 구성만으로도 GUI는 정상 작동합니다:

1. ✅ **백엔드 서버 실행**

   ```bash
   cd PICU/cointicker/backend
   bash run_server.sh
   ```

2. ✅ **프론트엔드 서버 실행 (선택적)**

   ```bash
   cd PICU/cointicker/frontend
   bash run_dev.sh
   ```

3. ✅ **GUI 애플리케이션 실행**
   ```bash
   cd PICU
   bash start.sh
   # 옵션 1 선택
   ```

### 완전 구성 (모든 기능 사용)

1. ✅ 백엔드 서버
2. ✅ 프론트엔드 서버
3. ✅ Kafka 브로커 (선택적)
4. ✅ 라즈베리파이 클러스터 (선택적)
5. ✅ HDFS (선택적)

---

## 🔍 모듈 찾기 실패 원인

### 모듈을 못 찾는 경우

**원인:**

- `gui/module_mapping.json` 파일이 없거나
- 모듈 경로가 잘못되었거나
- 모듈 클래스가 존재하지 않음

**해결 방법:**

1. **module_mapping.json 확인:**

   ```bash
   cat PICU/cointicker/gui/module_mapping.json
   ```

2. **모듈 파일 확인:**

   ```bash
   ls -la PICU/cointicker/gui/modules/
   ```

3. **모듈 등록 확인:**
   - `module_mapping.json`에 모듈이 올바르게 등록되어 있는지 확인
   - 모듈 클래스가 올바른 경로에 있는지 확인

---

## 📝 요약

| 오류                  | 정상 여부                 | 해결 필요 여부 | 영향 범위                   |
| --------------------- | ------------------------- | -------------- | --------------------------- |
| SSH 연결 실패         | ✅ 정상 (클러스터 미구성) | ❌ 불필요      | 클러스터 모니터링만         |
| Tier2 403 오류        | ❌ 비정상                 | ✅ 필요        | Tier2 모니터링, 웹 대시보드 |
| Kafka 의존성 실패     | ✅ 정상 (Kafka 미설치)    | ❌ 불필요      | Kafka 파이프라인만          |
| Spider 직접 실행 불가 | ✅ 정상 (설계상)          | ❌ 불필요      | GUI에서 Spider 제어만       |

---

## 🚀 빠른 시작 (오류 없이)

```bash
# 1. 백엔드 실행
cd PICU/cointicker/backend
bash run_server.sh

# 2. 프론트엔드 실행 (새 터미널)
cd PICU/cointicker/frontend
bash run_dev.sh

# 3. GUI 실행 (새 터미널)
cd PICU
bash start.sh
# 옵션 1 선택
```

이렇게 하면 대부분의 오류가 해결됩니다!
