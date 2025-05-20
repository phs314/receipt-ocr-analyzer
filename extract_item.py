import os
import re
import json
import math

"""
영수증 텍스트 처리 후 메뉴 항목 추출 모듈
- 영수증 텍스트에서 가게명, 메뉴 항목, 가격 정보 추출
- 추출된 정보를 JSON 형태로 구조화하여 저장
"""

def normalize_number(text):
    if not text:
        return text
    
    text = re.sub(r'O', '0', text)  # O를 0으로 변환 (OCR 오류 보정)
    text = re.sub(r'[,.\s]', '', text)  # 콤마, 점, 공백 제거
    
    return text

def is_price_format(text):
    return bool(re.match(r'^[\d,]+$', text))  # 숫자와 콤마만 포함하는지 확인

def is_text_format(text):
    # 한글/영문이 포함되고 숫자는 없는지 확인
    return bool(re.search(r'[가-힣a-zA-Z]', text)) and not bool(re.search(r'\d', text))

def extract_menu_items(txt_path):
    menu_items = []
    store_name = None
    started_processing_menu = False  # 메뉴 처리 시작 여부 플래그
    
    # 텍스트 파일 읽기
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 첫 줄은 가게명으로 처리
    if lines and lines[0].strip():
        store_name = lines[0].strip()
    
    # 두 번째 줄부터 메뉴 항목 추출
    for line in lines[1:]:
        line = line.strip()
        if not line:  # 빈 줄 건너뛰기
            continue
        
        words = line.split()
        
        # 메뉴 패턴: 메뉴명 + 단가 + 금액
        is_menu_pattern = (len(words) >= 3 and 
                          is_price_format(words[-1]) and  # 마지막 단어: 금액
                          is_price_format(words[-2]))     # 끝에서 두 번째: 단가
        
        if is_menu_pattern:
            # 메뉴 처리 시작
            if not started_processing_menu:
                started_processing_menu = True
            
            # 메뉴명 추출 (마지막 두 단어 제외한 모든 텍스트)
            menu_name = ' '.join(words[:-2])
            price = words[-2]  # 단가
            amount = words[-1]  # 금액
            
            try:
                # 숫자로 변환 (콤마 제거)
                price_int = int(normalize_number(price))
                amount_int = int(normalize_number(amount))
                
                # 금액이 단가보다 작으면 조정 (OCR 오류로 가정)
                if amount_int < price_int:
                    amount_int = price_int
                
                # 수량 계산 및 조정
                if price_int > 0:
                    quantity = amount_int / price_int
                    # 소수점 수량은 올림 처리 (ex: 1.2개 → 2개)
                    if quantity != int(quantity):
                        quantity = math.ceil(quantity)
                        price_int = int(amount_int / quantity)  # 단가 재계산
                else:
                    quantity = 1
                    price_int = amount_int
                
                # 메뉴 항목 추가
                menu_items.append({
                    "menu": menu_name,
                    "price": str(price_int),
                    "amount": str(amount_int),
                    "quantity": str(int(quantity))
                })
            except ValueError:
                pass  # 숫자 변환 실패 시 무시
        
        # 메뉴 패턴 끊김 감지 (영수증 하단 정보 등)
        elif started_processing_menu:
            break  # 메뉴 목록이 끝났다고 판단
    
    return store_name, menu_items

def process_txt_files(input_dir, output_dir):
    # 출력 폴더 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    processed_count = 0
    total_count = 0
    
    # 모든 텍스트 파일 처리
    for filename in os.listdir(input_dir):
        if not filename.endswith('.txt'):  # txt 파일만 처리
            continue
            
        total_count += 1
        txt_path = os.path.join(input_dir, filename)
        
        # 결과 파일명 생성
        base_name = os.path.splitext(filename)[0]
        if base_name.endswith("_processed"):
            base_name = base_name[:-10]  # "_processed" 제거
            
        json_path = os.path.join(output_dir, f"{base_name}.json")
        
        print(f"\n처리 중: {filename}")
        
        # 메뉴 정보 추출
        store_name, menu_items = extract_menu_items(txt_path)
        
        # 메뉴 항목이 있는 경우만 JSON 생성
        if menu_items:
            # 총 금액 계산
            try:
                total_amount = sum(int(item["amount"]) for item in menu_items)  # 모든 메뉴 금액 합
            except:
                total_amount = 0
            
            # JSON 객체 생성
            receipt_data = {
                "filename": base_name,
                "store_name": store_name,
                "items": menu_items,
                "total_amount": total_amount
            }
            
            # JSON 파일 저장
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(receipt_data, f, ensure_ascii=False, indent=2)  # 한글 저장
            
            # 결과 출력
            print(f"✅ 가게명: {store_name}")
            print(f"✅ 메뉴 항목: {len(menu_items)}개")
            for item in menu_items:
                print(f"  - {item['menu']}: {item['price']}원 x {item['quantity']}개 = {item['amount']}원")
            print(f"✅ JSON 저장 완료: {json_path}")
            
            processed_count += 1
        else:
            print(f"❌ 메뉴 항목 없음: {filename}")  # 메뉴를 찾지 못함
    
    print(f"\n처리 완료: {processed_count}/{total_count} 파일 처리됨")

if __name__ == "__main__":
    # 경로 설정
    output_dir = "output"
    input_dir = os.path.join(output_dir, "ocr_processed_txt")  # 처리된 OCR 텍스트 폴더
    json_output_dir = os.path.join(output_dir, "json")  # JSON 출력 폴더
    
    print(f"'{input_dir}' 폴더의 텍스트 파일에서 메뉴 항목 추출 시작...")
    process_txt_files(input_dir, json_output_dir)
    print(f"\n처리 완료. 결과는 '{json_output_dir}' 폴더에 저장됨")
