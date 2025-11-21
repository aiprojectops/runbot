# 📊 데이터 폴더

이 폴더에 회사 데이터 파일을 추가하세요.

## 지원 형식

- ✅ JSON (`.json`)
- ✅ PDF (`.pdf`)
- ✅ 이미지 (`.jpg`, `.png`) - OCR 처리
- ✅ Word (`.docx`)
- ✅ Excel (`.xlsx`)

## 사용 방법

### 1. 파일 추가
```bash
# 이 폴더에 파일 복사
data/
├── products.json
├── manual.pdf
├── receipt.jpg
└── faq.docx
```

### 2. 파일 처리
```bash
python setup/file_processor_v2.py
# → data/processed_data.json 생성
```

### 3. 파이프라인 실행
```bash
python 1_mysql_data_loader.py
python 2_embedding_generator.py
```

## 주의사항

⚠️ **실제 데이터 파일은 Git에 커밋하지 마세요!**
- `.gitignore`에 의해 자동으로 제외됩니다
- 민감한 정보가 포함될 수 있습니다

## 예시 데이터

예시 데이터는 별도로 제공되지 않습니다. 
실제 회사 데이터를 추가하여 사용하세요.

