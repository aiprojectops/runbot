-- ============================================
-- cafe24 MySQL RAG 챗봇 Supabase 설정 SQL
-- 작성일: 2025-01-20
-- ============================================
-- 
-- 사용 방법:
-- 1. Supabase 대시보드 접속 (https://app.supabase.com)
-- 2. 프로젝트 선택
-- 3. SQL Editor 메뉴 클릭
-- 4. 이 SQL 파일 전체를 붙여넣기
-- 5. 'RUN' 버튼 클릭
--
-- ============================================

-- 1. Vector Extension 활성화 (필수)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 임베딩 저장 테이블 생성
CREATE TABLE IF NOT EXISTS mysql_data_embeddings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content text NOT NULL,                      -- 원본 텍스트 내용
    metadata jsonb,                             -- 메타데이터 (테이블명, 컬럼 정보 등)
    embedding vector(1536),                     -- OpenAI text-embedding-3-small 임베딩 (1536 차원)
    created_at timestamp with time zone DEFAULT now()
);

-- 3. 벡터 검색 성능을 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS mysql_data_embeddings_embedding_idx 
ON mysql_data_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. 메타데이터 검색을 위한 GIN 인덱스
CREATE INDEX IF NOT EXISTS mysql_data_embeddings_metadata_idx 
ON mysql_data_embeddings 
USING gin (metadata);

-- 5. 전문 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS mysql_data_embeddings_content_idx 
ON mysql_data_embeddings 
USING gin (to_tsvector('english', content));

-- 6. 벡터 유사도 검색 함수 생성
CREATE OR REPLACE FUNCTION match_mysql_embeddings(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        mysql_data_embeddings.id,
        mysql_data_embeddings.content,
        mysql_data_embeddings.metadata,
        1 - (mysql_data_embeddings.embedding <=> query_embedding) AS similarity
    FROM mysql_data_embeddings
    WHERE 1 - (mysql_data_embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY mysql_data_embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 7. RLS (Row Level Security) 설정
ALTER TABLE mysql_data_embeddings ENABLE ROW LEVEL SECURITY;

-- 8. 공개 읽기 권한 정책
CREATE POLICY "Allow public read access" 
ON mysql_data_embeddings 
FOR SELECT 
USING (true);

-- 9. 인증된 사용자 쓰기 권한 정책
CREATE POLICY "Allow authenticated insert access" 
ON mysql_data_embeddings 
FOR INSERT 
WITH CHECK (true);

-- 10. 인증된 사용자 업데이트 권한 정책
CREATE POLICY "Allow authenticated update access" 
ON mysql_data_embeddings 
FOR UPDATE 
USING (true);

-- 11. 인증된 사용자 삭제 권한 정책
CREATE POLICY "Allow authenticated delete access" 
ON mysql_data_embeddings 
FOR DELETE 
USING (true);

-- ============================================
-- 설정 확인 쿼리
-- ============================================

-- Extension 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 테이블 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'mysql_data_embeddings'
) AS table_exists;

-- 함수 확인
SELECT EXISTS (
    SELECT FROM pg_proc 
    WHERE proname = 'match_mysql_embeddings'
) AS function_exists;

-- 인덱스 확인
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'mysql_data_embeddings';

-- ============================================
-- 완료 메시지
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ Supabase 설정 완료!';
    RAISE NOTICE '📋 테이블명: mysql_data_embeddings';
    RAISE NOTICE '🔍 검색 함수: match_mysql_embeddings';
    RAISE NOTICE '';
    RAISE NOTICE '📌 다음 단계:';
    RAISE NOTICE '   1. config.example.py를 config.py로 복사';
    RAISE NOTICE '   2. config.py에 실제 값 입력';
    RAISE NOTICE '   3. python 1_mysql_data_loader.py 실행';
    RAISE NOTICE '   4. python 2_embedding_generator.py 실행';
    RAISE NOTICE '   5. streamlit run 3_chatbot_app.py 실행';
END $$;

