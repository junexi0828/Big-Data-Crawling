# Vercel 배포 가이드: eieconcierge.com/data

## 🎯 목표

`https://eieconcierge.com/data` 경로에 PICU 대시보드 배포하기

---

## 방법 1: 기존 eieconcierge.com Vercel 프로젝트에 통합 (추천) ⭐

### 단계:

1. **기존 프로젝트 폴더에 `/data` 디렉토리 생성**

   ```bash
   # 기존 eieconcierge.com 프로젝트 폴더에서
   mkdir data
   ```

2. **PICU 파일들을 `/data` 폴더로 복사**

   ```bash
   cp /Users/juns/PICU/index.html [기존프로젝트]/data/
   cp /Users/juns/PICU/investment_dashboard.html [기존프로젝트]/data/
   cp /Users/juns/PICU/financeexpect.html [기존프로젝트]/data/
   ```

3. **기존 vercel.json에 rewrites 추가** (또는 새로 생성)

   ```json
   {
     "rewrites": [
       {
         "source": "/data",
         "destination": "/data/index.html"
       },
       {
         "source": "/data/(.*)",
         "destination": "/data/$1"
       }
     ]
   }
   ```

4. **Git에 커밋 및 푸시**

   ```bash
   git add .
   git commit -m "feat: PICU 데이터 대시보드 추가 (/data)"
   git push
   ```

5. **Vercel 자동 배포**
   - Vercel이 자동으로 감지하고 배포합니다

✅ **접속**: https://eieconcierge.com/data

---

## 방법 2: 새 Vercel 프로젝트 + Monorepo 구조

### 단계:

1. **Vercel CLI 설치 및 로그인**

   ```bash
   npm install -g vercel
   vercel login
   ```

2. **PICU 폴더에서 배포**

   ```bash
   cd /Users/juns/PICU
   vercel
   ```

3. **Vercel 설정 질문에 답변**

   - Set up and deploy? `Y`
   - Which scope? [계정 선택]
   - Link to existing project? `N`
   - Project name? `picu-data`
   - Directory? `./`
   - Override settings? `N`

4. **프로덕션 배포**

   ```bash
   vercel --prod
   ```

5. **기존 도메인 프로젝트의 vercel.json에 리라이트 추가**
   ```json
   {
     "rewrites": [
       {
         "source": "/data/:path*",
         "destination": "https://picu-data.vercel.app/:path*"
       }
     ]
   }
   ```

---

## 방법 3: GitHub 연동 (가장 자동화)

### 단계:

1. **Vercel 대시보드 접속**

   - https://vercel.com/dashboard

2. **New Project 클릭**

   - Import Git Repository
   - GitHub: `junexi0828/PICU` 선택

3. **프로젝트 설정**

   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (비워두기)
   - Output Directory: `.`

4. **Deploy 클릭**

5. **도메인 설정**

   - Project Settings → Domains
   - `data.eieconcierge.com` 추가

   또는 기존 프로젝트에서 rewrites 사용

---

## 🔧 추천 vercel.json 설정 (기존 프로젝트용)

기존 `eieconcierge.com` 프로젝트의 `vercel.json`에 추가:

```json
{
  "rewrites": [
    {
      "source": "/data",
      "destination": "/data/index.html"
    },
    {
      "source": "/data/investment-dashboard",
      "destination": "/data/investment_dashboard.html"
    },
    {
      "source": "/data/finance-simulation",
      "destination": "/data/financeexpect.html"
    },
    {
      "source": "/data/:path*",
      "destination": "/data/:path*"
    }
  ],
  "cleanUrls": true,
  "trailingSlash": false
}
```

---

## 📋 최종 접속 URL

설정 완료 후:

- https://eieconcierge.com/data
- https://eieconcierge.com/data/investment-dashboard
- https://eieconcierge.com/data/finance-simulation

---

## 🚀 즉시 실행 가능한 명령어

### GitHub 연동 방식 (가장 추천)

```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. 로그인
vercel login

# 3. 현재 프로젝트 링크 (GitHub 리포지토리 연동)
cd /Users/juns/PICU
vercel link

# 4. 배포
vercel --prod
```

그런 다음 Vercel 대시보드에서 기존 `eieconcierge.com` 프로젝트 설정에 위 rewrites 추가!

---

## 💡 팁

- **Cache 설정**: 정적 파일이므로 CDN 캐시 효율적
- **자동 배포**: GitHub push 시 자동 배포됨
- **미리보기**: PR 생성 시 자동 미리보기 URL 생성
- **분석**: Vercel Analytics 무료로 사용 가능

---

필요한 부분 도와드릴까요? 😊
