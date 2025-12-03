# 🚀 IR-dashboard 즉시 배포 가이드

## 현재 문제
- IR-dashboard가 아직 Vercel에 배포되지 않음
- voice-summarizer의 vercel.json에 플레이스홀더 URL(`xxxxx`)이 있음
- 404 에러 발생

## 해결 방법

### 1단계: IR-dashboard 배포

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/IR-dashboard

# Vercel CLI 설치 (없는 경우)
npm install -g vercel

# 로그인 (처음 한 번만)
vercel login

# 새 프로젝트로 배포
vercel
# 질문에 답변:
# - Set up and deploy? Y
# - Link to existing project? N (새 프로젝트)
# - Project name? ir-dashboard
# - Directory? ./
# - Override settings? N

# 프로덕션 배포
vercel --prod
```

**중요**: 배포 후 출력되는 URL을 복사하세요!
예: `https://ir-dashboard-abc123.vercel.app`

### 2단계: voice-summarizer vercel.json 업데이트

배포된 실제 URL을 voice-summarizer의 vercel.json에 업데이트:

```json
{
  "rewrites": [
    {
      "source": "/IR",
      "destination": "https://[실제-배포-URL]/"
    },
    {
      "source": "/IR/(.*)",
      "destination": "https://[실제-배포-URL]/$1"
    }
  ]
}
```

예시:
```json
{
  "rewrites": [
    {
      "source": "/IR",
      "destination": "https://ir-dashboard-abc123.vercel.app/"
    },
    {
      "source": "/IR/(.*)",
      "destination": "https://ir-dashboard-abc123.vercel.app/$1"
    }
  ]
}
```

### 3단계: voice-summarizer 재배포

```bash
cd /Users/juns/code/personal/notion/juns_workspace/voice-summarizer
git add vercel.json
git commit -m "fix: IR-dashboard 실제 배포 URL로 업데이트"
git push
```

또는 Vercel CLI로:
```bash
vercel --prod
```

## 확인 사항

배포 후 다음 URL들이 정상 작동해야 합니다:

- ✅ `https://eieconcierge.com/IR/` → IR-dashboard 메인
- ✅ `https://eieconcierge.com/IR/index.html` → IR-dashboard 메인
- ✅ `https://eieconcierge.com/IR/demo.html` → 데모 페이지
- ✅ `https://eieconcierge.com/IR/live-dashboard.html` → 실시간 대시보드
- ✅ `https://eieconcierge.com/IR/architecture.html` → 아키텍처
- ✅ `https://eieconcierge.com/IR/performance.html` → 성능 모니터링
- ✅ `https://eieconcierge.com/IR/data-pipeline.html` → 데이터 파이프라인
- ✅ `https://eieconcierge.com/IR/dashboard.html` → 대시보드

## 현재 vercel.json 설정

IR-dashboard의 vercel.json은 이미 올바르게 설정되어 있습니다:
- `/` → `/IR/index.html`
- `/IR` → `/IR/index.html`
- `/IR/` → `/IR/index.html`
- `/IR/(.*)` → `/IR/$1`

voice-summarizer의 rewrites도 수정되었습니다:
- `/IR` → `https://ir-dashboard-xxxxx.vercel.app/` (실제 URL로 변경 필요)
- `/IR/(.*)` → `https://ir-dashboard-xxxxx.vercel.app/$1` (실제 URL로 변경 필요)

