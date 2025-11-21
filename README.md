# 🤖 cafe24 MySQL RAG 챗봇

cafe24 MySQL 데이터베이스 기반 하이브리드 RAG(Retrieval-Augmented Generation) 챗봇 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 cafe24 MySQL 데이터베이스의 데이터를 활용하여 AI 챗봇을 구축합니다. **하이브리드 RAG 패턴**을 사용하여 정확하고 실시간으로 업데이트되는 답변을 제공합니다.

### 🌟 주요 기능

✅ **JSON/MySQL 데이터 추출**: JSON 파일 또는 MySQL DB에서 데이터 추출  
✅ **OpenAI 임베딩**: text-embedding-3-small 모델 사용  
✅ **하이브리드 검색**: 벡터 검색 + BM25 키워드 검색 결합  
✅ **실시간 MySQL 쿼리**: 새 데이터 즉시 반영 (재임베딩 불필요!)  
✅ **GPT-4o-mini 답변**: OpenAI GPT 모델 기반 자연스러운 답변  
✅ **두 가지 UI**: Streamlit 테스트용 / Flask 웹 위젯 (임베딩 가능)  
✅ **환경변수 관리**: .env 파일로 안전한 API 키 관리  

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────┐
│            하이브리드 RAG 시스템                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  사용자 질문                                     │
│       ↓                                          │
│  ┌─────────────┐                                │
│  │ 의도 분석    │ "포도 얼마?"                   │
│  └─────┬───────┘                                │
│        ├───────────┬──────────────┐             │
│        ↓           ↓              ↓             │
│   [RAG 검색]  [실시간 DB]   [하이브리드]        │
│        │           │              │             │
│  ┌─────▼──────┐ ┌─▼─────────┐ ┌─▼──────┐      │
│  │ Supabase   │ │   MySQL   │ │  통합   │      │
│  │ Vector DB  │ │ 직접쿼리  │ │  결과   │      │
│  └────────────┘ └───────────┘ └────────┘      │
│        │           │              │             │
│        └───────────┴──────────────┘             │
│                    ↓                             │
│            ┌───────────────┐                    │
│            │  GPT-4o-mini  │                    │
│            │   답변 생성    │                    │
│            └───────────────┘                    │
└─────────────────────────────────────────────────┘

데이터 준비 파이프라인:
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  JSON 파일    │───▶│  임베딩 생성  │───▶│  Supabase    │
│ (products등)  │    │  (OpenAI)    │    │  저장 완료    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 🚀 빠른 시작

### 1단계: 필요한 계정 준비

- ☁️ **Supabase**: 벡터 데이터베이스 ([무료 가입](https://supabase.com))
- 🤖 **OpenAI**: 임베딩 + GPT API ([API 키 발급](https://platform.openai.com/api-keys))
- 🗄️ **cafe24**: MySQL 데이터베이스 (선택사항 - JSON 파일도 가능)

### 2단계: Python 패키지 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3단계: Supabase 설정

1. [Supabase](https://app.supabase.com) 접속 및 **새 프로젝트 생성**
2. **SQL Editor**에서 `supabase_setup.sql` 파일 내용 **전체 실행**
3. **Settings > API**에서 다음 정보 복사:
   - Project URL
   - **service_role key** (⚠️ anon key 아님!)

### 4단계: 환경변수 설정

```bash
# 1. .env 파일 생성 (env.example을 복사)
# Windows (PowerShell)
Copy-Item env.example .env

# Mac/Linux
cp env.example .env

# 2. .env 파일을 열고 실제 값 입력
```

**`.env` 파일 예시:**
```env
# OpenAI API 키
OPENAI_API_KEY=sk-proj-실제_키를_여기에

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=실제_service_role_키를_여기에

# Cafe24 MySQL (선택사항)
CAFE24_DB_HOST=your-host.mycafe24.com
CAFE24_DB_USER=your_username
CAFE24_DB_PASSWORD=your_password
CAFE24_DB_DATABASE=your_database
USE_MYSQL_CONNECTION=False  # JSON 파일 사용 시 False
```

### 5단계: 데이터 파이프라인 실행

```bash
# 1단계: JSON 파일에서 데이터 추출
python 1_mysql_data_loader.py
# → extracted_data.json 생성됨

# 2단계: 임베딩 생성 및 Supabase 저장
python 2_embedding_generator.py
# → Supabase에 벡터 임베딩 저장 완료

# 3단계: 챗봇 실행 (두 가지 옵션)
```

#### 옵션 A: Streamlit 챗봇 (테스트용)
```bash
streamlit run 3_chatbot_app.py
# → http://localhost:8501 에서 확인
```
- ✅ 빠른 테스트에 적합
- ❌ 실시간 MySQL 쿼리 불가
- ❌ 다른 사이트에 임베딩 불가

#### 옵션 B: Flask 웹 챗봇 (실서비스용, **권장**)
```bash
python 4_chatbot_web.py
# → http://localhost:8080 에서 확인
```
- ✅ 실시간 MySQL 쿼리 지원
- ✅ 새 데이터 즉시 반영
- ✅ 다른 사이트에 `<script>` 태그로 임베딩 가능
- ✅ 사이드 톡 위젯 UI

## 📁 프로젝트 구조

```
runbot/
│
├── 📝 설정 파일
│   ├── .env                          # 환경변수 (API 키 등) ⚠️ Git 제외
│   ├── env.example                   # 환경변수 템플릿
│   ├── config.py                     # 설정 로더 (.env에서 읽기)
│   └── config.example.py             # 설정 예제 (참고용)
│
├── 🔄 데이터 파이프라인
│   ├── 1_mysql_data_loader.py        # JSON/MySQL 데이터 추출
│   ├── 2_embedding_generator.py      # 임베딩 생성 & Supabase 저장
│   └── extracted_data.json           # 추출된 데이터 (자동 생성)
│
├── 🤖 챗봇 애플리케이션
│   ├── 3_chatbot_app.py              # Streamlit 챗봇 (테스트용)
│   ├── 4_chatbot_web.py              # Flask 웹 챗봇 (실서비스용)
│   └── database_helper.py            # 실시간 MySQL 쿼리 헬퍼
│
├── 🌐 웹 리소스
│   ├── templates/
│   │   └── index.html                # 메인 페이지
│   └── static/
│       ├── css/
│       │   ├── chatbot.css           # Streamlit 챗봇 스타일
│       │   └── chatbot-widget.css    # 위젯 스타일
│       └── js/
│           ├── chatbot.js            # Streamlit 챗봇 로직
│           └── chatbot-widget.js     # 임베딩 위젯 (자동 실행)
│
├── 📊 데이터
│   ├── data/
│   │   ├── children.json             # 아이 정보 (예시)
│   │   ├── activity_photos.json      # 활동 사진 (예시)
│   │   └── products.json             # 제품 정보 (예시)
│
├── 📚 문서
│   ├── README.md                     # 프로젝트 설명서 (이 파일)
│   ├── HYBRID_RAG_GUIDE.md           # 하이브리드 RAG 상세 가이드
│   ├── EMBED_GUIDE.md                # 위젯 임베딩 가이드
│   └── MYSQL_CONNECTION_GUIDE.md     # MySQL 연결 가이드
│
├── 🛠️ 유틸리티
│   ├── test_mysql_connection.py      # MySQL 연결 테스트
│   ├── example_embed.html            # 위젯 임베딩 예시
│   └── supabase_setup.sql            # Supabase 초기 설정 SQL
│
├── ⚙️ 기타
│   ├── requirements.txt              # Python 패키지 목록
│   ├── .gitignore                    # Git 제외 파일 목록
│   └── chatbot.log                   # 챗봇 로그 (자동 생성)
```

## ⚙️ 상세 설정

### 데이터 추출 설정 (`config.py`)

현재 프로젝트는 **3개 테이블**을 사용합니다:

```python
DATA_EXTRACTION_CONFIG = {
    # 1. 아이 정보
    "children": {
        "json_file": "data/children.json",
        "table": "children",
        "text_columns": ["name", "class_name", "notes"],
        "metadata_columns": ["id", "birth_date", "gender", "created_at"]
    },
    
    # 2. 활동 사진
    "activity_photos": {
        "json_file": "data/activity_photos.json",
        "table": "activity_photos",
        "text_columns": ["title", "description"],
        "metadata_columns": ["id", "child_id", "photo_path", "upload_date"]
    },
    
    # 3. 제품 정보 (새로 추가됨!)
    "products": {
        "json_file": "data/products.json",
        "table": "products",
        "text_columns": ["name", "description", "status"],
        "metadata_columns": ["id", "price", "discount_price", "stock_quantity"]
    }
}
```

### 새 데이터 소스 추가하기

1. **JSON 파일 준비**: `data/` 폴더에 JSON 파일 저장
2. **config.py 수정**: `DATA_EXTRACTION_CONFIG`에 설정 추가
3. **파이프라인 재실행**:
   ```bash
   python 1_mysql_data_loader.py
   python 2_embedding_generator.py
   ```

### 챗봇 모델 설정

```python
CHATBOT_CONFIG = {
    "llm_model": "gpt-4o-mini",           # OpenAI 모델
    "temperature": 0.2,                    # 창의성 (0~1)
    "max_tokens": 1500,                    # 최대 응답 길이
    "search_results_count": 5,             # 검색 결과 개수
    "bm25_weight": 0.3,                    # BM25 가중치
    "vector_weight": 0.7                   # 벡터 검색 가중치
}
```

## 🚀 하이브리드 RAG + 실시간 MySQL 쿼리

**핵심 기능!** RAG 벡터 검색과 실시간 MySQL 쿼리를 지능적으로 결합한 시스템입니다.

### 🎯 특징

✅ **실시간성**: MySQL에 새 데이터 추가 → 재임베딩 없이 즉시 검색 가능!  
✅ **정확성**: 특정 정보는 DB에서 직접 조회 (AI 환각 최소화)  
✅ **효율성**: 일반 질문은 RAG, 구체적 정보는 MySQL 직접 쿼리  
✅ **자동 판단**: 질문 의도를 AI가 자동 분석하여 최적 검색 방법 선택  

### 작동 방식

```
사용자 질문: "포도는 얼마인가요?"
      ↓
┌─────────────────┐
│ 의도 분석 (AI)   │ → "제품 가격 질문"
└────────┬────────┘
         │
    ┌────▼─────┬─────────────┐
    │          │             │
 [RAG 검색] [MySQL 쿼리] [통합]
    │          │             │
Supabase   products      결합
Vector DB  테이블         결과
    │          │             │
    └──────────┴─────────────┘
               ↓
       ┌──────────────┐
       │ GPT-4o-mini  │
       │  답변 생성    │
       └──────────────┘
```

### 실제 예시

#### 예시 1: 제품 정보 질문
**질문:** "포도는 얼마인가요?"

**처리 과정:**
1. 의도 분석 → `product_info` (제품 정보 질문)
2. MySQL 실시간 쿼리:
   ```sql
   SELECT * FROM products WHERE name LIKE '%포도%'
   ```
3. 결과: "출하예정(2025-12-07)_포도, 15,000원, 재고 20개"

**장점:** 방금 추가한 제품도 즉시 검색! ✅

#### 예시 2: 아이 정보 질문
**질문:** "박지훈은 어느 반인가요?"

**처리 과정:**
1. 의도 분석 → `child_info` (아이 정보 질문)
2. MySQL 실시간 쿼리:
   ```sql
   SELECT * FROM children WHERE name LIKE '%박지훈%'
   ```
3. 결과: "박지훈, 기쁨반, 남자, 2019-03-15"

**장점:** 신규 등록 아이도 즉시 검색! ✅

#### 예시 3: 일반 질문
**질문:** "농장 소개해주세요"

**처리 과정:**
1. 의도 분석 → `general` (일반 질문)
2. RAG 벡터 검색 (Supabase)
3. 관련 문서 검색 후 GPT 답변

**장점:** 복잡한 맥락도 이해! ✅

### 지원되는 질문 유형

| 질문 유형 | 예시 | 검색 방법 |
|----------|------|----------|
| 제품 정보 | "고추 가격", "딸기 얼마" | MySQL (products) |
| 아이 정보 | "김민수 어느 반", "이지은 생일" | MySQL (children) |
| 활동 정보 | "최근 활동 사진", "새로운 업로드" | MySQL (activity_photos) |
| 전체 목록 | "전체 아이 명단", "상품 목록" | MySQL (전체 조회) |
| 일반 질문 | "농장 소개", "운영 시간" | RAG (Supabase) |

### 상세 가이드

자세한 내용은 **[HYBRID_RAG_GUIDE.md](./HYBRID_RAG_GUIDE.md)** 파일을 참고하세요.

---

## 🌐 다른 웹사이트에 챗봇 추가하기

단 **한 줄의 코드**로 어떤 웹사이트에든 챗봇을 추가할 수 있습니다!

### 사용 방법

1. 챗봇 서버 실행:
   ```bash
   python 4_chatbot_web.py
   ```

2. HTML 파일의 `</body>` 닫는 태그 직전에 추가:
   ```html
   <script src="http://localhost:8080/static/js/chatbot-widget.js"></script>
   ```

3. 완료! 오른쪽 하단에 채팅 버튼이 나타납니다.

### 상세 가이드

자세한 내용은 **[EMBED_GUIDE.md](./EMBED_GUIDE.md)** 파일을 참고하세요:
- WordPress, Cafe24, Wix 등 플랫폼별 추가 방법
- 실제 서버 배포 시 설정 변경
- 버튼 위치, 색상 커스터마이징
- 문제 해결 방법

### 예시 파일

- `example_embed.html`: 챗봇 임베드 예시 HTML

## 🔍 RAG 작동 원리 상세

### 1️⃣ 데이터 준비 단계 (1회만 실행)

```
JSON 파일
    ↓
1_mysql_data_loader.py
    ├─ JSON 파일 읽기
    ├─ Document 객체 변환
    └─ extracted_data.json 저장
    ↓
2_embedding_generator.py
    ├─ 텍스트 청크 분할 (1000자 단위)
    ├─ OpenAI 임베딩 생성 (1536차원 벡터)
    └─ Supabase Vector DB 저장
    ↓
✅ 준비 완료!
```

### 2️⃣ 질의응답 단계 (실시간)

```
사용자 질문: "포도는 얼마인가요?"
    ↓
4_chatbot_web.py
    ├─ 1. 의도 분석 (check_query_intent)
    │   └─ "제품 정보" 질문으로 판단
    │
    ├─ 2. 데이터 검색 (2가지 동시 실행)
    │   ├─ [벡터 검색] Supabase에서 유사 문서 5개
    │   └─ [MySQL 쿼리] products 테이블 직접 검색
    │
    ├─ 3. 결과 통합
    │   └─ 벡터 검색 결과 + DB 검색 결과 결합
    │
    └─ 4. GPT 답변 생성
        └─ GPT-4o-mini에게 통합 결과 전달 → 답변
    ↓
✅ 답변 완료!
```

### 3️⃣ 하이브리드 검색 알고리즘

```python
# 1. 벡터 검색 (의미 기반)
vector_docs = supabase.similarity_search("포도 가격")
# → "포도", "과일", "가격" 등 유사한 의미의 문서

# 2. BM25 검색 (키워드 기반)
bm25_docs = bm25_retriever.search("포도 가격")
# → "포도"라는 단어가 정확히 들어간 문서

# 3. 점수 결합
final_score = (vector_score × 0.7) + (bm25_score × 0.3)
```

## 📊 성능 최적화 팁

### 1. 임베딩 최적화

✅ **text-embedding-3-small 사용** (비용 1/4, 속도 2배)  
✅ **배치 처리** (100개씩 묶어서 처리)  
✅ **청크 크기 조절** (1000자, 중복 200자)

### 2. 검색 최적화

✅ **하이브리드 검색** (벡터 70% + BM25 30%)  
✅ **Supabase 벡터 인덱스** (HNSW 알고리즘)  
✅ **검색 결과 개수 제한** (기본 5개)

### 3. 응답 최적화

✅ **gpt-4o-mini 사용** (gpt-4보다 15배 저렴)  
✅ **온도 0.2** (일관된 답변)  
✅ **최대 토큰 1500** (적절한 답변 길이)

### 4. 서버 최적화

✅ **리소스 캐싱** (검색기, LLM 재사용)  
✅ **연결 풀링** (MySQL 연결 재사용)  
✅ **로그 레벨 조정** (INFO 권장)

### 성능 벤치마크

| 항목 | 시간 | 비용 |
|------|------|------|
| 데이터 추출 (17개) | ~1초 | 무료 |
| 임베딩 생성 (17개) | ~3초 | $0.0001 |
| 벡터 검색 | ~0.5초 | 무료 |
| MySQL 쿼리 | ~0.1초 | 무료 |
| GPT 답변 생성 | ~2초 | $0.001 |
| **총 응답 시간** | **~3초** | **$0.001** |

## 🛠️ 트러블슈팅

### 1. `.env` 파일 관련 오류

#### 증상: `ValueError: 필수 환경변수가 설정되지 않았습니다`

**원인:** `.env` 파일이 없거나 필수 값이 누락됨

**해결:**
```bash
# 1. .env 파일 존재 확인
# 2. env.example과 비교하여 누락된 값 확인
# 3. 특히 다음 값 확인:
#    - OPENAI_API_KEY
#    - SUPABASE_URL
#    - SUPABASE_SERVICE_ROLE_KEY
```

### 2. OpenAI API 키 오류

#### 증상: `Error code: 401 - Incorrect API key`

**원인:** 
- API 키가 잘못되었거나 만료됨
- 크레딧이 소진됨

**해결:**
1. https://platform.openai.com/api-keys 에서 새 키 생성
2. `.env` 파일의 `OPENAI_API_KEY` 업데이트
3. 서버 재시작

### 3. Supabase 연결 오류

#### 증상: `HTTP/2 401 Unauthorized`

**원인:** 
- `anon` 키를 사용함 (잘못됨!)
- `service_role` 키가 필요

**해결:**
1. Supabase 대시보드 → Settings → API
2. **service_role key** 복사 (anon key 아님!)
3. `.env` 파일의 `SUPABASE_SERVICE_ROLE_KEY` 업데이트
4. 서버 재시작

#### 증상: `Supabase에 저장된 데이터가 없습니다`

**원인:** 1, 2단계를 실행하지 않음

**해결:**
```bash
# 순서대로 실행 필수!
python 1_mysql_data_loader.py    # 먼저
python 2_embedding_generator.py  # 그 다음
python 4_chatbot_web.py          # 마지막
```

### 4. MySQL 연결 오류

#### 증상: `Can't connect to MySQL server`

**원인:** 
- 호스트 주소가 잘못됨
- 외부 IP 접근 허용 안 됨

**해결:**
1. **Cafe24 호스팅센터**에서 정확한 MySQL 호스트 확인
2. **MySQL 외부 접속 IP** 등록 확인
3. 자세한 내용: [MYSQL_CONNECTION_GUIDE.md](./MYSQL_CONNECTION_GUIDE.md)

### 5. Unicode 오류 (Windows)

#### 증상: `UnicodeEncodeError: 'cp949'`

**원인:** Windows 콘솔이 한글을 제대로 표시 못 함

**해결:**
```bash
# PowerShell에서 실행
$env:PYTHONIOENCODING="utf-8"
python 4_chatbot_web.py

# 또는 환경변수 설정 (영구적)
# 시스템 환경변수에 PYTHONIOENCODING=utf-8 추가
```

### 6. 새 데이터가 검색 안 됨

#### 증상: MySQL에 추가한 데이터가 챗봇에서 안 나옴

**원인:** `3_chatbot_app.py` (Streamlit) 사용 중

**해결:**
- ❌ **3번 파일**: RAG만 지원 (재임베딩 필요)
- ✅ **4번 파일**: 실시간 MySQL 쿼리 지원

```bash
# 4번 파일로 변경
python 4_chatbot_web.py
```

### 7. 의존성 충돌 오류

#### 증상: `pip install` 시 httpx 버전 충돌

**해결:**
```bash
# 가상환경 새로 생성
python -m venv venv_new
venv_new\Scripts\activate
pip install -r requirements.txt
```

## 📝 실제 사용 사례

### 사례 1: 농장 쇼핑몰 챗봇

**데이터 구성:**
- `products`: 농산물 정보 (고추, 딸기, 포도 등)
- `children`: 농장 체험 학생 정보
- `activity_photos`: 활동 사진

**주요 질문:**
- "포도는 얼마인가요?" → 실시간 제품 검색
- "박지훈은 어느 반인가요?" → 실시간 학생 검색
- "농장 소개해주세요" → RAG 벡터 검색

### 사례 2: 교육 기관 챗봇

**데이터 구성:**
```python
DATA_EXTRACTION_CONFIG = {
    "students": {
        "json_file": "data/students.json",
        "text_columns": ["name", "class", "notes"],
        ...
    },
    "courses": {
        "json_file": "data/courses.json",
        "text_columns": ["course_name", "description"],
        ...
    }
}
```

### 사례 3: 고객 지원 챗봇

**데이터 구성:**
```python
DATA_EXTRACTION_CONFIG = {
    "faq": {
        "json_file": "data/faq.json",
        "text_columns": ["question", "answer"],
        ...
    },
    "products": {
        "json_file": "data/products.json",
        "text_columns": ["name", "specs"],
        ...
    }
}
```

## 🎯 향후 개선 계획

- [ ] 다국어 지원 (영어, 일본어, 중국어)
- [ ] 이미지 검색 기능 (멀티모달 RAG)
- [ ] 대화 이력 저장 및 세션 관리
- [ ] 사용자 피드백 시스템 (👍/👎 평가)
- [ ] 성능 모니터링 대시보드
- [ ] 음성 인터페이스 지원
- [ ] 자동 재학습 파이프라인
- [ ] 다중 데이터베이스 지원 (PostgreSQL, MongoDB 등)

## 💡 주요 기술 스택

| 카테고리 | 기술 |
|----------|------|
| **AI/ML** | OpenAI GPT-4o-mini, text-embedding-3-small |
| **벡터 DB** | Supabase (pgvector) |
| **검색** | Hybrid (Vector + BM25) |
| **웹 프레임워크** | Flask, Streamlit |
| **데이터베이스** | MySQL (Cafe24) |
| **언어** | Python 3.13+ |
| **주요 라이브러리** | LangChain, OpenAI, Supabase, PyMySQL |

## 📚 참고 문서

- [HYBRID_RAG_GUIDE.md](./HYBRID_RAG_GUIDE.md) - 하이브리드 RAG 시스템 상세 가이드
- [EMBED_GUIDE.md](./EMBED_GUIDE.md) - 챗봇 위젯 임베딩 가이드
- [MYSQL_CONNECTION_GUIDE.md](./MYSQL_CONNECTION_GUIDE.md) - MySQL 연결 설정 가이드

## ⚠️ 중요 보안 사항

- ✅ `.env` 파일은 절대 Git에 커밋하지 마세요
- ✅ `service_role` 키는 서버에서만 사용하세요
- ✅ API 키는 정기적으로 교체하세요
- ✅ 프로덕션 배포 시 HTTPS 사용 필수

## 📄 라이선스

이 프로젝트는 개인 학습 및 프로젝트 용도로 자유롭게 사용할 수 있습니다.

## 🤝 문의 및 기여

프로젝트 관련 문의사항이나 버그 리포트는 이슈로 등록해주세요.

---

## 🚀 배포 (Render)

### 빠른 배포
```bash
# 1. GitHub에 푸시
git push origin main

# 2. Render에서 웹 서비스 생성
# 3. 환경변수 설정 (.env 내용)
# 4. 자동 배포 완료!
```

### 상세 가이드
👉 **[DEPLOY.md](./DEPLOY.md)** 참고

### embed 코드 (배포 후)
```html
<script src="https://your-app.onrender.com/static/js/chatbot-widget.js"></script>
```

---

**🎉 이제 시작하세요!**

```bash
# 로컬 개발
python 4_chatbot_web.py

# 배포
git push → Render 자동 배포
```

**Made with ❤️ using OpenAI, Supabase, and LangChain**

