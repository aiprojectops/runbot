# 🚀 Render 배포 가이드

이 문서는 챗봇을 Render에 배포하는 방법을 설명합니다.

---

## 📋 사전 준비

1. ✅ GitHub 계정
2. ✅ Render 계정 (무료) - https://render.com
3. ✅ 환경변수 준비
   - OpenAI API 키
   - Supabase URL & Service Role 키
   - MySQL 정보 (선택사항)

---

## 🎬 배포 단계

### 1단계: GitHub에 푸시

```bash
# 1. Git 초기화 (아직 안 했다면)
git init

# 2. 모든 파일 추가
git add .

# 3. 커밋
git commit -m "Initial commit: 챗봇 프로젝트"

# 4. GitHub 저장소 생성 후 연결
git remote add origin https://github.com/your-username/your-repo-name.git

# 5. 푸시
git push -u origin main
```

⚠️ **주의:** `.env` 파일은 `.gitignore`에 의해 자동으로 제외됩니다!

---

### 2단계: Render 배포

#### A. Render 대시보드 접속
https://dashboard.render.com

#### B. 새 Web Service 생성
1. **"New +"** 클릭
2. **"Web Service"** 선택
3. **GitHub 저장소 연결**
   - "Connect account" → GitHub 인증
   - 저장소 선택

#### C. 설정 입력
```
Name: your-chatbot-name
Environment: Python 3
Region: Singapore (또는 가까운 지역)
Branch: main
Root Directory: (비워두기)

Build Command: pip install -r requirements.txt
Start Command: python 4_chatbot_web.py

Instance Type: Free (또는 Starter $7/월)
```

#### D. 환경변수 추가 ⭐ 중요!

**"Environment"** 섹션에서 다음 변수들을 **하나씩** 추가:

```
OPENAI_API_KEY=sk-proj-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
USE_MYSQL_CONNECTION=True
CAFE24_DB_HOST=your-host.mycafe24.com
CAFE24_DB_PORT=3306
CAFE24_DB_USER=your-username
CAFE24_DB_PASSWORD=your-password
CAFE24_DB_DATABASE=your-database
CAFE24_DB_CHARSET=utf8mb4
```

💡 **팁:** `.env` 파일 내용을 그대로 복사해서 입력하세요!

#### E. 배포 시작
1. **"Create Web Service"** 클릭
2. 배포 진행 (5~10분 소요)
3. 로그 확인

---

### 3단계: 배포 확인

#### A. URL 확인
```
https://your-chatbot-name.onrender.com
```

브라우저에서 접속하여 챗봇이 정상 작동하는지 확인

#### B. 로그 확인
Render 대시보드 → Logs 탭
```
[완료] 서버를 시작합니다: http://0.0.0.0:10000
* Running on all addresses (0.0.0.0)
```

#### C. 테스트
```
https://your-chatbot-name.onrender.com/api/health
```
→ `{"status": "ok"}` 응답 확인

---

### 4단계: 클라이언트 전달

#### embed 코드 생성
```html
<!-- 클라이언트 웹사이트에 추가 -->
<script src="https://your-chatbot-name.onrender.com/static/js/chatbot-widget.js"></script>
```

위치: `</body>` 태그 직전

---

## 🔄 업데이트 방법

### 코드 수정 후 재배포

```bash
# 1. 수정사항 커밋
git add .
git commit -m "Update: 기능 개선"

# 2. 푸시
git push

# 3. Render가 자동으로 재배포 (Auto Deploy)
```

Render는 **GitHub 푸시를 감지하여 자동으로 재배포**합니다!

---

## 📊 무료 티어 제한

### Render Free Tier
- ✅ 무료
- ⚠️ 15분 미사용 시 sleep (첫 요청 시 재시작)
- ⚠️ 월 750시간 제한
- ⚠️ 느린 속도

### Render Starter ($7/월)
- ✅ Sleep 없음
- ✅ 빠른 속도
- ✅ 무제한 시간

**추천:** 테스트는 Free, 실서비스는 Starter

---

## 🛠️ 문제 해결

### 1. 배포 실패
**증상:** Build failed

**해결:**
- `requirements.txt` 확인
- Python 버전 확인 (3.13 사용)
- Render 로그 확인

### 2. 서버 시작 실패
**증상:** Start command failed

**해결:**
```bash
# Start Command 확인
python 4_chatbot_web.py

# 포트 자동 감지 (이미 구현됨)
port = int(os.getenv('PORT', 8080))
```

### 3. 환경변수 오류
**증상:** 챗봇이 작동하지 않음

**해결:**
- Render 대시보드 → Environment 탭
- 모든 환경변수 확인 (특히 Service Role Key!)
- 저장 후 재배포

### 4. Supabase 연결 실패
**증상:** 401 Unauthorized

**해결:**
- `SUPABASE_SERVICE_ROLE_KEY` 확인 (anon 키 아님!)
- Supabase 대시보드 → Settings → API
- Service Role Key 다시 복사

### 5. MySQL 연결 실패
**증상:** Can't connect to MySQL

**해결:**
- Render IP를 Cafe24 MySQL 외부 접속 IP에 추가
- 호스트 주소 확인 (예: `xxx.mycafe24.com`)

---

## 💡 프로덕션 체크리스트

배포 전 확인사항:

- [ ] `.env` 파일이 Git에 포함되지 않았는지 확인
- [ ] 환경변수 모두 Render에 입력
- [ ] Supabase에 데이터 임베딩 완료
- [ ] 로컬에서 테스트 완료
- [ ] API 키 유효성 확인
- [ ] MySQL 외부 접속 IP 등록

---

## 📚 추가 문서

- [README.md](./README.md) - 프로젝트 전체 설명
- [README_SETUP.md](./README_SETUP.md) - 초기 설정 가이드
- [HYBRID_RAG_GUIDE.md](./HYBRID_RAG_GUIDE.md) - 하이브리드 RAG 가이드

---

**배포 성공을 기원합니다! 🎉**

