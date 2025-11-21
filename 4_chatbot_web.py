"""
4단계: 웹사이트 임베드 가능한 사이드 톡 챗봇
작성일: 2025-11-20

주요 기능:
- Flask 웹 서버
- 사이드 톡 형태의 채팅 UI
- RAG 기반 챗봇 API
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain_core.messages import HumanMessage
from supabase import create_client
from database_helper import DatabaseHelper, MySQLDatabaseHelper
import re

# 설정 파일 임포트
try:
    from config import (
        OPENAI_API_KEY,
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
        SUPABASE_TABLES,
        CHATBOT_CONFIG,
        EMBEDDING_CONFIG,
        LOGGING_CONFIG,
        DATA_EXTRACTION_CONFIG
    )
    
    # MySQL 설정 (선택사항)
    try:
        from config import CAFE24_DB_CONFIG, USE_MYSQL_CONNECTION
    except ImportError:
        CAFE24_DB_CONFIG = None
        USE_MYSQL_CONNECTION = False
        
except ImportError:
    print("[오류] config.py 파일이 없습니다!")
    print("[참고] config.example.py를 config.py로 복사하고 실제 값을 입력하세요.")
    exit(1)

# 로깅 설정
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)  # CORS 허용


# ==============================================
# 1. 검색기 클래스
# ==============================================

class SupabaseVectorRetriever:
    """Supabase RPC를 직접 호출하는 벡터 검색기"""
    
    def __init__(self, supabase_client, embeddings, table_name: str, query_name: str):
        self.supabase_client = supabase_client
        self.embeddings = embeddings
        self.table_name = table_name
        self.query_name = query_name
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """유사도 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embeddings.embed_query(query)
            
            # Supabase RPC 함수 호출
            response = self.supabase_client.rpc(
                self.query_name,
                {
                    "query_embedding": query_embedding,
                    "match_count": k,
                    "match_threshold": 0.0
                }
            ).execute()
            
            # Document 객체로 변환
            documents = []
            if response.data:
                for item in response.data:
                    doc = Document(
                        page_content=item.get("content", ""),
                        metadata=item.get("metadata", {})
                    )
                    documents.append(doc)
            
            logger.info(f"[완료] 벡터 검색 완료: {len(documents)}개 결과")
            return documents
            
        except Exception as e:
            logger.error(f"[오류] 벡터 검색 오류: {str(e)}")
            return []


class HybridRetriever:
    """하이브리드 검색기 (벡터 검색 + BM25 키워드 검색)"""
    
    def __init__(self, vector_retriever, bm25_retriever, vector_weight=0.7, bm25_weight=0.3):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
    
    def invoke(self, query: str, k: int = 5) -> List[Document]:
        """하이브리드 검색 수행"""
        try:
            # 벡터 검색
            vector_docs = self.vector_retriever.similarity_search(query, k=k)
            
            # BM25 검색
            bm25_docs = self.bm25_retriever.invoke(query)
            
            # 점수 기반 결합
            doc_scores = {}
            
            # 벡터 검색 결과 점수 부여
            for i, doc in enumerate(vector_docs):
                content_hash = hash(doc.page_content)
                score = (k - i) * self.vector_weight
                doc_scores[content_hash] = {
                    "doc": doc,
                    "score": score
                }
            
            # BM25 검색 결과 점수 부여
            for i, doc in enumerate(bm25_docs):
                content_hash = hash(doc.page_content)
                score = (k - i) * self.bm25_weight
                
                if content_hash in doc_scores:
                    doc_scores[content_hash]["score"] += score
                else:
                    doc_scores[content_hash] = {
                        "doc": doc,
                        "score": score
                    }
            
            # 점수 순으로 정렬
            sorted_docs = sorted(
                doc_scores.values(),
                key=lambda x: x["score"],
                reverse=True
            )
            
            # 상위 k개 반환
            result = [item["doc"] for item in sorted_docs[:k]]
            
            logger.info(f"[완료] 하이브리드 검색 완료: {len(result)}개 결과")
            return result
            
        except Exception as e:
            logger.error(f"[오류] 검색 오류: {str(e)}")
            return []


# ==============================================
# 2. 전역 리소스 초기화
# ==============================================

# 전역 변수로 검색기와 LLM 저장
retriever = None
llm = None
db_helper = None

def initialize_resources():
    """검색기 및 LLM 초기화"""
    global retriever, llm, db_helper
    
    try:
        logger.info("[시작] 리소스 초기화 중...")
        
        # 데이터베이스 헬퍼 초기화
        if USE_MYSQL_CONNECTION and CAFE24_DB_CONFIG:
            try:
                logger.info("[시도] MySQL 직접 연결 시도...")
                db_helper = MySQLDatabaseHelper(CAFE24_DB_CONFIG)
                logger.info("[완료] MySQL 직접 연결 성공!")
            except Exception as mysql_error:
                logger.error(f"[오류] MySQL 연결 실패: {str(mysql_error)}")
                logger.info("[대체] JSON 파일 모드로 전환...")
                db_helper = DatabaseHelper(DATA_EXTRACTION_CONFIG)
        else:
            logger.info("[정보] JSON 파일 모드 사용")
            db_helper = DatabaseHelper(DATA_EXTRACTION_CONFIG)
        
        logger.info("[완료] 데이터베이스 헬퍼 초기화")
        
        # Supabase 클라이언트
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # OpenAI 임베딩
        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_CONFIG["model"],
            openai_api_key=OPENAI_API_KEY
        )
        
        # 벡터 검색기
        vector_retriever = SupabaseVectorRetriever(
            supabase_client=supabase_client,
            embeddings=embeddings,
            table_name=SUPABASE_TABLES["embeddings"],
            query_name=SUPABASE_TABLES["match_function"]
        )
        
        # BM25 검색기 준비
        response = supabase_client.table(SUPABASE_TABLES["embeddings"]).select("content,metadata").execute()
        
        if not response.data:
            logger.error("[오류] Supabase에 저장된 데이터가 없습니다.")
            return False
        
        documents = [
            Document(
                page_content=item["content"],
                metadata=item.get("metadata", {})
            )
            for item in response.data
        ]
        
        # BM25 검색기
        bm25_retriever = BM25Retriever.from_documents(
            documents=documents,
            k=CHATBOT_CONFIG["search_results_count"]
        )
        
        # 하이브리드 검색기
        retriever = HybridRetriever(
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            vector_weight=CHATBOT_CONFIG["vector_weight"],
            bm25_weight=CHATBOT_CONFIG["bm25_weight"]
        )
        
        # GPT 모델
        llm = ChatOpenAI(
            model_name=CHATBOT_CONFIG["llm_model"],
            temperature=CHATBOT_CONFIG["temperature"],
            max_tokens=CHATBOT_CONFIG["max_tokens"],
            api_key=OPENAI_API_KEY
        )
        
        logger.info("[완료] 리소스 초기화 완료")
        return True
        
    except Exception as e:
        logger.error(f"[오류] 리소스 초기화 실패: {str(e)}")
        return False


# ==============================================
# 3. 질문 의도 파악 및 DB 검색
# ==============================================

def extract_person_name(query: str) -> str:
    """질문에서 이름 추출"""
    # "김민수는", "최예은이", "박지훈" 등 패턴 매칭
    name_patterns = [
        r'([가-힣]{2,4})(?:는|은|이|가|의|을|를)',  # 조사가 붙은 이름
        r'([가-힣]{2,4})\s*어[디느]',  # "김민수 어디" 형태
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)
    
    # 단순히 한글 이름만 있는 경우
    words = query.split()
    for word in words:
        if re.match(r'^[가-힣]{2,4}$', word):
            return word
    
    return ""

def check_query_intent(query: str) -> Dict[str, Any]:
    """
    질문 의도 파악
    
    Returns:
        {
            "needs_db": bool,  # DB 검색 필요 여부
            "intent": str,     # "child_info", "recent_activity", "product_info" 등
            "params": dict     # 검색 파라미터
        }
    """
    query_lower = query.lower()
    
    # 이름 추출
    name = extract_person_name(query)
    
    # 제품/상품 관련 질문 (우선순위 높음)
    product_keywords = ['제품', '상품', '농산물', '판매', '가격', '얼마', '재고', '사고 싶', '구매', '주문']
    if any(keyword in query for keyword in product_keywords):
        # 제품명 추출 시도 (간단한 방법)
        for word in query.split():
            if len(word) >= 2 and not any(k in word for k in product_keywords):
                return {
                    "needs_db": True,
                    "intent": "product_info",
                    "params": {"name": word}
                }
    
    # 제품명이 직접 언급된 경우 (고추, 딸기, 포도 등)
    common_products = ['고추', '딸기', '포도', '사과', '바나나', '블루베리', '콩', '당근', '망골드']
    for product in common_products:
        if product in query:
            return {
                "needs_db": True,
                "intent": "product_info",
                "params": {"name": product}
            }
    
    # 특정 아이 정보 질문
    if name and any(keyword in query for keyword in ['반', '어느', '어디', '누구', '언제', '몇']):
        return {
            "needs_db": True,
            "intent": "child_info",
            "params": {"name": name}
        }
    
    # 최신 활동 질문
    if any(keyword in query for keyword in ['최근', '최신', '새로운', '오늘', '어제']):
        if any(keyword in query for keyword in ['활동', '사진', '업로드']):
            return {
                "needs_db": True,
                "intent": "recent_activity",
                "params": {"limit": 5}
            }
    
    # 전체 목록 질문
    if '명단' in query or '목록' in query or '전체' in query:
        return {
            "needs_db": True,
            "intent": "list_all",
            "params": {}
        }
    
    # 기본: RAG만 사용
    return {
        "needs_db": False,
        "intent": "general",
        "params": {}
    }

def search_database(intent: str, params: Dict[str, Any]) -> str:
    """
    데이터베이스에서 실시간 정보 검색
    
    Returns:
        검색 결과 텍스트
    """
    try:
        if intent == "product_info":
            name = params.get("name", "")
            products = db_helper.search_products(name=name)
            
            if not products:
                return f"'{name}' 제품을 찾을 수 없습니다."
            
            if len(products) == 1:
                return f"[실시간 DB 검색 결과]\n{db_helper.format_product_info(products[0])}"
            else:
                result = f"[실시간 DB 검색 결과]\n'{name}'으로 {len(products)}개 제품이 검색되었습니다:\n\n"
                for product in products:
                    result += db_helper.format_product_info(product) + "\n\n"
                return result
        
        elif intent == "child_info":
            name = params.get("name", "")
            children = db_helper.search_children(name=name)
            
            if not children:
                return f"{name}에 대한 정보를 찾을 수 없습니다."
            
            if len(children) == 1:
                return f"[실시간 DB 검색 결과]\n{db_helper.format_child_info(children[0])}"
            else:
                result = f"[실시간 DB 검색 결과]\n'{name}'으로 {len(children)}명이 검색되었습니다:\n\n"
                for child in children:
                    result += db_helper.format_child_info(child) + "\n\n"
                return result
        
        elif intent == "recent_activity":
            limit = params.get("limit", 5)
            photos = db_helper.get_latest_activity_photos(limit=limit)
            
            if not photos:
                return "최근 활동 사진이 없습니다."
            
            result = f"[실시간 DB 검색 결과]\n최근 활동 사진 {len(photos)}개:\n\n"
            for i, photo in enumerate(photos, 1):
                result += f"{i}. {db_helper.format_activity_photo_info(photo)}\n\n"
            return result
        
        elif intent == "list_all":
            children = db_helper.get_all_children()
            result = f"[실시간 DB 검색 결과]\n전체 아이 목록 ({len(children)}명):\n\n"
            for child in children:
                result += f"- {child.get('name', '알 수 없음')} ({child.get('class_name', '알 수 없음')})\n"
            return result
        
        return ""
        
    except Exception as e:
        logger.error(f"[오류] DB 검색 실패: {str(e)}")
        return f"데이터베이스 검색 중 오류가 발생했습니다: {str(e)}"


# ==============================================
# 4. RAG 챗봇 함수 (하이브리드)
# ==============================================

def generate_answer(query: str) -> Dict[str, Any]:
    """하이브리드 RAG + 실시간 DB 검색 기반 답변 생성"""
    try:
        # 1. 질문 의도 파악
        intent_info = check_query_intent(query)
        
        # 2. 실시간 DB 검색 (필요한 경우)
        db_result = ""
        if intent_info["needs_db"]:
            db_result = search_database(intent_info["intent"], intent_info["params"])
            logger.info(f"[검색] 실시간 DB 검색 수행: {intent_info['intent']}")
        
        # 3. RAG 벡터 검색 (항상 수행)
        docs = retriever.invoke(query, k=CHATBOT_CONFIG["search_results_count"])
        
        # 4. 컨텍스트 구성 (DB 결과 + RAG 결과)
        context_parts = []
        
        # DB 검색 결과가 있으면 우선 추가
        if db_result:
            context_parts.append(f"[최신 데이터베이스 정보]\n{db_result}")
        
        # RAG 검색 결과 추가
        if docs:
            rag_context = "\n\n".join([
                f"[기존 데이터 {i+1}]\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ])
            context_parts.append(rag_context)
        
        if not context_parts:
            return {
                "answer": "죄송합니다. 관련 정보를 찾을 수 없습니다.",
                "sources": []
            }
        
        context = "\n\n==========\n\n".join(context_parts)
        
        # 5. 프롬프트 구성
        prompt = f"""당신은 친절하고 전문적인 AI 어시스턴트입니다.
아래 제공된 정보를 바탕으로 사용자의 질문에 정확하고 상세하게 답변해주세요.

제공된 정보:
{context}

사용자 질문: {query}

답변 지침:
1. 최신 데이터베이스 정보가 있다면 이를 우선적으로 사용하세요
2. 제공된 정보를 바탕으로 정확하게 답변하세요
3. 명확하고 구조화된 형태로 답변하세요
4. 필요시 단계별로 설명하세요
5. 정보가 불충분한 경우 솔직히 말씀해주세요

답변:"""
        
        # LLM 호출
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content
        
        # 6. 출처 정보 구성
        sources = []
        
        # DB 검색 결과도 출처에 추가
        if db_result:
            sources.append({
                "content": "실시간 데이터베이스 검색 결과",
                "metadata": {"type": "real-time", "intent": intent_info["intent"]}
            })
        
        # RAG 검색 결과 추가
        for doc in docs:
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"[오류] 답변 생성 오류: {str(e)}")
        return {
            "answer": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
            "sources": []
        }


# ==============================================
# 5. Flask 라우트
# ==============================================

@app.route('/')
def index():
    """메인 테스트 페이지"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """챗봇 API 엔드포인트"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                "error": "메시지가 비어있습니다."
            }), 400
        
        # RAG 답변 생성
        result = generate_answer(user_message)
        
        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"]
        })
        
    except Exception as e:
        logger.error(f"[오류] API 오류: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """헬스 체크"""
    return jsonify({
        "status": "ok",
        "message": "챗봇 서버가 정상 작동 중입니다."
    })


# ==============================================
# 6. 메인 실행
# ==============================================

if __name__ == '__main__':
    logger.info("="*50)
    logger.info("[시작] 챗봇 웹 서버 시작")
    logger.info("="*50)
    
    # 리소스 초기화
    if initialize_resources():
        # Render 배포 시 PORT 환경변수 사용, 로컬은 8080
        port = int(os.getenv('PORT', 8080))
        logger.info(f"[완료] 서버를 시작합니다: http://0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("[오류] 리소스 초기화 실패. 서버를 시작할 수 없습니다.")

