# Vercel 배포 가이드: eieconcierge.com

## 🎯 목표

`https://eieconcierge.com` 루트 도메인에 PICU 대시보드 배포하기

---

## 방법 1: 기존 eieconcierge.com Vercel 프로젝트에 통합 (추천) ⭐

### 단계:

1. **PICU 파일들을 루트 디렉토리에 배치**

   ```bash
   # 기존 eieconcierge.com 프로젝트 폴더에
   # IR-dashboard 폴더의 파일들을 루트로 복사
   cp -r PICU/IR-dashboard/* [기존프로젝트]/
   ```

2. **기존 vercel.json에 rewrites 추가** (또는 새로 생성)

   ```json
   {
     "rewrites": [
       {
         "source": "/",
         "destination": "/index.html"
       },
       {
         "source": "/IR",
         "destination": "/IR/index.html"
       },
       {
         "source": "/IR/(.*)",
         "destination": "/IR/$1"
       },
       {
         "source": "/investment-dashboard",
         "destination": "/investment_dashboard.html"
       },
       {
         "source": "/finance-simulation",
         "destination": "/financeexpect.html"
       }
     ],
     "cleanUrls": true,
     "trailingSlash": false
   }
   ```

3. **Git에 커밋 및 푸시**

   ```bash
   git add .
   git commit -m "feat: PICU 대시보드 추가 (루트 도메인)"
   git push
   ```

4. **Vercel 자동 배포**
   - Vercel이 자동으로 감지하고 배포합니다

✅ **접속**: https://eieconcierge.com

---

## 방법 2: 별도 Vercel 프로젝트로 배포 + 기존 도메인에 경로 연결 (추천) ⭐

IR-dashboard를 별도 프로젝트로 배포하고, 기존 `eieconcierge.com` 프로젝트의 rewrites를 통해 `/IR/` 경로로 연결합니다.

### 단계:

1. **IR-dashboard 폴더로 이동**

   ```bash
   cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/IR-dashboard
   ```

2. **Vercel CLI 설치 및 로그인** (처음 한 번만)

   ```bash
   npm install -g vercel
   vercel login
   ```

3. **Vercel 프로젝트 초기화 및 배포**

   ```bash
   vercel
   ```

   설정 질문에 답변:

   - Set up and deploy? `Y`
   - Which scope? [계정 선택]
   - Link to existing project? `N` (새 프로젝트 생성)
   - Project name? `ir-dashboard` (원하는 이름)
   - Directory? `./` (현재 디렉토리)
   - Override settings? `N`

4. **프로덕션 배포**

   ```bash
   vercel --prod
   ```

   배포 후 Vercel이 제공하는 URL을 확인합니다:

   - 예: `https://ir-dashboard-xxxxx.vercel.app`

5. **기존 eieconcierge.com 프로젝트의 vercel.json에 rewrites 추가**

   기존 `eieconcierge.com` 프로젝트 폴더의 `vercel.json`에 다음을 추가:

   ```json
   {
     "rewrites": [
       {
         "source": "/IR",
         "destination": "https://ir-dashboard-xxxxx.vercel.app/"
       },
       {
         "source": "/IR/(.*)",
         "destination": "https://ir-dashboard-xxxxx.vercel.app/$1"
       }
     ]
   }
   ```

   ⚠️ **중요**: `ir-dashboard-xxxxx.vercel.app`를 실제 배포된 URL로 변경하세요!

6. **기존 프로젝트 재배포**

   ```bash
   cd [기존-eieconcierge.com-프로젝트-폴더]
   git add vercel.json
   git commit -m "feat: IR 대시보드 경로 추가"
   git push
   ```

   또는 Vercel CLI로:

   ```bash
   vercel --prod
   ```

7. **완료!**

   ✅ **접속**:

   - https://eieconcierge.com/IR/ (메인 대시보드)
   - https://eieconcierge.com/IR/dashboard.html
   - https://eieconcierge.com/IR/architecture.html
   - 등등...

   - 기존 `eieconcierge.com` 프로젝트는 그대로 유지
   - `/IR/` 경로만 새 프로젝트로 연결됨
   - 자동으로 HTTPS 적용
   - CDN 캐싱 자동 설정

### 도메인 설정이 필요한가요?

**아니요, 필요 없습니다!**

이 방법은 기존 `eieconcierge.com` 프로젝트의 rewrites를 사용하므로:

- ✅ 별도 도메인 설정 불필요
- ✅ DNS 레코드 추가 불필요
- ✅ 기존 도메인 그대로 사용
- ✅ `/IR/` 경로만 새 프로젝트로 연결

### GitHub 연동 (자동 배포)

1. **GitHub 리포지토리와 연결**

   ```bash
   vercel link
   ```

   - GitHub 리포지토리 선택
   - 자동으로 연동됨

2. **이후 자동 배포**
   - `git push` 할 때마다 자동 배포
   - PR 생성 시 미리보기 URL 자동 생성

---

## 방법 3: GitHub 연동으로 자동 배포 (가장 편리)

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
   - `eieconcierge.com` 추가
   - DNS 설정 가이드에 따라 도메인 DNS 레코드 수정

---

## 🔧 기존 프로젝트 vercel.json 설정 예시

기존 `eieconcierge.com` 프로젝트의 `vercel.json`에 IR-dashboard 프로젝트로 rewrites 추가:

```json
{
  "rewrites": [
    {
      "source": "/IR",
      "destination": "https://ir-dashboard-xxxxx.vercel.app/"
    },
    {
      "source": "/IR/(.*)",
      "destination": "https://ir-dashboard-xxxxx.vercel.app/$1"
    }
  ]
}
```

⚠️ **주의**:

- `ir-dashboard-xxxxx.vercel.app`를 실제 배포된 IR-dashboard 프로젝트 URL로 변경하세요
- 기존 rewrites는 그대로 유지하고 위 항목만 추가하면 됩니다

---

## 📋 최종 접속 URL

설정 완료 후:

- https://eieconcierge.com/ (메인 대시보드)
- https://eieconcierge.com/IR (IR 대시보드)
- https://eieconcierge.com/investment-dashboard (투자 대시보드)
- https://eieconcierge.com/finance-simulation (금융 시뮬레이션)

---

## 🚀 즉시 실행 가능한 명령어

### 별도 프로젝트로 배포 (추천)

```bash
# 1. IR-dashboard 폴더로 이동
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/IR-dashboard

# 2. Vercel CLI 설치 (처음 한 번만)
npm install -g vercel

# 3. 로그인 (처음 한 번만)
vercel login

# 4. 새 프로젝트로 배포
vercel

# 5. 프로덕션 배포
vercel --prod
```

### 도메인 연결 (Vercel 대시보드에서)

1. https://vercel.com/dashboard 접속
2. 배포한 프로젝트 선택
3. Settings → Domains
4. `eieconcierge.com` 추가
5. DNS 설정 가이드에 따라 도메인 DNS 레코드 수정

### GitHub 연동 (자동 배포 설정)

```bash
# GitHub 리포지토리와 연결
vercel link

# 이후 git push 시 자동 배포됨
git push
```

---

## 💡 팁

- **Cache 설정**: 정적 파일이므로 CDN 캐시 효율적
- **자동 배포**: GitHub push 시 자동 배포됨
- **미리보기**: PR 생성 시 자동 미리보기 URL 생성
- **분석**: Vercel Analytics 무료로 사용 가능

---

필요한 부분 도와드릴까요? 😊
