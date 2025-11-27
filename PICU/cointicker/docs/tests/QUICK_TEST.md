# 빠른 테스트 가이드

## 🚀 3단계 빠른 테스트

### 1단계: 설치 (5분)

```bash
cd PICU
bash setup_venv.sh
```

### 2단계: GUI 테스트 (1분)

```bash
source venv/bin/activate
bash run_gui.sh
```

**확인:**

- GUI 창이 열리는지
- 모듈이 로드되는지

### 3단계: Backend + Frontend 테스트 (2분)

**터미널 1 - Backend:**

```bash
source venv/bin/activate
cd cointicker/backend
uvicorn app:app --host 0.0.0.0 --port 5000
```

**터미널 2 - Frontend:**

```bash
cd PICU/cointicker/frontend
npm install  # 처음만
npm run dev
```

**확인:**

- Backend: http://localhost:5000/health
- Frontend: http://localhost:3000

---

## ✅ 테스트 체크리스트

- [ ] 설치 성공
- [ ] GUI 실행 성공
- [ ] Backend 서버 실행 성공
- [ ] Frontend 개발 서버 실행 성공
- [ ] Frontend에서 Backend API 연결 확인

---

## 🎯 완료!

모든 테스트가 통과하면 배포 준비 완료입니다! 🚀
