"""
2단계: 추출된 데이터를 임베딩하여 Supabase 벡터 DB에 저장
작성일: 2025-01-20

주요 기능:
- JSON에서 Document 로드
- 텍스트 분할 (Chunking)
- Cohere 임베딩 생성
- Supabase 벡터 DB 저장
"""

import json
import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from supabase import create_client
from tqdm import tqdm

# 설정 파일 임포트
try:
    from config import (
        OPENAI_API_KEY,
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
        EMBEDDING_CONFIG,
        SUPABASE_TABLES,
        LOGGING_CONFIG
    )
except ImportError:
    print("[오류] config.py 파일이 없습니다!")
    print("[참고] config.example.py를 config.py로 복사하고 실제 값을 입력하세요.")
    exit(1)

# 로깅 설정
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """임베딩 생성 및 벡터 DB 저장 클래스"""
    
    def __init__(self):
        """초기화"""
        # OpenAI 임베딩 모델
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_CONFIG["model"],
            openai_api_key=OPENAI_API_KEY
        )
        
        # Supabase 클라이언트
        self.supabase_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY
        )
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", " ", ""],
            chunk_size=EMBEDDING_CONFIG["chunk_size"],
            chunk_overlap=EMBEDDING_CONFIG["chunk_overlap"],
            length_function=len
        )
        
        logger.info("[완료] 임베딩 생성기 초기화 완료")
    
    def load_documents_from_json(self, file_path: str) -> List[Document]:
        """
        JSON 파일에서 Document 로드
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            Document 객체 리스트
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            documents = [
                Document(
                    page_content=item["page_content"],
                    metadata=item["metadata"]
                )
                for item in data
            ]
            
            logger.info(f"[완료] {len(documents)}개 Document 로드 완료: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"[오류] Document 로드 실패: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        긴 문서를 청크로 분할
        
        Args:
            documents: 원본 Document 리스트
            
        Returns:
            분할된 Document 리스트
        """
        try:
            logger.info(f"[분할] 문서 분할 시작 (청크 크기: {EMBEDDING_CONFIG['chunk_size']})")
            
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"[완료] {len(documents)}개 문서 -> {len(chunks)}개 청크로 분할")
            return chunks
            
        except Exception as e:
            logger.error(f"[오류] 문서 분할 실패: {str(e)}")
            return documents
    
    def save_to_supabase(self, documents: List[Document]) -> bool:
        """
        Supabase 벡터 DB에 저장
        
        Args:
            documents: 저장할 Document 리스트
            
        Returns:
            성공 여부
        """
        try:
            logger.info(f"[저장] Supabase에 {len(documents)}개 문서 저장 시작...")
            
            # 배치 처리로 저장
            batch_size = EMBEDDING_CONFIG["batch_size"]
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            for i in tqdm(range(0, len(documents), batch_size), desc="임베딩 생성 및 저장"):
                batch = documents[i:i + batch_size]
                
                try:
                    # SupabaseVectorStore에 저장
                    SupabaseVectorStore.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        client=self.supabase_client,
                        table_name=SUPABASE_TABLES["embeddings"],
                        query_name=SUPABASE_TABLES["match_function"]
                    )
                    
                    logger.info(f"[완료] 배치 {i//batch_size + 1}/{total_batches} 저장 완료")
                    
                except Exception as batch_error:
                    logger.error(f"[경고] 배치 {i//batch_size + 1} 저장 실패: {str(batch_error)}")
                    continue
            
            logger.info("[완료] Supabase 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"[오류] Supabase 저장 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """메인 실행 함수"""
    logger.info("="*50)
    logger.info("[시작] 임베딩 생성 및 저장 시작")
    logger.info("="*50)
    
    # 임베딩 생성기 초기화
    generator = EmbeddingGenerator()
    
    # 1단계에서 생성한 JSON 파일 로드
    input_file = "extracted_data.json"
    documents = generator.load_documents_from_json(input_file)
    
    if not documents:
        logger.error("[오류] Document를 로드할 수 없습니다.")
        return
    
    # 문서 분할
    chunks = generator.split_documents(documents)
    
    # Supabase에 저장
    success = generator.save_to_supabase(chunks)
    
    if success:
        logger.info("\n" + "="*50)
        logger.info("[완료] 임베딩 생성 및 저장 완료")
        logger.info("="*50)
        logger.info(f"[결과] 처리 결과:")
        logger.info(f"   - 원본 문서 수: {len(documents)}")
        logger.info(f"   - 분할된 청크 수: {len(chunks)}")
        logger.info(f"   - 저장 위치: {SUPABASE_TABLES['embeddings']} 테이블")
        logger.info("\n[다음] 다음 단계: python 3_chatbot_app.py 실행")
    else:
        logger.error("[오류] 임베딩 저장 실패")


if __name__ == "__main__":
    main()

