"""
파일 처리 스크립트 v2 (폴더 구조 지원)

data/ 폴더의 다양한 파일을 처리합니다.

두 가지 방식 지원:
1. 단순 모드: data/에 모든 파일 → 자동 처리
2. 구조화 모드: data/json/, data/pdf/ 등 → 폴더별 처리

지원 형식:
- JSON, PDF, 이미지, Word, Excel

사용법:
    python setup/file_processor_v2.py
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
import mimetypes

def get_file_type(file_path: Path) -> str:
    """파일 형식 자동 감지"""
    ext = file_path.suffix.lower()
    
    type_map = {
        '.json': 'json',
        '.pdf': 'pdf',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.docx': 'word',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.csv': 'csv',
    }
    
    return type_map.get(ext, 'unknown')

def process_json_file(file_path: Path, folder_name: str = None) -> List[Dict[str, Any]]:
    """JSON 파일 처리"""
    print(f"  📄 JSON: {file_path.name}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # phpMyAdmin 형식 처리
    if isinstance(data, list) and len(data) > 0:
        for item in data:
            if item.get("type") == "table" and "data" in item:
                data = item["data"]
                break
    
    # 리스트가 아니면 리스트로 변환
    if not isinstance(data, list):
        data = [data]
    
    # 메타데이터 추가
    for item in data:
        if isinstance(item, dict):
            item['_source_type'] = 'json'
            item['_source_file'] = str(file_path)
            if folder_name:
                item['_source_folder'] = folder_name
    
    return data

def process_pdf_file(file_path: Path, folder_name: str = None) -> List[Dict[str, Any]]:
    """PDF 파일 처리"""
    print(f"  📕 PDF: {file_path.name}")
    
    try:
        import PyPDF2
    except ImportError:
        print("    ⚠️ PyPDF2가 설치되지 않았습니다. pip install PyPDF2")
        return []
    
    documents = []
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    "id": f"{file_path.stem}_page_{page_num + 1}",
                    "title": f"{file_path.stem} - 페이지 {page_num + 1}",
                    "content": text.strip(),
                    "source": str(file_path),
                    "page": page_num + 1,
                    "_source_type": "pdf",
                    "_source_file": str(file_path),
                    "_source_folder": folder_name or "root"
                })
    
    print(f"    ✅ {len(documents)}개 페이지 추출됨")
    return documents

def process_image_file(file_path: Path, folder_name: str = None) -> List[Dict[str, Any]]:
    """이미지 파일 처리 (OCR)"""
    print(f"  🖼️ 이미지: {file_path.name}")
    
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        print("    ⚠️ PIL 또는 pytesseract가 설치되지 않았습니다.")
        print("    pip install Pillow pytesseract")
        return []
    
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='kor+eng')
        
        if text.strip():
            return [{
                "id": file_path.stem,
                "title": file_path.stem,
                "content": text.strip(),
                "source": str(file_path),
                "type": "image_ocr",
                "_source_type": "image",
                "_source_file": str(file_path),
                "_source_folder": folder_name or "root"
            }]
        else:
            print("    ⚠️ 텍스트를 추출할 수 없습니다")
            return []
    except Exception as e:
        print(f"    ❌ OCR 실패: {str(e)}")
        return []

def process_docx_file(file_path: Path, folder_name: str = None) -> List[Dict[str, Any]]:
    """Word 문서 처리"""
    print(f"  📘 Word: {file_path.name}")
    
    try:
        from docx import Document
    except ImportError:
        print("    ⚠️ python-docx가 설치되지 않았습니다. pip install python-docx")
        return []
    
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    if text.strip():
        return [{
            "id": file_path.stem,
            "title": file_path.stem,
            "content": text.strip(),
            "source": str(file_path),
            "type": "word",
            "_source_type": "word",
            "_source_file": str(file_path),
            "_source_folder": folder_name or "root"
        }]
    return []

def process_excel_file(file_path: Path, folder_name: str = None) -> List[Dict[str, Any]]:
    """Excel 파일 처리"""
    print(f"  📊 Excel: {file_path.name}")
    
    try:
        import pandas as pd
    except ImportError:
        print("    ⚠️ pandas가 설치되지 않았습니다. pip install pandas openpyxl")
        return []
    
    df = pd.read_excel(file_path)
    records = df.to_dict('records')
    
    # 메타데이터 추가
    for record in records:
        record['_source_type'] = 'excel'
        record['_source_file'] = str(file_path)
        record['_source_folder'] = folder_name or "root"
    
    print(f"    ✅ {len(records)}개 행 추출됨")
    return records

def scan_directory(base_path: Path) -> Dict[str, List[Path]]:
    """
    디렉토리 스캔
    
    Returns:
        {
            'json': [파일들],
            'pdf': [파일들],
            ...
        }
    """
    file_handlers = {
        '.json': 'json',
        '.pdf': 'pdf',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.docx': 'word',
        '.xlsx': 'excel',
        '.xls': 'excel',
    }
    
    files_by_type = {}
    
    # 재귀적으로 모든 파일 찾기
    for file_path in base_path.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            file_type = file_handlers.get(ext)
            
            if file_type:
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                
                # 상대 폴더 경로 계산
                rel_path = file_path.relative_to(base_path)
                folder_name = str(rel_path.parent) if rel_path.parent != Path('.') else 'root'
                
                files_by_type[file_type].append({
                    'path': file_path,
                    'folder': folder_name
                })
    
    return files_by_type

def main():
    print("=" * 60)
    print("📁 파일 처리 시작 (v2 - 폴더 구조 지원)")
    print("=" * 60)
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ 폴더가 없습니다.")
        return
    
    # 파일 스캔
    print("\n🔍 파일 스캔 중...\n")
    files_by_type = scan_directory(data_dir)
    
    if not files_by_type:
        print("⚠️ 처리 가능한 파일이 없습니다.")
        return
    
    # 통계 출력
    print(f"발견된 파일 형식:")
    for file_type, files in files_by_type.items():
        print(f"  - {file_type}: {len(files)}개")
    print()
    
    # 파일 처리
    all_documents = []
    
    processors = {
        'json': process_json_file,
        'pdf': process_pdf_file,
        'image': process_image_file,
        'word': process_docx_file,
        'excel': process_excel_file,
    }
    
    for file_type, files in files_by_type.items():
        processor = processors.get(file_type)
        if not processor:
            continue
        
        print(f"\n📂 {file_type.upper()} 파일 처리 중...")
        print("-" * 60)
        
        for file_info in files:
            file_path = file_info['path']
            folder_name = file_info['folder']
            
            try:
                docs = processor(file_path, folder_name)
                all_documents.extend(docs)
            except Exception as e:
                print(f"  ❌ 처리 실패 ({file_path.name}): {str(e)}")
    
    # 결과 저장
    if all_documents:
        output_path = data_dir / "processed_data.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_documents, f, ensure_ascii=False, indent=2)
        
        # 통계 출력
        print("\n" + "=" * 60)
        print(f"✅ 처리 완료!")
        print("=" * 60)
        print(f"📊 통계:")
        
        by_type = {}
        by_folder = {}
        for doc in all_documents:
            # 형식별 통계
            source_type = doc.get('_source_type', 'unknown')
            by_type[source_type] = by_type.get(source_type, 0) + 1
            
            # 폴더별 통계
            source_folder = doc.get('_source_folder', 'root')
            by_folder[source_folder] = by_folder.get(source_folder, 0) + 1
        
        print(f"\n📈 형식별:")
        for ftype, count in by_type.items():
            print(f"  - {ftype}: {count}개")
        
        print(f"\n📂 폴더별:")
        for folder, count in by_folder.items():
            print(f"  - {folder}: {count}개")
        
        print(f"\n💾 총 {len(all_documents)}개 문서")
        print(f"📄 저장 위치: {output_path}")
        print("=" * 60)
        print("\n다음 단계:")
        print("  python 1_mysql_data_loader.py")
        print("  python 2_embedding_generator.py")
    else:
        print("\n❌ 처리된 문서가 없습니다.")

if __name__ == "__main__":
    main()

