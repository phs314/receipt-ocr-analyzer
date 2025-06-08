# 영수증 OCR 분석기 (Receipt OCR Analyzer)

영수증 이미지에서 텍스트를 추출하고 메뉴 항목과 가격 정보를 구조화된 JSON 형태로 변환하는 도구입니다.

## 주요 기능

- **이미지 OCR 처리**: 영수증 이미지에서 텍스트 추출
- **텍스트 후처리**: OCR 오류 보정 및 정규화
- **메뉴 항목 추출**: 가게명, 메뉴, 가격, 수량 정보 추출
- **사전 기반 매칭**: 한글 자모 분해를 통한 유사도 계산으로 정확도 향상
- **JSON 출력**: 구조화된 데이터 형태로 결과 저장
- **성능 비교**: 다양한 추출 방법 간의 성능 평가

## 📁 프로젝트 구조

```
receipt-ocr-analyzer/
│
├── 🚀 메인 실행 파일
│   └── main.py                    # 전체 파이프라인 실행
│
├── 🔧 핵심 처리 모듈
│   ├── ocr_extract.py             # OCR 텍스트 추출
│   ├── process_text.py            # 텍스트 후처리 및 사전 매칭
│   ├── extract_item.py            # 기본 메뉴 항목 추출 (패턴 기반)
│   └── extract_item2.py           # 개선된 메뉴 항목 추출 (사전 기반)
│
├── 📊 성능 비교 도구
│   ├── compare_accuracy.py        # 추출 정확도 비교 도구
│   └── compare_performance.py     # 추출 성능 비교 도구
│
├── 📚 사전 관리 도구
│   ├── dictionary_item.py         # 메뉴 사전 관리 도구
│   └── dictionary_store.py        # 가게 사전 관리 도구
│
├── 📝 사전 파일
│   ├── dictionary.txt             # 기본 한글 단어 사전
│   ├── dictionary_item.txt        # 메뉴 사전
│   ├── dictionary_store.txt       # 가게 사전
│   └── dictionary_store_item.json # 가게별 메뉴 사전 (개선된 버전용)
│
├── 📁 입력 폴더
│   └── images/                    # 🖼️ 영수증 이미지 파일 (jpg, png, etc.)
│       ├── receipt_001.jpg
│       ├── receipt_002.png
│       └── ...
│
└── 📁 출력 폴더
    └── output/
        ├── 📄 ocr_raw_txt/        # OCR 원본 텍스트 (.txt)
        │   ├── receipt_001_raw.txt
        │   ├── receipt_002_raw.txt
        │   └── ...
        │
        ├── ✨ ocr_processed_txt/   # 후처리된 텍스트 (.txt)
        │   ├── receipt_001_processed.txt
        │   ├── receipt_002_processed.txt
        │   └── ...
        │
        └── 📋 json/               # 최종 JSON 결과 (.json)
            ├── receipt_001.json
            ├── receipt_002.json
            └── ...
```

## ⚡ 데이터 흐름

```
🖼️ Images              📄 Raw OCR           ✨ Processed Text      📋 Final JSON
┌─────────────┐       ┌─────────────┐      ┌─────────────────┐    ┌─────────────┐
│ receipt.jpg │  ➜    │ receipt.txt │  ➜   │ receipt_proc.txt│ ➜  │ receipt.json│
│ receipt.png │       │ (OCR 원본)   │      │ (오류 보정됨)     │    │ (구조화됨)   │
└─────────────┘       └─────────────┘      └─────────────────┘    └─────────────┘
      ↓                       ↓                       ↓                    ↓
  ocr_extract.py       process_text.py      extract_item.py        최종 결과
                                              또는
                                          extract_item2.py
```

## 설치 및 설정

### 1. 필수 라이브러리 설치

```bash
pip install easyocr opencv-python pillow python-levenshtein
```

### 2. 폴더 구조 준비

```bash
# 입력 폴더 생성
mkdir images

# 영수증 이미지를 images/ 폴더에 복사
cp your_receipts/* images/
```

### 3. 사전 파일 준비

- `dictionary.txt`: 한글 단어 사전 (텍스트 후처리용)
- `dictionary_item.txt`: 메뉴 사전 (텍스트 후처리용)
- `dictionary_store.txt`: 가게 사전 (텍스트 후처리용)
- `dictionary_store_item.json`: 가게별 메뉴 사전 (개선된 추출용)

## 사용 방법

### 1. 전체 파이프라인 실행

```bash
python main.py
```

모든 단계를 순차적으로 실행하여 이미지에서 JSON까지 변환합니다.

### 2. 개별 모듈 실행

#### OCR 텍스트 추출

```bash
python ocr_extract.py
# 결과: images/*.jpg → output/ocr_raw_txt/*.txt
```

#### 텍스트 후처리

```bash
python process_text.py
# 결과: output/ocr_raw_txt/*.txt → output/ocr_processed_txt/*.txt
```

#### 메뉴 항목 추출 (기본 버전)

```bash
python extract_item.py
# 결과: output/ocr_processed_txt/*.txt → output/json/*.json
```

#### 메뉴 항목 추출 (개선된 버전)

```bash
python extract_item2.py
# 결과: output/ocr_processed_txt/*.txt → output/json/*.json
```

### 3. 사전 관리 도구

#### 메뉴 사전 관리

```bash
python dictionary_item.py
# 기능: 메뉴 아이템 사전 추가/수정/삭제
```

#### 가게 사전 관리

```bash
python dictionary_store.py
# 기능: 가게 정보 사전 추가/수정/삭제
```

## 추출 방법 비교

### extract_item.py (기본 버전)

- **방식**: 패턴 기반 추출
- **특징**: 메뉴명 + 단가 + 금액 패턴 인식
- **장점**: 빠른 처리 속도, 단순한 구조
- **단점**: OCR 오류에 취약, 복잡한 형식 처리 어려움

### extract_item2.py (개선된 버전)

- **방식**: 사전 기반 유사도 매칭
- **사전**: `dictionary_store_item.json` 사용
- **특징**:
  - 한글 자모 분해를 통한 유사도 계산
  - 가게별 메뉴 사전으로 정확도 향상
  - OCR 오류 보정 강화
- **장점**: 높은 정확도, 다양한 영수증 형식 지원
- **단점**: 상대적으로 느린 처리 속도

## 성능 비교 도구

### compare_accuracy.py

```bash
python compare_accuracy.py
```

- **기능**: 두 추출 방법의 정확도 비교
- **비교 항목**:
  - 가게명 매칭 정확도
  - 메뉴 항목 수 비교
  - 총 금액 정확도
  - 개별 메뉴 매칭률
- **출력**: 상세한 비교 리포트 생성

### compare_performance.py

```bash
python compare_performance.py
```

- **기능**: 두 추출 방법의 성능 비교
- **측정 항목**:
  - 처리 시간 비교
  - 메모리 사용량
  - 파일별 처리 속도
  - 전체 처리 효율성
- **출력**: 성능 벤치마크 결과

## 사전 관리 도구

### dictionary_item.py

- **기능**: 메뉴 아이템 사전 관리
- **주요 작업**:
  - 새로운 메뉴 아이템 추가
  - 기존 메뉴 아이템 수정
  - 메뉴 아이템 삭제
  - 사전 데이터 검증

### dictionary_store.py

- **기능**: 가게 정보 사전 관리
- **주요 작업**:
  - 새로운 가게 추가
  - 가게별 메뉴 목록 관리
  - 가게 정보 수정/삭제
  - 사전 구조 최적화

## 사전 파일 형식

### dictionary_store_item.json 구조

```json
{
  "stores": {
    "맥도날드": {
      "items": ["빅맥", "치킨맥너겟", "감자튀김", "코카콜라"]
    },
    "버거킹": {
      "items": ["와퍼", "치킨버거", "어니언링", "펩시콜라"]
    }
  }
}
```

## 출력 형식

### JSON 결과 예시

```json
{
  "filename": "receipt_001",
  "store_name": "맥도날드",
  "items": [
    {
      "menu": "빅맥",
      "price": "6900",
      "amount": "6900",
      "quantity": "1"
    },
    {
      "menu": "감자튀김",
      "price": "2500",
      "amount": "5000",
      "quantity": "2"
    }
  ],
  "total_amount": 11900
}
```

## 알려진 제한사항

- 손글씨 영수증은 인식률이 낮을 수 있습니다
- 복잡한 레이아웃의 영수증은 정확도가 떨어질 수 있습니다
- 사전에 없는 가게나 메뉴는 인식되지 않을 수 있습니다

## 개발 환경

- Python 3.8+
- EasyOCR 1.6+
- OpenCV 4.0+
- Levenshtein 0.20+

## 라이센스

MIT License
