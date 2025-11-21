"""
1단계: JSON 파일에서 데이터 추출
작성일: 2025-01-20
수정일: 2025-01-20 (JSON 파일 직접 로드 방식으로 변경)

주요 기능:
- data/ 폴더의 JSON 파일 로드
- Document 객체로 변환
- extracted_data.json 파일로 저장
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from langchain_core.documents import Document
import os

# 설정 파일 임포트
try:
    from config import (
        DATA_EXTRACTION_CONFIG,
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


class JSONDataLoader:
    """JSON 파일에서 데이터를 추출하는 클래스"""
    
    def __init__(self):
        """초기화"""
        logger.info("[완료] JSON 데이터 로더 초기화 완료")
    
    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        JSON 파일 로드
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            데이터 리스트
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"[오류] 파일을 찾을 수 없습니다: {file_path}")
                return []
            
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            # phpMyAdmin JSON 형식 처리
            # 구조: [header, database, table_with_data]
            data = []
            
            for item in json_data:
                if item.get("type") == "table" and "data" in item:
                    data = item["data"]
                    break
            
            if not data:
                logger.warning(f"[경고] {file_path}에서 데이터를 찾을 수 없습니다.")
                return []
            
            logger.info(f"[완료] {file_path}에서 {len(data)}개 행 로드 완료")
            return data
            
        except Exception as e:
            logger.error(f"[오류] JSON 파일 로드 실패: {str(e)}")
            return []
    
    def convert_to_documents(
        self, 
        data: List[Dict[str, Any]], 
        text_columns: List[str],
        metadata_columns: List[str],
        table_name: str
    ) -> List[Document]:
        """
        JSON 데이터를 LangChain Document 객체로 변환
        
        Args:
            data: JSON에서 추출한 데이터
            text_columns: 텍스트로 합칠 컬럼 목록
            metadata_columns: 메타데이터로 저장할 컬럼 목록
            table_name: 테이블명 (메타데이터에 포함)
            
        Returns:
            Document 객체 리스트
        """
        documents = []
        
        for row in data:
            try:
                # 텍스트 내용 구성
                text_parts = []
                for col in text_columns:
                    if col in row and row[col] and row[col] != "null":
                        value = str(row[col])
                        # None이나 빈 문자열 제외
                        if value and value.lower() not in ["none", "null", ""]:
                            text_parts.append(f"{col}: {value}")
                
                # 텍스트가 없으면 건너뛰기
                if not text_parts:
                    logger.debug(f"[경고] 텍스트 컬럼이 비어있어 건너뜁니다: {row}")
                    continue
                
                page_content = "\n".join(text_parts)
                
                # 메타데이터 구성
                metadata = {
                    "source": table_name,
                    "extraction_date": datetime.now().isoformat()
                }
                
                for col in metadata_columns:
                    if col in row:
                        value = row[col]
                        # None이나 null 값 처리
                        if value is not None and value != "null":
                            metadata[col] = value
                
                # Document 생성
                doc = Document(
                    page_content=page_content,
                    metadata=metadata
                )
                documents.append(doc)
                
            except Exception as e:
                logger.warning(f"[경고] 행 변환 실패: {str(e)}")
                continue
        
        logger.info(f"[완료] {len(documents)}개 Document 객체 생성 완료")
        return documents


def main():
    """메인 실행 함수"""
    logger.info("="*50)
    logger.info("[시작] JSON 데이터 추출 시작")
    logger.info("="*50)
    
    # JSON 데이터 로더 초기화
    loader = JSONDataLoader()
    
    # 모든 테이블에서 데이터 추출
    all_documents = []
    
    try:
        for table_key, table_config in DATA_EXTRACTION_CONFIG.items():
            logger.info(f"\n[처리] 테이블 처리 중: {table_key}")
            
            # JSON 파일 경로 확인
            json_file = table_config.get("json_file")
            if not json_file:
                logger.error(f"[오류] {table_key}에 json_file 경로가 없습니다.")
                continue
            
            # 데이터 로드
            raw_data = loader.load_json_file(json_file)
            
            if not raw_data:
                logger.warning(f"[경고] {table_key}에서 데이터를 가져오지 못했습니다.")
                continue
            
            logger.info(f"[결과] 로드된 데이터: {len(raw_data)}개 행")
            logger.info(f"[정보] 텍스트 컬럼: {table_config['text_columns']}")
            
            # Document 변환
            documents = loader.convert_to_documents(
                data=raw_data,
                text_columns=table_config["text_columns"],
                metadata_columns=table_config["metadata_columns"],
                table_name=table_config["table"]
            )
            
            all_documents.extend(documents)
            logger.info(f"[완료] {table_key}: {len(documents)}개 Document 생성")
        
        # 결과 저장 (JSON 형태로)
        output_file = "extracted_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            documents_dict = [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in all_documents
            ]
            json.dump(documents_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n[완료] 총 {len(all_documents)}개 Document 추출 완료")
        logger.info(f"[저장] 결과 저장: {output_file}")
        
        # 추출된 내용 미리보기
        if all_documents:
            logger.info("\n" + "="*50)
            logger.info("[미리보기] 추출된 데이터 미리보기 (첫 2개)")
            logger.info("="*50)
            for i, doc in enumerate(all_documents[:2]):
                logger.info(f"\n[Document {i+1}]")
                logger.info(f"내용:\n{doc.page_content}")
                logger.info(f"메타데이터: {doc.metadata}")
        
    except Exception as e:
        logger.error(f"[오류] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "="*50)
    logger.info("[완료] 데이터 추출 완료")
    logger.info("="*50)
    logger.info("[다음] 다음 단계: python 2_embedding_generator.py 실행")


if __name__ == "__main__":
    main()
