# 영수증 OCR 처리 시스템

## 프로젝트 개요
이 프로젝트는 영수증 이미지를 OCR(광학 문자 인식) 기술을 활용하여 텍스트로 변환하고, 추출된 텍스트에서 가게명과 구매한 상품 정보를 자동으로 식별하여 구조화된 데이터로 제공하는 시스템입니다.

## 주요 기능
- **이미지 OCR 처리**: EasyOCR을 이용한 영수증 이미지의 텍스트 추출
- **텍스트 후처리**: OCR에서 발생하는 오류 수정 및 텍스트 정규화
- **정보 추출**: 가게명, 상품명, 가격, 수량 등 중요 정보 추출
- **데이터 구조화**: JSON 형식으로 결과 저장
- **시각화**: 인식된 텍스트 위치 표시 이미지 생성

## 처리 파이프라인
1. **이미지 입력**: `input` 폴더에 영수증 이미지 파일 배치
2. **OCR 처리**: `image_to_text.py`가 이미지에서 텍스트 추출
3. **텍스트 후처리**: `process_text.py`가 OCR 결과 정규화 및 오류 수정
4. **정보 추출**: `extract_item.py`가 메뉴 항목, 가격 정보 추출
5. **JSON 출력**: 구조화된 데이터를 `output/json` 폴더에 저장

## 폴더 구조
```
./
│
├── input/                           # 입력 영수증 이미지 폴더
│
├── output/                          # 출력 결과 폴더
│   ├── ocr_vis/                     # OCR 시각화 이미지
│   ├── ocr_raw_txt/                 # OCR 원본 텍스트
│   ├── ocr_processed_txt/           # 후처리된 텍스트
│   └── json/                        # 추출된 정보 JSON 파일
│
├── image_to_text.py                 # 이미지 OCR 모듈
├── process_text.py                  # 텍스트 후처리 모듈
├── extract_item.py                  # 정보 추출 모듈
├── dictionary.txt                   # 영수증 용어 사전
└── README.md                        # 프로젝트 설명서
```

## 사용 방법
1. `input` 폴더에 처리할 영수증 이미지를 넣습니다.
2. 각 단계별로 스크립트를 실행합니다:
   ```
   python image_to_text.py   # OCR 처리
   python process_text.py    # 텍스트 후처리
   python extract_item.py    # 정보 추출
   ```
3. 처리 결과는 `output/json` 폴더에서 확인할 수 있습니다.

## 구현 기술
- **이미지 처리**: PIL(Python Imaging Library) 사용
- **OCR**: EasyOCR 라이브러리 사용 (한국어, 영어 지원)
- **텍스트 처리**: 정규표현식과 Levenshtein 거리를 활용한 텍스트 교정
- **정보 추출**: 패턴 인식 및 컨텍스트 분석

## JSON 출력 예시
```json
{
  "filename": "receipt1",
  "store_name": "동국대화교소비자생 환협동조합",
  "items": [
    {
      "menu": "언치즈손밥",
      "price": "5000",
      "amount": "5000",
      "quantity": "1"
    },
    {
      "menu": "삼경김치철만",
      "price": "6000",
      "amount": "6000",
      "quantity": "1"
    }
  ],
  "total_amount": 11000
}
```

## 설치 요구사항
```
pip install easyocr pillow python-Levenshtein
```

## 향후 개선사항
- 다양한 영수증 포맷 지원 확장
- 결제 방법, 할인 정보 등 추가 데이터 추출
- 웹 인터페이스 구현
