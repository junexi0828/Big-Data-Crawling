# PICU 프로젝트 개선 실행 계획

**작성 일시**: 2025-12-02
**목적**: 문서 분석 결과를 바탕으로 한 실용적이고 단계적인 실행 계획 수립
**기준 문서**:

- `FOLDER_STRUCTURE_REVIEW_COMPLETE.md` - 폴더 구조 점검 보고서
- `DEPLOYMENT_STRUCTURE_ANALYSIS.md` - 배포 구조 분석
- `REQUIREMENTS_MANAGEMENT_STRATEGY.md` - Requirements 관리 전략
- `DOCUMENT_CLEANUP_REPORT.md` - ISO/SPICE 표준 준수 보고서

---

## 🎯 전체 개선 목표

1. **즉시 해결**: 스크립트 오류 수정 (4개 스크립트)
2. **안전한 정리**: 중복 파일 및 캐시 정리
3. **구조 개선**: Requirements 및 venv 구조 표준화
4. **표준 준수**: ISO/SPICE 기준 문서 생성 (장기)

---

## 📋 단계별 실행 계획

### 🔴 Phase 1: 긴급 수정 (즉시 실행) - 약 30분

**목표**: 스크립트 오류 해결 및 기본 구조 정리

#### 1.1 PICU/requirements.txt 생성 (필수) ⚡

**문제**: 4개 스크립트가 `PICU/requirements.txt`를 찾지 못해 오류 발생

**영향받는 스크립트**:

- `scripts/start.sh`
- `scripts/test_user_flow.sh`
- `cointicker/gui/scripts/install.sh`
- `cointicker/tests/run_integration_tests.sh`

**작업 내용**:

```bash
# 1. requirements/ 디렉토리 구조 확인
cd PICU
ls -la requirements/

# 2. base.txt 생성 (공통 의존성)
cat > requirements/base.txt << 'EOF'
# 공통 의존성 (모든 노드)
pyyaml>=6.0.1
python-dotenv>=1.0.0
loguru>=0.7.2
hdfs>=2.7.0
kafka-python>=2.0.2
EOF

# 3. dev.txt 생성 (개발 환경)
cat > requirements/dev.txt << 'EOF'
-r base.txt

# GUI 개발
pyqt5>=5.15.0

# 테스트
pytest>=7.4.0
pytest-cov>=4.1.0

# Scrapy (로컬 테스트용)
scrapy>=2.11.0
beautifulsoup4>=4.12.0
requests>=2.31.0
selenium>=4.0.0
webdriver-manager>=4.0.1

# 코드 품질
black>=23.0.0
flake8>=6.0.0

# Tier2 (로컬 테스트용)
flask>=3.0.0
flask-cors>=4.0.0
pymongo>=4.6.0
pandas>=2.1.0
numpy>=1.24.0
pyarrow>=14.0.0

# 기타 개발 도구
ipython>=8.0.0
jupyter>=1.0.0
EOF

# 4. PICU/requirements.txt 생성 (심볼릭 링크)
ln -s requirements/dev.txt requirements.txt

# 5. 검증
ls -la requirements.txt
cat requirements.txt | head -5
```

**예상 시간**: 10분
**검증 방법**: `bash scripts/start.sh` 실행하여 오류 없이 동작 확인

---

#### 1.2 안전한 정리 작업 (캐시 및 중복 파일)

**작업 내용**:

```bash
# 1. .scrapy/ 캐시 삭제 (안전 - 자동 재생성됨)
rm -rf ./cointicker/worker-nodes/.scrapy/

# 2. .gitignore 업데이트
cat >> ./cointicker/.gitignore << 'EOF'
# Scrapy 캐시
.scrapy/
*.pyc
__pycache__/

# 임시 데이터
data/temp/
*.log

# 런타임 파일
.backend_port
.frontend_port
EOF

# 3. gui_config.yaml 심볼릭 링크로 통합
# (두 파일이 동일한지 먼저 확인)
diff PICU/config/gui_config.yaml PICU/cointicker/config/gui_config.yaml

# 동일하면 심볼릭 링크 생성
rm ./cointicker/config/gui_config.yaml
ln -s ../../config/gui_config.yaml ./cointicker/config/gui_config.yaml

# 4. 검증
ls -la ./cointicker/config/gui_config.yaml
```

**예상 시간**: 5분
**검증 방법**: GUI 실행하여 설정 파일 정상 로드 확인

---

#### 1.3 배포 스크립트 파일명 정리 (선택)

**작업 내용**:

```bash
# requirements/ 디렉토리 파일명 변경
cd requirements/
mv requirements-master.txt master.txt
mv requirements-worker.txt worker.txt
mv requirements-tier2.txt tier2.txt

# 배포 스크립트 수정 필요 (deployment/setup_master.sh, setup_worker.sh)
# 이 작업은 배포 테스트 전에 수행
```

**예상 시간**: 5분
**주의**: 배포 스크립트도 함께 수정 필요

---

**Phase 1 완료 체크리스트**:

- [ ] `PICU/requirements.txt` 생성 완료
- [ ] `requirements/base.txt` 생성 완료
- [ ] `requirements/dev.txt` 생성 완료
- [ ] `.scrapy/` 캐시 삭제 완료
- [ ] `.gitignore` 업데이트 완료
- [ ] `gui_config.yaml` 심볼릭 링크 생성 완료
- [ ] 스크립트 오류 해결 확인 (`scripts/start.sh` 테스트)

---

### 🟡 Phase 2: 구조 개선 (테스트 후 실행) - 약 1시간

**목표**: Requirements 구조 완전 개선 및 venv 통합

#### 2.1 Requirements 구조 완전 개선

**작업 내용**:

```bash
# 1. 기존 requirements 파일 확인
cd requirements/
ls -la

# 2. master.txt, worker.txt, tier2.txt에 base.txt 참조 추가
# (파일명이 이미 변경되었다면 이 단계 생략)

# 3. 각 파일에 -r base.txt 추가 (파일 맨 앞에)
# master.txt
echo "-r base.txt" | cat - master.txt > temp && mv temp master.txt

# worker.txt
echo "-r base.txt" | cat - worker.txt > temp && mv temp worker.txt

# tier2.txt
echo "-r base.txt" | cat - tier2.txt > temp && mv temp tier2.txt

# 4. cointicker/requirements.txt를 심볼릭 링크로 전환 (선택)
cd ..
mv cointicker/requirements.txt cointicker/requirements.txt.bak
ln -s ../requirements.txt cointicker/requirements.txt

# 5. 검증
cat requirements/master.txt | head -3
cat requirements/worker.txt | head -3
cat requirements/tier2.txt | head -3
```

**예상 시간**: 15분
**검증 방법**: 각 requirements 파일이 base.txt를 참조하는지 확인

---

#### 2.2 배포 스크립트 수정

**작업 내용**:

```bash
# deployment/setup_master.sh 수정
# 변경 전: requirements-master.txt
# 변경 후: master.txt

# deployment/setup_worker.sh 수정
# 변경 전: requirements-worker.txt
# 변경 후: worker.txt
```

**예상 시간**: 10분
**주의**: 실제 배포 전에 테스트 필요

---

#### 2.3 venv 통합 (선택, 신중히)

**작업 내용**:

```bash
# 1. 현재 venv 백업
mv ./cointicker/venv ./cointicker/venv.bak
mv ./scripts/venv ./scripts/venv.bak

# 2. 루트 venv 확인 또는 재생성
if [ ! -d "./venv" ]; then
    python3 -m venv ./venv
fi

# 3. 루트 venv에 의존성 설치
source ./venv/bin/activate
pip install -r requirements.txt

# 4. 심볼릭 링크 생성
ln -s ../venv ./cointicker/venv
ln -s ../venv ./scripts/venv

# 5. 테스트 (모든 스크립트 실행 확인)
# 성공 시 백업 삭제
# rm -rf ./cointicker/venv.bak ./scripts/venv.bak
```

**예상 시간**: 20분
**주의**: 모든 스크립트가 정상 작동하는지 충분히 테스트 필요

---

#### 2.4 data/temp/ 통합 (선택, 신중히)

**작업 내용**:

```bash
# 1. 백업
mkdir -p ./backup/data_temp_backup
cp -r ./cointicker/worker-nodes/data/temp/* ./backup/data_temp_backup/ 2>/dev/null || true
cp -r ./cointicker/worker-nodes/cointicker/data/temp/* ./backup/data_temp_backup/ 2>/dev/null || true

# 2. 메인 디렉토리로 데이터 이동
mkdir -p ./cointicker/data/temp/
cp -r ./cointicker/worker-nodes/data/temp/* ./cointicker/data/temp/ 2>/dev/null || true
cp -r ./cointicker/worker-nodes/cointicker/data/temp/* ./cointicker/data/temp/ 2>/dev/null || true

# 3. 심볼릭 링크 생성
rm -rf ./cointicker/worker-nodes/data/temp/
ln -s ../../data/temp ./cointicker/worker-nodes/data/temp

rm -rf ./cointicker/worker-nodes/cointicker/data/temp/
ln -s ../../../data/temp ./cointicker/worker-nodes/cointicker/data/temp

# 4. 테스트 (Scrapy, 파이프라인 실행)
# 성공 시 백업 삭제
# rm -rf ./backup/data_temp_backup
```

**예상 시간**: 10분
**주의**: Scrapy 및 파이프라인 실행 후 데이터 경로 정상 작동 확인 필요

---

**Phase 2 완료 체크리스트**:

- [ ] Requirements 구조 개선 완료
- [ ] 배포 스크립트 수정 완료
- [ ] venv 통합 완료 (선택)
- [ ] data/temp/ 통합 완료 (선택)
- [ ] 모든 스크립트 정상 작동 확인

---

### 🟢 Phase 3: 표준 준수 (장기 개선) - 약 2주

**목표**: ISO/SPICE 표준 준수를 위한 문서 생성

#### 3.1 필수 문서 생성 (우선순위 1)

**작업 내용**:

1. **테스트 계획서** (`planning/TEST_PLAN.md`)

   - 테스트 전략
   - 테스트 범위
   - 테스트 일정
   - 예상 시간: 2시간

2. **검증 계획서** (`planning/VERIFICATION_PLAN.md`)

   - 검증 기준
   - 검증 방법
   - 검증 일정
   - 예상 시간: 1.5시간

3. **확인 계획서** (`planning/VALIDATION_PLAN.md`)

   - 확인 기준
   - 확인 방법
   - 확인 일정
   - 예상 시간: 1.5시간

4. **품질 계획서** (`planning/QUALITY_PLAN.md`)

   - 품질 목표
   - 품질 기준
   - 품질 측정 방법
   - 예상 시간: 2시간

5. **형상 관리 계획서** (`planning/CONFIGURATION_MANAGEMENT_PLAN.md`)
   - 형상 관리 절차
   - 버전 관리 정책
   - 변경 관리 절차
   - 예상 시간: 1시간

**총 예상 시간**: 8시간 (1일 작업)

---

#### 3.2 문서 메타데이터 표준화 (우선순위 2)

**작업 내용**:

1. **문서 메타데이터 템플릿 생성**

   - `PICU_docs/templates/document_metadata_template.yaml` 생성
   - 예상 시간: 30분

2. **기존 문서에 메타데이터 추가**
   - 37개 문서에 YAML front matter 추가
   - 예상 시간: 8시간 (문서당 약 15분)

**총 예상 시간**: 8.5시간 (1일 작업)

---

#### 3.3 문서 템플릿 표준화 (우선순위 3)

**작업 내용**:

1. **템플릿 디렉토리 생성**

   - `PICU_docs/templates/` 생성
   - 예상 시간: 10분

2. **주요 문서 유형별 템플릿 생성**
   - 요구사항 명세서 템플릿
   - 설계 문서 템플릿
   - 테스트 계획서 템플릿
   - 검증/확인 보고서 템플릿
   - 문제 해결 보고서 템플릿
   - 예상 시간: 4시간

**총 예상 시간**: 4시간

---

**Phase 3 완료 체크리스트**:

- [ ] 필수 문서 5개 생성 완료
- [ ] 문서 메타데이터 표준화 완료
- [ ] 문서 템플릿 표준화 완료
- [ ] ISO/SPICE 준수도 향상 확인

---

## 🚀 권장 실행 순서

### 시나리오 A: 최소 조치 (권장 시작점)

**목표**: 스크립트 오류만 해결

1. ✅ **Phase 1.1**: PICU/requirements.txt 생성 (10분)
2. ✅ **Phase 1.2**: 안전한 정리 작업 (5분)

**총 시간**: 15분
**효과**: 스크립트 오류 해결, 기본 정리 완료

---

### 시나리오 B: 표준 조치 (권장)

**목표**: 구조 개선까지 완료

1. ✅ **Phase 1 전체** (30분)
2. ✅ **Phase 2.1**: Requirements 구조 완전 개선 (15분)
3. ✅ **Phase 2.2**: 배포 스크립트 수정 (10분)

**총 시간**: 55분
**효과**: 스크립트 오류 해결, 구조 표준화, 배포 준비 완료

---

### 시나리오 C: 완전 개선

**목표**: 모든 개선 사항 완료

1. ✅ **Phase 1 전체** (30분)
2. ✅ **Phase 2 전체** (1시간)
3. ✅ **Phase 3 전체** (2주)

**총 시간**: 약 2주
**효과**: 완전한 표준 준수 및 구조 개선

---

## ⚠️ 주의사항

### 실행 전 확인 사항

1. **Git 상태 확인**

   ```bash
   git status
   git diff
   ```

   - 변경 사항 커밋 또는 백업

2. **현재 작동하는 기능 확인**

   - GUI 실행 확인
   - Backend 실행 확인
   - Frontend 실행 확인
   - Scrapy 실행 확인

3. **백업 생성**
   ```bash
   # 중요 파일 백업
   cp -r requirements requirements.backup
   cp -r config config.backup
   ```

### 실행 중 주의사항

1. **Phase 1**: 안전하지만 스크립트 테스트 필요
2. **Phase 2**: 각 단계마다 테스트 필요
3. **Phase 3**: 문서 작업이므로 코드 영향 없음

### 실행 후 검증

1. **스크립트 테스트**

   ```bash
   bash scripts/start.sh
   bash scripts/test_user_flow.sh
   bash cointicker/tests/run_integration_tests.sh
   ```

2. **GUI 테스트**

   ```bash
   python cointicker/gui/main.py
   ```

3. **배포 스크립트 테스트** (가능한 경우)
   ```bash
   bash deployment/setup_master.sh --dry-run
   ```

---

## 📊 진행 상황 추적

### Phase 1 진행 상황

- [ ] 1.1 PICU/requirements.txt 생성
- [ ] 1.2 안전한 정리 작업
- [ ] 1.3 배포 스크립트 파일명 정리

### Phase 2 진행 상황

- [ ] 2.1 Requirements 구조 완전 개선
- [ ] 2.2 배포 스크립트 수정
- [ ] 2.3 venv 통합 (선택)
- [ ] 2.4 data/temp/ 통합 (선택)

### Phase 3 진행 상황

- [ ] 3.1 필수 문서 생성
- [ ] 3.2 문서 메타데이터 표준화
- [ ] 3.3 문서 템플릿 표준화

---

## 🎯 다음 단계 결정 가이드

### 지금 바로 시작할 것

1. **Phase 1.1**: PICU/requirements.txt 생성 (긴급)
2. **Phase 1.2**: 안전한 정리 작업 (빠르고 안전)

### 이번 주 내에 완료할 것

3. **Phase 2.1**: Requirements 구조 완전 개선
4. **Phase 2.2**: 배포 스크립트 수정

### 다음 주부터 시작할 것

5. **Phase 3**: ISO/SPICE 표준 준수 문서 생성

---

## 📝 체크리스트 요약

### 즉시 실행 (Phase 1)

- [ ] `PICU/requirements.txt` 생성
- [ ] `requirements/base.txt` 생성
- [ ] `requirements/dev.txt` 생성
- [ ] `.scrapy/` 캐시 삭제
- [ ] `.gitignore` 업데이트
- [ ] `gui_config.yaml` 심볼릭 링크 생성
- [ ] 스크립트 오류 해결 확인

### 구조 개선 (Phase 2)

- [ ] Requirements 구조 완전 개선
- [ ] 배포 스크립트 수정
- [ ] venv 통합 (선택)
- [ ] data/temp/ 통합 (선택)

### 표준 준수 (Phase 3)

- [ ] 필수 문서 5개 생성
- [ ] 문서 메타데이터 표준화
- [ ] 문서 템플릿 표준화

---

**작성자**: Juns Claude Code
**최종 업데이트**: 2025-12-02
**다음 검토**: Phase 1 완료 후
