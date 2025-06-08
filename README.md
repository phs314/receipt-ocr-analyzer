# 영수증 OCR 분석기 (Receipt OCR Analyzer)

영수증 이미지에서 텍스트를 추출하고 메뉴 항목과 가격 정보를 구조화된 JSON 형태로 변환하는 도구입니다.

---

## 📁 폴더 및 파일 구조 (핵심)

```
receipt-ocr-analyzer/
│
├── 🔧 핵심 처리 모듈
│   ├── image_to_text.py           # 🖼️ 이미지 → 텍스트 (OCR)
│   ├── process_text.py            # 📝 OCR 텍스트 후처리
│   ├── extract_item.py            # 📄 패턴 기반 메뉴/가격 추출
│   └── extract_item2.py           # 📄 사전 기반(유사도) 메뉴/가격 추출
│
├── 📊 성능/유사도 비교 도구
│   ├── compare_item_store.py      # 🧩 단어 유사도(자모) 비교 도구 (콘솔)
│   └── compare_jamo_console.py    # 🧩 자모 기반 유사도 분석 및 CSV 리포트
│
├── 📝 사전 파일
│   ├── dictionary.txt             # 📚 한글 단어 사전
│   ├── dictionary_item.txt        # 📚 메뉴 사전
│   ├── dictionary_store.txt       # 📚 가게 사전
│   └── dictionary_store_item.json # 📚 가게별 메뉴 사전 (extract_item2용)
│
├── 📁 입력 폴더
│   └── input/                     # 📥 (추가 입력 데이터 폴더, 필요시)
│
└── 📁 출력 폴더
    └── output/
        ├── ocr_raw_txt/           # 📄 OCR 원본 텍스트
        ├── ocr_processed_txt/     # 📝 후처리된 텍스트
        ├── ocr_vis/               # 👁️ OCR 시각화 결과
        └── json/                  # 📋 최종 JSON 결과
```

---

## ⚡ 데이터 흐름

```
📂 images/         ➡️  📄 ocr_raw_txt/   ➡️  📝 ocr_processed_txt/   ➡️  📋 json/
┌──────────────┐   ┌───────────────┐   ┌────────────────────┐   ┌──────────────┐
│ receipt.jpg  │ → │ receipt.txt   │ → │ receipt_proc.txt   │ → │ receipt.json │
│ receipt.png  │   │ (OCR 원본)    │   │ (오류 보정됨)      │   │ (구조화됨)   │
└──────────────┘   └───────────────┘   └────────────────────┘   └──────────────┘
       │                  │                     │                      │
       │     image_to_text.py         process_text.py         extract_item.py
       │                                                    또는
       │                                                extract_item2.py
```

---

## 🛠️ 사용 방법

1. **OCR 텍스트 추출**

   ```bash
   python image_to_text.py
   # images/ → output/ocr_raw_txt/
   ```

2. **텍스트 후처리**

   ```bash
   python process_text.py
   # output/ocr_raw_txt/ → output/ocr_processed_txt/
   ```

3. **메뉴/가격 정보 추출**

   - 패턴 기반:
     ```bash
     python extract_item.py
     # output/ocr_processed_txt/ → output/json/
     ```
   - 사전(유사도) 기반:
     ```bash
     python extract_item2.py
     # output/ocr_processed_txt/ → output/json/
     ```

4. **단어 유사도 비교 도구 (콘솔)**

   ```bash
   python compare_item_store.py
   # 입력한 단어와 메뉴 사전(dictionary_item.txt) 내 단어 유사도 비교
   ```

5. **자모 기반 유사도 분석 및 리포트(CSV)**
   ```bash
   python compare_jamo_console.py
   # output/ocr_raw_txt/ 내 단어의 유사도 분석 결과를 CSV로 저장
   ```

---

## 📚 주요 사전 파일

- `dictionary.txt` : 한글 단어 사전 (후처리용)
- `dictionary_item.txt` : 메뉴명 사전 (유사도 비교용)
- `dictionary_store.txt` : 가게명 사전
- `dictionary_store_item.json` : 가게별 메뉴 사전 (extract_item2.py에서 사용)

---

## ⚠️ 참고

- 입력 이미지는 `input/` 폴더에 넣어주세요.
- 출력 결과는 `output/` 폴더 하위에 생성됩니다.
- 사전 파일이 없으면 일부 기능이 동작하지 않을 수 있습니다.

---

## 라이선스

MIT License
