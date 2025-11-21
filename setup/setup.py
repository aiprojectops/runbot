"""
챗봇 셋업 자동화 스크립트

이 스크립트는 새로운 회사를 위한 챗봇을 설정합니다.
- .env 파일 생성
- config.py 생성
- database_helper.py 생성

사용법:
    python setup/setup.py
"""

import os
import sys
from pathlib import Path
import re

def get_input(prompt, default=None, password=False):
    """사용자 입력 받기"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    if password:
        import getpass
        value = getpass.getpass(prompt_text)
    else:
        value = input(prompt_text)
    
    return value if value else default

def validate_company_id(company_name):
    """회사 이름을 company_id로 변환"""
    # 소문자, 공백을 언더스코어로
    company_id = company_name.lower().replace(' ', '_')
    # 특수문자 제거
    company_id = re.sub(r'[^a-z0-9_]', '', company_id)
    return company_id

def main():
    print("=" * 60)
    print("🤖 챗봇 셋업 마법사")
    print("=" * 60)
    print("\n이 스크립트는 새 회사를 위한 챗봇을 자동으로 설정합니다.")
    print("필요한 정보를 입력해주세요.\n")
    
    # 1. 회사 정보
    print("📋 1단계: 회사 정보")
    print("-" * 60)
    company_name = get_input("회사 이름 (예: ABC Corp)")
    if not company_name:
        print("❌ 회사 이름은 필수입니다.")
        sys.exit(1)
    
    company_id = validate_company_id(company_name)
    print(f"✅ Company ID: {company_id}")
    
    # 2. OpenAI 설정
    print("\n🤖 2단계: OpenAI API 키")
    print("-" * 60)
    print("OpenAI API 키 발급: https://platform.openai.com/api-keys")
    print("💡 팁: Ctrl+V로 붙여넣기 가능")
    openai_key = get_input("OpenAI API Key")  # password=True 제거
    if not openai_key:
        print("❌ OpenAI API 키는 필수입니다.")
        sys.exit(1)
    
    # 3. Supabase 설정
    print("\n☁️ 3단계: Supabase 설정")
    print("-" * 60)
    print("Supabase 프로젝트 생성: https://supabase.com")
    supabase_url = get_input("Supabase URL (예: https://xxx.supabase.co)")
    if not supabase_url:
        print("❌ Supabase URL은 필수입니다.")
        sys.exit(1)
    
    print("💡 팁: Settings > API > service_role key 복사")
    supabase_key = get_input("Supabase Service Role Key")  # password=True 제거
    if not supabase_key:
        print("❌ Supabase 키는 필수입니다.")
        sys.exit(1)
    
    # 4. MySQL 설정 (선택)
    print("\n🗄️ 4단계: MySQL 설정 (선택사항)")
    print("-" * 60)
    use_mysql = get_input("MySQL 사용? (y/n)", default="n").lower() == 'y'
    
    mysql_config = {
        'USE_MYSQL_CONNECTION': 'True' if use_mysql else 'False',
        'CAFE24_DB_HOST': '',
        'CAFE24_DB_PORT': '3306',
        'CAFE24_DB_USER': '',
        'CAFE24_DB_PASSWORD': '',
        'CAFE24_DB_DATABASE': ''
    }
    
    if use_mysql:
        mysql_config['CAFE24_DB_HOST'] = get_input("MySQL Host")
        mysql_config['CAFE24_DB_PORT'] = get_input("MySQL Port", default="3306")
        mysql_config['CAFE24_DB_USER'] = get_input("MySQL User")
        print("💡 팁: 비밀번호가 화면에 표시됩니다. 조심하세요!")
        mysql_config['CAFE24_DB_PASSWORD'] = get_input("MySQL Password")  # password=True 제거
        mysql_config['CAFE24_DB_DATABASE'] = get_input("MySQL Database")
    
    # 5. 설정 파일 생성
    print("\n📝 5단계: 설정 파일 생성 중...")
    print("-" * 60)
    
    # .env 파일 생성
    template_path = Path("templates/env.template")
    if not template_path.exists():
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        sys.exit(1)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # 플레이스홀더 치환
    replacements = {
        '{{COMPANY_NAME}}': company_name,
        '{{COMPANY_ID}}': company_id,
        '{{OPENAI_API_KEY}}': openai_key,
        '{{SUPABASE_URL}}': supabase_url,
        '{{SUPABASE_SERVICE_ROLE_KEY}}': supabase_key,
        **{f'{{{{{k}}}}}': v for k, v in mysql_config.items()}
    }
    
    for placeholder, value in replacements.items():
        env_content = env_content.replace(placeholder, value)
    
    # .env 파일 저장
    env_path = Path(".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print(f"✅ .env 파일 생성 완료")
    
    # data 폴더 생성
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ data/ 폴더 생성 완료")
    
    # 완료 메시지
    print("\n" + "=" * 60)
    print("🎉 셋업 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. data/ 폴더에 회사 데이터 파일을 추가하세요 (JSON, PDF, 이미지)")
    print("2. 파일 처리: python setup/file_processor.py")
    print("3. 데이터 로드: python 1_mysql_data_loader.py")
    print("4. 임베딩 생성: python 2_embedding_generator.py")
    print("5. 챗봇 실행: python 4_chatbot_web.py")
    print("\n배포:")
    print("- Render: 이 폴더를 GitHub에 푸시하고 Render에서 배포")
    print("- 환경변수는 .env 내용을 Render 대시보드에 입력")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

