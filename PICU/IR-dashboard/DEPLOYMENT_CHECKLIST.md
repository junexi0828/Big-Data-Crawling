# 🚀 IR-dashboard 배포 체크리스트

## ⚠️ 중요: voice-summarizer 삭제 전 필수 확인사항

### 현재 상황
- ✅ 파일 마이그레이션 완료: `PICU/IR-dashboard/IR/`로 모든 파일 이동
- ✅ 경로 수정 완료: `/cointicker/` → 상대 경로로 변경
- ⚠️ **기존 도메인은 아직 voice-summarizer 프로젝트에 연결됨**

### ❌ 삭제하면 안 되는 이유

1. **Vercel 자동 배포**
   - voice-summarizer 프로젝트는 Git과 연동되어 자동 배포됩니다
   - 파일을 삭제하면 다음 배포 시 `/cointicker` 경로가 작동하지 않습니다

2. **기존 도메인 연결**
   - `eieconcierge.com/cointicker/...`는 voice-summarizer 프로젝트를 가리킵니다
   - 파일 삭제 시 기존 링크가 깨집니다

---

## ✅ 배포 전 필수 단계

### 1단계: PICU/IR-dashboard를 새 Vercel 프로젝트로 배포

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/IR-dashboard

# Vercel CLI 설치 (없는 경우)
npm install -g vercel

# 로그인
vercel login

# 프로젝트 링크 (새 프로젝트 생성)
vercel link

# 프로덕션 배포
vercel --prod
```

### 2단계: 도메인 연결 확인

**옵션 A: 새 서브도메인 사용 (추천)**
- Vercel 대시보드 → Project Settings → Domains
- `ir.eieconcierge.com` 또는 `dashboard.eieconcierge.com` 추가

**옵션 B: 기존 경로 유지 (리라이트 사용)**
- 기존 `eieconcierge.com` 프로젝트의 `vercel.json` 수정:

```json
{
  "rewrites": [
    {
      "source": "/cointicker/:path*",
      "destination": "https://[새-프로젝트-URL].vercel.app/IR/:path*"
    }
  ]
}
```

### 3단계: 배포 확인

1. 새 배포 URL 접속 테스트
2. 모든 페이지 동작 확인:
   - `/IR/index.html`
   - `/IR/dashboard.html`
   - `/IR/demo.html`
   - `/IR/live-dashboard.html`
   - `/IR/architecture.html`
   - `/IR/performance.html`
   - `/IR/data-pipeline.html`

### 4단계: 기존 도메인 리다이렉트 설정 (선택)

기존 링크 유지가 필요한 경우:

```json
{
  "redirects": [
    {
      "source": "/cointicker/:path*",
      "destination": "/IR/:path*",
      "permanent": true
    }
  ]
}
```

---

## 🗑️ voice-summarizer에서 삭제하기

### ✅ 삭제 가능한 시점

다음 조건이 모두 충족된 후에만 삭제:

- [ ] PICU/IR-dashboard가 새 Vercel 프로젝트로 배포됨
- [ ] 새 URL에서 모든 페이지 정상 동작 확인
- [ ] 기존 도메인 리다이렉트 설정 완료 (또는 새 도메인으로 전환 완료)
- [ ] 기존 링크 업데이트 완료 (필요한 경우)

### 삭제할 파일/폴더

```bash
cd /Users/juns/code/personal/notion/juns_workspace/voice-summarizer

# build/cointicker 폴더 삭제
rm -rf build/cointicker

# public/cointicker 폴더 삭제
rm -rf public/cointicker

# vercel.json에서 /cointicker 경로 제거
# (vercel.json 수정 필요)
```

### vercel.json 수정

`voice-summarizer/vercel.json`에서 다음 라인 제거:

```json
{
  "src": "/cointicker",
  "dest": "/cointicker/index.html"
},
{
  "src": "/cointicker/(.*)",
  "dest": "/cointicker/$1"
}
```

---

## 📋 최종 확인 사항

- [ ] 새 배포 URL 정상 작동
- [ ] 기존 도메인 경로 정상 작동 (리다이렉트 또는 새 배포)
- [ ] 모든 HTML 파일의 내부 링크 정상 작동
- [ ] 정적 파일 (CSS, JS) 정상 로드
- [ ] voice-summarizer에서 파일 삭제 후 배포 테스트

---

## 💡 권장 워크플로우

1. **지금**: PICU/IR-dashboard 배포 및 테스트
2. **도메인 연결**: 새 도메인 또는 리다이렉트 설정
3. **테스트 기간**: 1-2주간 두 프로젝트 병행 운영
4. **최종 전환**: 모든 링크 업데이트 후 voice-summarizer에서 삭제

---

**⚠️ 결론: voice-summarizer에서 삭제하기 전에 반드시 새 배포를 완료하고 테스트해야 합니다!**

