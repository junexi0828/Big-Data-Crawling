# 다중 프로젝트 독립 배포 가이드

## 🎯 목표

하나의 도메인(`eieconcierge.com`)에서 3개의 독립 프로젝트를 배포:

1. **voice-summarizer** → `https://eieconcierge.com/` (루트)
2. **frontend** → `https://eieconcierge.com/cointicker/`
3. **IR-dashboard** → `https://eieconcierge.com/IR/`

모든 프로젝트는 독립적으로 배포되며, voice-summarizer의 rewrites를 통해 연결됩니다.

---

## 📋 배포 순서

### 1단계: frontend 배포 (React SPA)

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/frontend

# Vercel CLI 설치 (처음 한 번만)
npm install -g vercel
vercel login

# 새 프로젝트로 배포
vercel
# - Set up and deploy? Y
# - Link to existing project? N
# - Project name? cointicker-frontend
# - Directory? ./
# - Override settings? N

# 프로덕션 배포
vercel --prod
```

**배포 후 URL 확인**: `https://cointicker-frontend-xxxxx.vercel.app`

---

### 2단계: IR-dashboard 배포 (정적 HTML)

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/IR-dashboard

# 새 프로젝트로 배포
vercel
# - Set up and deploy? Y
# - Link to existing project? N
# - Project name? ir-dashboard
# - Directory? ./
# - Override settings? N

# 프로덕션 배포
vercel --prod
```

**배포 후 URL 확인**: `https://ir-dashboard-xxxxx.vercel.app`

---

### 3단계: voice-summarizer vercel.json 수정

voice-summarizer 프로젝트의 `vercel.json`에 rewrites 추가:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    // ... 기존 routes 유지 ...
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "rewrites": [
    {
      "source": "/cointicker",
      "destination": "https://cointicker-frontend-xxxxx.vercel.app/"
    },
    {
      "source": "/cointicker/(.*)",
      "destination": "https://cointicker-frontend-xxxxx.vercel.app/$1"
    },
    {
      "source": "/IR",
      "destination": "https://ir-dashboard-xxxxx.vercel.app/IR/"
    },
    {
      "source": "/IR/(.*)",
      "destination": "https://ir-dashboard-xxxxx.vercel.app/IR/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "http://192.168.1.24:3001",
    "CI": "false"
  }
}
```

⚠️ **중요**:

- `cointicker-frontend-xxxxx.vercel.app`를 실제 frontend 배포 URL로 변경
- `ir-dashboard-xxxxx.vercel.app`를 실제 IR-dashboard 배포 URL로 변경

---

### 4단계: voice-summarizer 재배포

```bash
cd /Users/juns/code/personal/notion/juns_workspace/voice-summarizer

git add vercel.json
git commit -m "feat: cointicker 및 IR-dashboard 경로 연결"
git push
```

또는 Vercel CLI로:

```bash
vercel --prod
```

---

### 5단계: voice-summarizer에서 기존 파일 삭제

배포 성공 및 모든 경로 정상 작동 확인 후:

```bash
cd /Users/juns/code/personal/notion/juns_workspace/voice-summarizer

# 기존 cointicker 폴더 삭제
rm -rf public/cointicker
rm -rf build/cointicker

# 커밋 및 푸시
git add .
git commit -m "chore: cointicker 파일 제거 (별도 프로젝트로 분리)"
git push
```

---

## ✅ 최종 접속 URL

배포 완료 후:

- **voice-summarizer**: `https://eieconcierge.com/`
- **frontend**:
  - `https://eieconcierge.com/cointicker/`
  - `https://eieconcierge.com/cointicker/demo`
  - `https://eieconcierge.com/cointicker/live-dashboard`
  - 등등...
- **IR-dashboard**:
  - `https://eieconcierge.com/IR/`
  - `https://eieconcierge.com/IR/dashboard.html`
  - `https://eieconcierge.com/IR/architecture.html`
  - 등등...

---

## 🔍 확인 사항

### 각 프로젝트 독립 배포 확인

1. **frontend**: `https://cointicker-frontend-xxxxx.vercel.app` 접속 가능
2. **IR-dashboard**: `https://ir-dashboard-xxxxx.vercel.app` 접속 가능
3. **voice-summarizer**: `https://eieconcierge.com` 접속 가능

### 경로 연결 확인

1. `https://eieconcierge.com/cointicker/` → frontend 프로젝트로 연결
2. `https://eieconcierge.com/IR/` → IR-dashboard 프로젝트로 연결
3. 모든 하위 경로 정상 작동 확인

---

## 💡 장점

- ✅ **독립 배포**: 각 프로젝트를 독립적으로 배포 및 관리
- ✅ **독립 스케일링**: 각 프로젝트별로 리소스 최적화
- ✅ **빠른 배포**: 한 프로젝트 변경 시 다른 프로젝트 영향 없음
- ✅ **단일 도메인**: 하나의 도메인으로 통합 관리
- ✅ **자동 HTTPS**: Vercel이 자동으로 HTTPS 인증서 발급

---

## 🚨 주의사항

1. **URL 변경 시**: voice-summarizer의 vercel.json도 함께 업데이트 필요
2. **캐싱**: Vercel CDN 캐싱으로 인해 변경사항 반영에 시간이 걸릴 수 있음
3. **환경 변수**: 각 프로젝트의 환경 변수는 독립적으로 관리

---

## 📝 체크리스트

- [ ] frontend 배포 완료 및 URL 확인
- [ ] IR-dashboard 배포 완료 및 URL 확인
- [ ] voice-summarizer vercel.json에 rewrites 추가
- [ ] voice-summarizer 재배포
- [ ] 모든 경로 접속 테스트
- [ ] voice-summarizer에서 기존 파일 삭제

---

**Last Updated**: 2025-12-03
