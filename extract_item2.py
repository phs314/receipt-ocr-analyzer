import re
import math
import os
import json
from process_text import TextPostProcessor

def normalize_number(text):
    if not text:
        return text
    text = re.sub(r'O', '0', text)  # O를 0으로 변환 (OCR 오류 보정)
    text = re.sub(r'[,.\s]', '', text)  # 콤마, 점, 공백 제거
    return text

def is_number_format(text):
    """텍스트가 숫자 형식인지 확인"""
    try:
        int(normalize_number(text))
        return True
    except ValueError:
        return False

def extract_numbers_from_line(words):
    """줄에서 숫자 형식의 단어들을 추출"""
    numbers = []
    for word in words:
        if is_number_format(word):
            try:
                numbers.append(int(normalize_number(word)))
            except ValueError:
                continue
    return numbers

def extract_menu_items(txt_path):
    """
    사전 기반 유사도 매칭을 사용한 메뉴 항목 추출
    TextPostProcessor를 사용해서 dictionary_store_item.json 로드
    """
    # JSON 사전 파일을 사용하는 TextPostProcessor 생성
    dict_path = os.path.join(os.path.dirname(__file__), 'dictionary_store_item.json')
    processor = TextPostProcessor(dict_path=dict_path)
    
    # 텍스트 파일 읽기
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 줄별로 정리
    lines = [line.strip() for line in lines if line.strip()]
    
    menu_items = []
    store_name = None
    store_found = False
    last_successful_line = -1  # 마지막으로 성공적으로 메뉴가 추가된 줄 번호
    
    # 1) 맨 위부터 읽으면서 가게명 찾기
    for i, line in enumerate(lines):
        if not store_found:
            # 2) 가게명과 유사도 검사
            # 전체 줄에서 가게명 매칭 시도
            match, score = processor.find_best_store_match(line)
            if match:
                store_name = match
                store_found = True
                print(f"🏪 가게명 발견: {line} → {match} (유사도: {score:.2f})")
                break
            
            # 단어별로도 시도
            words = line.split()
            for word in words:
                match, score = processor.find_best_store_match(word)
                if match:
                    store_name = match
                    store_found = True
                    print(f"🏪 가게명 발견: {word} → {match} (유사도: {score:.2f})")
                    break
            
            if store_found:
                break
    
    # 3) 가게명을 찾았다면, 이후 다시 txt를 읽어서 메뉴 항목 찾기
    if store_found and store_name:
        for i, line in enumerate(lines):
            words = line.split()
            if len(words) == 0:
                continue
            print(f"📄 [{i}] 현재 줄: '{line}'")
            
            # 연속성 체크: 첫 번째 메뉴가 아니고 이전 성공 줄과 너무 멀면 중단
            if last_successful_line != -1 and i > last_successful_line + 2:
                break
            
            # 4) 첫 번째 단어부터 시작해서 누적적으로 확장하며 최고 유사도 찾기
            best_match = None
            best_score = 0
            best_end_index = -1
            best_test_phrase = None  # 실제 매칭된 구문 저장
            
            # 첫 번째 단어부터만 시작
            for k in range(0, len(words)):
                # 0부터 k까지의 단어들을 합침
                if k == 0:
                    # 첫 번째 단어만
                    test_phrase = words[0]
                else:
                    # 여러 단어를 띄어쓰기로 연결
                    test_phrase = " ".join(words[0:k+1])
                
                # 메뉴 사전과 비교
                match, score = processor.find_best_item_match(test_phrase, store_name)
                
                if match and score > best_score:
                    best_match = match
                    best_score = score
                    best_end_index = k
                    best_test_phrase = test_phrase  # 실제 매칭된 구문 저장
                
                # 숫자가 나타나면 더 이상 확장하지 않음
                if k < len(words) - 1 and is_number_format(words[k+1]):
                    break
            
            # 최고 매칭이 있다면 처리
            if best_match and best_score >= 0.4:  # 임계값
                # 매칭된 부분 다음부터 숫자 추출
                remaining_words = words[best_end_index + 1:]
                numbers = extract_numbers_from_line(remaining_words)
                
                menu_added = False
                
                if len(numbers) == 1:
                    # 4.1) 숫자 하나: 총액 = 개당 가격
                    total_amount = numbers[0]
                    unit_price = total_amount
                    quantity = 1
                    
                    menu_items.append({
                        "menu": best_match,
                        "price": str(unit_price),
                        "amount": str(total_amount),
                        "quantity": str(quantity)
                    })
                    print(f"🍔 메뉴 발견: {best_test_phrase} → {best_match} (유사도: {best_score:.2f})")
                    print(f"   → 개당: {unit_price}원, 개수: {quantity}개, 총액: {total_amount}원")
                    menu_added = True
                    
                elif len(numbers) == 2:
                    # 4.2) 숫자 두개: 첫번째=개당가격, 두번째=총액
                    unit_price = numbers[0]
                    total_amount = numbers[1]
                    quantity = total_amount // unit_price if unit_price > 0 else 1
                    
                    menu_items.append({
                        "menu": best_match,
                        "price": str(unit_price),
                        "amount": str(total_amount),
                        "quantity": str(quantity)
                    })
                    print(f"🍔 메뉴 발견: {best_test_phrase} → {best_match} (유사도: {best_score:.2f})")
                    print(f"   → 개당: {unit_price}원, 개수: {quantity}개, 총액: {total_amount}원")
                    menu_added = True
                    
                elif len(numbers) >= 3:
                    # 4.3) 숫자 세개 이상: 첫번째=개당가격, 두번째=개수, 세번째=총액
                    unit_price = numbers[0]
                    quantity = numbers[1]
                    total_amount = numbers[2]
                    
                    menu_items.append({
                        "menu": best_match,
                        "price": str(unit_price),
                        "amount": str(total_amount),
                        "quantity": str(quantity)
                    })
                    print(f"🍔 메뉴 발견: {best_test_phrase} → {best_match} (유사도: {best_score:.2f})")
                    print(f"   → 개당: {unit_price}원, 개수: {quantity}개, 총액: {total_amount}원")
                    menu_added = True
                
                # 메뉴가 성공적으로 추가되었으면 마지막 성공 줄 번호 업데이트
                if menu_added:
                    last_successful_line = i
    
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