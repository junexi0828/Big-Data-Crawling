# 실사용자 흐름 테스트 가이드

## 📋 테스트 시나리오

실제 사용자가 처음 설치부터 사용까지의 전체 흐름을 테스트합니다.

## 🚀 테스트 순서

### 1단계: 처음 설치

```bash
# PICU 루트에서
bash setup_venv.sh
```

**예상 결과:**

- ✅ Python 버전 확인 완료
- ✅ 가상환경 생성 완료
- ✅ 의존성 설치 완료

**확인 사항:**

- `venv/` 디렉토리 생성 확인
- `requirements.txt`의 모든 패키지 설치 확인

---

### 2단계: GUI 열기

```bash
# 가상환경 활성화
source venv/bin/activate

# GUI 실행
bash run_gui.sh
```

**예상 결과:**

- ✅ GUI 애플리케이션 창이 열림
- ✅ 모듈 로드 성공
- ✅ 네비게이션 메뉴 표시

**확인 사항:**

- GUI 창이 정상적으로 열리는지
- 모듈 관리 탭에서 모든 모듈이 표시되는지
- 클러스터 모니터링 탭이 작동하는지

---

### 3단계: Backend 서버 실행

**새 터미널에서:**

```bash
# PICU 루트로 이동
cd /path/to/PICU

# 가상환경 활성화
source venv/bin/activate

# Backend 서버 실행
cd cointicker/backend
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

**예상 결과:**

- ✅ 서버가 `http://localhost:5000`에서 실행
- ✅ API 문서: `http://localhost:5000/docs`
- ✅ 헬스 체크: `http://localhost:5000/health`

**확인 사항:**

- 서버가 정상적으로 시작되는지
- API 엔드포인트가 응답하는지
- CORS 설정이 올바른지

---

### 4단계: 프론트엔드 실행

**새 터미널에서:**

```bash
# PICU 루트로 이동
cd /path/to/PICU

# Frontend 디렉토리로 이동
cd cointicker/frontend

# 의존성 설치 (처음만)
npm install

# 개발 서버 실행
npm run dev
```

**예상 결과:**

- ✅ 개발 서버가 `http://localhost:3000`에서 실행
- ✅ 브라우저에서 자동으로 열림
- ✅ 홈 페이지가 표시됨

**확인 사항:**

- 홈 페이지 (`/`)가 정상적으로 표시되는지
- 대시보드 (`/app`)가 정상적으로 표시되는지
- API 연결이 정상적인지 (Backend 서버 실행 필요)

---

## 🧪 통합 테스트

### 자동 테스트 스크립트

```bash
# 전체 시스템 테스트
bash test_full_system.sh

# 실사용자 흐름 테스트
bash test_user_flow.sh
```

### 수동 테스트 체크리스트

#### 설치 단계

- [ ] `bash setup_venv.sh` 실행 성공
- [ ] 가상환경 생성 확인
- [ ] 모든 의존성 설치 확인

#### GUI 단계

- [ ] `bash run_gui.sh` 실행 성공
- [ ] GUI 창이 열림
- [ ] 모든 모듈이 로드됨
- [ ] 네비게이션 메뉴 작동

#### Backend 단계

- [ ] Backend 서버 실행 성공
- [ ] `http://localhost:5000/health` 응답 확인
- [ ] `http://localhost:5000/docs` 접속 가능

#### Frontend 단계

- [ ] Frontend 개발 서버 실행 성공
- [ ] `http://localhost:3000` 접속 가능
- [ ] 홈 페이지 표시
- [ ] 대시보드 페이지 표시
- [ ] Backend API 연결 확인

---

## 🔍 문제 해결

### GUI가 열리지 않을 때

1. **PyQt5 확인:**

   ```bash
   python3 -c "import PyQt5; print('OK')"
   ```

2. **가상환경 확인:**

   ```bash
   source venv/bin/activate
   which python
   ```

3. **CLI 버전 사용:**
   ```bash
   python cointicker/gui/installer/installer_cli.py
   ```

### Backend 서버가 시작되지 않을 때

1. **포트 확인:**

   ```bash
   lsof -i :5000
   ```

2. **의존성 확인:**

   ```bash
   pip list | grep fastapi
   pip list | grep uvicorn
   ```

3. **데이터베이스 설정 확인:**
   - `cointicker/config/database_config.yaml` 확인

### Frontend가 실행되지 않을 때

1. **Node.js 확인:**

   ```bash
   node --version
   npm --version
   ```

2. **의존성 재설치:**

   ```bash
   rm -rf node_modules
   npm install
   ```

3. **포트 확인:**
   ```bash
   lsof -i :3000
   ```

---

## 📊 테스트 결과 기록

테스트 완료 후 다음 정보를 기록하세요:

- **테스트 날짜**:
- **환경**: macOS / Linux / Windows
- **Python 버전**:
- **Node.js 버전**:
- **통과한 테스트**:
- **실패한 테스트**:
- **발견된 문제**:

---

## ✅ 성공 기준

다음 모든 항목이 성공하면 테스트 통과:

1. ✅ 설치 스크립트 실행 성공
2. ✅ GUI 실행 성공
3. ✅ Backend 서버 실행 성공
4. ✅ Frontend 개발 서버 실행 성공
5. ✅ 모든 서비스가 정상적으로 통신

---

## 🎯 다음 단계

테스트가 모두 통과하면:

1. 실제 라즈베리파이에 배포 준비
2. 배포 스크립트 작성
3. 프로덕션 환경 테스트
