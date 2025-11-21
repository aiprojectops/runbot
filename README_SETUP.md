# 🚀 챗봇 셋업 가이드

이 가이드는 새로운 회사를 위한 맞춤형 챗봇을 설정하는 방법을 설명합니다.

---

## 📋 전체 프로세스

```
1. 템플릿 준비 (최초 1회)
   ↓
2. 회사별 셋업 (회사마다 반복)
   ├─ setup.py 실행
   ├─ 데이터 파일 추가
   ├─ 파일 처리
   └─ 파이프라인 실행
   ↓
3. 배포 (Render)
   ↓
4. 클라이언트 전달 (embed 코드)
```

---

## 🎬 시작하기

### 사전 준비

1. **계정 생성** (무료)
   - [OpenAI](https://platform.openai.com) - API 키 발급
   - [Supabase](https://supabase.com) - 벡터 DB
   - [Render](https://render.com) - 호스팅 (선택)

2. **Supabase 설정**
   ```sql
   -- Supabase SQL Editor에서 실행
   -- supabase_setup.sql 파일 내용 전체 실행
   ```

---

## 📦 회사별 챗봇 생성 (예: ABC Corp)

### 1️⃣ 템플릿 복제

```bash
# GitHub에서 복제 (또는 폴더 복사)
git clone https://github.com/your-repo/chatbot-template.git abc-corp-chatbot
cd abc-corp-chatbot

# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 패키지 설치
pip install -r requirements.txt
```

### 2️⃣ 자동 셋업 실행

```bash
python setup/setup.py
```

**대화형 프롬프트 예시:**
```
🤖 챗봇 셋업 마법사
============================================================

📋 1단계: 회사 정보
------------------------------------------------------------
회사 이름 (예: ABC Corp): ABC Corporation
✅ Company ID: abc_corporation

🤖 2단계: OpenAI API 키
------------------------------------------------------------
OpenAI API Key: sk-proj-abc123...

☁️ 3단계: Supabase 설정
------------------------------------------------------------
Supabase URL: https://abcxyz.supabase.co
Supabase Service Role Key: eyJhbG...

🗄️ 4단계: MySQL 설정 (선택사항)
------------------------------------------------------------
MySQL 사용? (y/n) [n]: y
MySQL Host: abc.mysql.com
MySQL Port [3306]: 3306
MySQL User: abc_user
MySQL Password: ***
MySQL Database: abc_db

✅ 셋업 완료!
```

**생성되는 파일:**
- `.env` - 환경변수 (절대 Git에 커밋 금지!)
- `data/` - 데이터 폴더 (여기에 파일 추가)

### 3️⃣ 데이터 파일 추가

```bash
# data/ 폴더에 회사 데이터 복사
data/
├── products.json       # 제품 정보
├── manual.pdf          # 사용 설명서
├── receipt.jpg         # 영수증 샘플
└── faq.docx           # FAQ 문서
```

**지원 파일 형식:**
- ✅ JSON (phpMyAdmin 내보내기 형식 지원)
- ✅ PDF (텍스트 추출)
- ✅ 이미지 (OCR - 한글/영어)
- ✅ Word (.docx)
- ✅ Excel (.xlsx)

### 4️⃣ 파일 처리

```bash
# 다양한 파일 → JSON 변환
python setup/file_processor.py

# 출력 예시:
# 📁 파일 처리 시작
# 발견된 파일: 4개
#   📄 JSON: products.json
#   📕 PDF: manual.pdf
#     ✅ 15개 페이지 추출됨
#   🖼️ 이미지: receipt.jpg
#   📘 Word: faq.docx
# ✅ 처리 완료! 총 42개 문서
# 📄 저장 위치: data/processed_data.json
```

### 5️⃣ 데이터 파이프라인 실행

```bash
# 1단계: 데이터 추출
python 1_mysql_data_loader.py

# 출력:
# [완료] 총 42개 Document 추출 완료
# [저장] extracted_data.json

# 2단계: 임베딩 생성 & Supabase 저장
python 2_embedding_generator.py

# 출력:
# [완료] 42개 Document 로드
# [진행] 임베딩 생성 중...
# [완료] Supabase에 42개 저장 완료
```

### 6️⃣ 로컬 테스트

```bash
python 4_chatbot_web.py

# 브라우저에서:
# http://localhost:8080

# 테스트 질문:
# "제품 목록 알려줘"
# "사용 설명서 요약해줘"
```

---

## 🌐 Render 배포

### 1️⃣ GitHub에 푸시

```bash
# .env 파일은 gitignore되어 있음 (자동 제외)
git init
git add .
git commit -m "ABC Corp 챗봇 초기 설정"
git remote add origin https://github.com/your-account/abc-corp-chatbot.git
git push -u origin main
```

### 2️⃣ Render 설정

1. [Render 대시보드](https://dashboard.render.com) 접속
2. **"New +"** → **"Web Service"**
3. GitHub 저장소 연결: `abc-corp-chatbot`
4. 설정:
   ```
   Name: abc-corp-chatbot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python 4_chatbot_web.py
   ```
5. **환경변수 추가** (중요!)
   - `.env` 파일 내용을 하나씩 복사
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `USE_MYSQL_CONNECTION`
   - ... (나머지 변수들)

6. **"Create Web Service"** 클릭

### 3️⃣ 배포 완료

```
✅ 배포 완료!
URL: https://abc-corp-chatbot.onrender.com

테스트:
https://abc-corp-chatbot.onrender.com
```

---

## 📤 클라이언트에게 전달

### embed 코드

```html
<!-- ABC Corp 홈페이지에 추가 -->
<script src="https://abc-corp-chatbot.onrender.com/static/js/chatbot-widget.js"></script>
```

### 위치
- **WordPress**: 테마 편집기 → footer.php → `</body>` 앞
- **Cafe24**: 디자인 관리 → HTML 편집 → 하단 HTML → `</body>` 앞
- **일반 HTML**: `</body>` 태그 직전에 삽입

---

## 🔄 데이터 업데이트

회사에서 데이터를 업데이트하고 싶을 때:

```bash
# 1. 새 파일을 data/에 추가
cp new_products.json data/

# 2. 파일 처리
python setup/file_processor.py

# 3. 파이프라인 재실행
python 1_mysql_data_loader.py
python 2_embedding_generator.py

# 4. 서버 재시작 (Render는 자동)
# 로컬: Ctrl+C 후 python 4_chatbot_web.py
```

---

## 📊 비용 예상 (회사당)

| 항목 | 비용/월 |
|------|---------|
| Render (Free Tier) | $0 |
| Render (Starter) | $7 |
| Supabase (Free) | $0 |
| OpenAI API | $5~$20 |
| **총 예상** | **$5~$30** |

**무료 티어로 시작 가능!**

---

## 🛠️ 문제 해결

### PDF 처리 오류
```bash
pip install PyPDF2
```

### 이미지 OCR 오류
```bash
# 1. Python 패키지
pip install Pillow pytesseract

# 2. Tesseract OCR 설치
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract tesseract-lang
# 한글 지원: 언어 데이터 다운로드
```

### Render 배포 실패
- 환경변수 확인 (`.env` 내용 그대로 입력)
- `Start Command` 확인: `python 4_chatbot_web.py`
- 포트 설정: Render는 자동으로 `$PORT` 환경변수 제공

---

## 📚 다음 단계

1. **커스터마이징**
   - `static/css/chatbot-widget.css` - 위젯 스타일
   - `templates/index.html` - 메인 페이지

2. **고급 기능**
   - 대화 이력 저장
   - 사용자 피드백 수집
   - 분석 대시보드

3. **다른 회사 추가**
   - 1단계부터 반복
   - 각 회사는 독립된 인스턴스

---

## 🤝 지원

문제가 발생하면 GitHub 이슈로 등록해주세요.

**Happy Chatbotting! 🎉**

