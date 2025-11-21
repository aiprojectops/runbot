"""
데이터베이스 헬퍼 - MySQL 실시간 쿼리
작성일: 2025-11-20

주요 기능:
- MySQL 실시간 쿼리
- 최신 데이터 조회
- RAG와 결합하여 하이브리드 검색
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseHelper:
    """MySQL 데이터베이스 실시간 조회 헬퍼"""
    
    def __init__(self, json_files_config: Dict[str, Any]):
        """
        초기화 (JSON 파일 기반)
        
        Args:
            json_files_config: config.py의 DATA_EXTRACTION_CONFIG
        """
        self.config = json_files_config
        self.data_cache = {}
        self.load_data()
    
    def load_data(self):
        """JSON 파일에서 데이터 로드 (MySQL 대신)"""
        try:
            for table_key, table_config in self.config.items():
                json_file = table_config.get("json_file")
                if not json_file:
                    continue
                
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                # phpMyAdmin JSON 형식 파싱
                data = []
                for item in json_data:
                    if item.get("type") == "table" and "data" in item:
                        data = item["data"]
                        break
                
                self.data_cache[table_key] = data
                logger.info(f"[완료] {table_key} 테이블 로드: {len(data)}개 행")
                
        except Exception as e:
            logger.error(f"[오류] 데이터 로드 실패: {str(e)}")
    
    def search_children(self, name: Optional[str] = None, 
                       class_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        아이 검색
        
        Args:
            name: 이름 검색어
            class_name: 반 이름 검색어
            
        Returns:
            검색 결과 리스트
        """
        try:
            children_data = self.data_cache.get("children", [])
            results = []
            
            for child in children_data:
                matched = True
                
                if name:
                    child_name = str(child.get("name", ""))
                    if name.lower() not in child_name.lower():
                        matched = False
                
                if class_name:
                    child_class = str(child.get("class_name", ""))
                    if class_name.lower() not in child_class.lower():
                        matched = False
                
                if matched:
                    results.append(child)
            
            logger.info(f"[검색] 아이 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"[오류] 아이 검색 실패: {str(e)}")
            return []
    
    def get_child_by_id(self, child_id: int) -> Optional[Dict[str, Any]]:
        """ID로 아이 정보 조회"""
        try:
            children_data = self.data_cache.get("children", [])
            for child in children_data:
                if int(child.get("id", -1)) == child_id:
                    return child
            return None
        except Exception as e:
            logger.error(f"[오류] 아이 조회 실패: {str(e)}")
            return None
    
    def get_all_children(self) -> List[Dict[str, Any]]:
        """모든 아이 목록 조회"""
        return self.data_cache.get("children", [])
    
    def search_activity_photos(self, title: Optional[str] = None,
                               child_id: Optional[int] = None,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        활동 사진 검색
        
        Args:
            title: 제목 검색어
            child_id: 특정 아이의 사진만
            limit: 최대 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            photos_data = self.data_cache.get("activity_photos", [])
            results = []
            
            for photo in photos_data:
                matched = True
                
                if title:
                    photo_title = str(photo.get("title", ""))
                    if title.lower() not in photo_title.lower():
                        matched = False
                
                if child_id is not None:
                    photo_child_id = photo.get("child_id")
                    if photo_child_id != child_id:
                        matched = False
                
                if matched:
                    results.append(photo)
            
            # 최신순 정렬 (upload_date 기준)
            results.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
            
            # 제한
            results = results[:limit]
            
            logger.info(f"[검색] 활동 사진 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"[오류] 활동 사진 검색 실패: {str(e)}")
            return []
    
    def get_latest_activity_photos(self, limit: int = 5) -> List[Dict[str, Any]]:
        """최신 활동 사진 조회"""
        return self.search_activity_photos(limit=limit)
    
    def format_child_info(self, child: Dict[str, Any]) -> str:
        """아이 정보를 텍스트로 포맷"""
        return f"""
이름: {child.get('name', '알 수 없음')}
반: {child.get('class_name', '알 수 없음')}
성별: {child.get('gender', '알 수 없음')}
생년월일: {child.get('birth_date', '알 수 없음')}
비고: {child.get('notes', '없음')}
""".strip()
    
    def format_activity_photo_info(self, photo: Dict[str, Any]) -> str:
        """활동 사진 정보를 텍스트로 포맷"""
        child_id = photo.get('child_id')
        child_info = ""
        if child_id:
            child = self.get_child_by_id(int(child_id))
            if child:
                child_info = f" ({child.get('name', '알 수 없음')})"
        
        return f"""
제목: {photo.get('title', '알 수 없음')}
설명: {photo.get('description', '없음')}
아이{child_info}
업로드 날짜: {photo.get('upload_date', '알 수 없음')}
""".strip()
    
    def get_statistics(self) -> Dict[str, Any]:
        """데이터베이스 통계"""
        return {
            "children_count": len(self.data_cache.get("children", [])),
            "activity_photos_count": len(self.data_cache.get("activity_photos", [])),
            "last_updated": datetime.now().isoformat()
        }


class MySQLDatabaseHelper(DatabaseHelper):
    """
    실제 MySQL 연결 버전 (선택사항)
    
    사용하려면:
    1. requirements.txt에 pymysql 추가
    2. config.py에 MySQL 설정 추가
    3. 이 클래스 사용
    """
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        MySQL 연결 초기화
        
        Args:
            db_config: MySQL 연결 정보
        """
        try:
            import pymysql
            
            self.connection = pymysql.connect(
                host=db_config["host"],
                port=db_config.get("port", 3306),
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("[완료] MySQL 연결 성공")
            
        except ImportError:
            logger.error("[오류] pymysql이 설치되지 않았습니다. pip install pymysql")
            raise
        except Exception as e:
            logger.error(f"[오류] MySQL 연결 실패: {str(e)}")
            raise
    
    def search_children(self, name: Optional[str] = None, 
                       class_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """MySQL에서 직접 아이 검색"""
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM children WHERE 1=1"
                params = []
                
                if name:
                    query += " AND name LIKE %s"
                    params.append(f"%{name}%")
                
                if class_name:
                    query += " AND class_name LIKE %s"
                    params.append(f"%{class_name}%")
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                logger.info(f"[검색] MySQL 아이 검색 완료: {len(results)}개 결과")
                return results
                
        except Exception as e:
            logger.error(f"[오류] MySQL 검색 실패: {str(e)}")
            return []
    
    def search_products(self, name: Optional[str] = None, 
                       status: Optional[str] = "판매중") -> List[Dict[str, Any]]:
        """MySQL에서 직접 제품 검색"""
        try:
            with self.connection.cursor() as cursor:
                # 모든 컬럼 조회 (출하 예정일 등 포함)
                query = "SELECT * FROM products WHERE 1=1"
                params = []
                
                if name:
                    query += " AND name LIKE %s"
                    params.append(f"%{name}%")
                
                if status:
                    query += " AND status = %s"
                    params.append(status)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                logger.info(f"[검색] MySQL 제품 검색 완료: {len(results)}개 결과")
                return results
                
        except Exception as e:
            logger.error(f"[오류] MySQL 제품 검색 실패: {str(e)}")
            return []
    
    def get_all_products(self, status: Optional[str] = "판매중") -> List[Dict[str, Any]]:
        """모든 제품 목록 조회"""
        return self.search_products(status=status)
    
    def get_all_children(self) -> List[Dict[str, Any]]:
        """모든 아이 목록 조회"""
        return self.search_children()
    
    def format_product_info(self, product: Dict[str, Any]) -> str:
        """제품 정보를 보기 좋게 포맷팅"""
        info = f"🛒 제품명: {product.get('name', 'N/A')}\n"
        info += f"💰 가격: {product.get('price', 'N/A')}원"
        
        if product.get('discount_price') and product.get('discount_price') != product.get('price'):
            info += f" → {product.get('discount_price')}원 (할인 중!)"
        
        info += f"\n📦 재고: {product.get('stock_quantity', 'N/A')}개\n"
        info += f"📌 상태: {product.get('status', 'N/A')}"
        
        # 출하 예정일 추가 (여러 가능한 컬럼 이름 확인)
        shipping_date = (product.get('shipping_date') or 
                        product.get('delivery_date') or 
                        product.get('expected_date') or
                        product.get('출하예정일') or
                        product.get('expected_shipping_date'))
        
        if shipping_date:
            info += f"\n🚚 출하 예정일: {shipping_date}"
        
        # description이 있으면 앞부분만 추가
        if product.get('description'):
            desc = product.get('description', '')[:100].strip()
            if desc:
                info += f"\n📝 설명: {desc}..."
        
        return info
    
    def __del__(self):
        """연결 종료"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            logger.info("[완료] MySQL 연결 종료")

