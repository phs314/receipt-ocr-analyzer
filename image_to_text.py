import os
import easyocr
from PIL import Image, ImageDraw, ImageFont
import re

"""
영수증 이미지에서 텍스트 추출 모듈
- EasyOCR을 사용하여 이미지에서 텍스트 인식
- 인식된 텍스트를 원본 이미지 위치에 시각화
- 인식된 텍스트를 줄 단위로 그룹화하여 저장
"""

# 폴더 경로 설정
INPUT_IMAGE_PATH = "input"  # 원본 이미지 폴더
OUTPUT_DIR = "output"       # 출력 상위 폴더
OCR_VIS_PATH = os.path.join(OUTPUT_DIR, "ocr_vis")           # 시각화 이미지 저장 폴더
OCR_RAW_TXT_PATH = os.path.join(OUTPUT_DIR, "ocr_raw_txt")   # OCR 원본 텍스트 폴더
JSON_PATH = os.path.join(OUTPUT_DIR, "json")                 # JSON 파일 저장 폴더

# 폰트 설정
font_size = 20
font = ImageFont.truetype("GmarketSansTTFLight.ttf", font_size, encoding="UTF-8")

# EasyOCR 모델 전역 초기화
print("EasyOCR 모델 로드 중...")
reader = easyocr.Reader(['en', 'ko'], gpu=False)  # 한글/영어 인식, CPU 사용
print("EasyOCR 모델 로드 완료")

def create_output_directories():
    for path in [INPUT_IMAGE_PATH, OUTPUT_DIR, OCR_VIS_PATH, OCR_RAW_TXT_PATH, JSON_PATH]:
        if not os.path.exists(path):
            os.makedirs(path)  # 없는 폴더 생성
            print(f"'{path}' 폴더가 생성되었습니다.")

def draw_text_on_original_location(img_draw, bbox, text, font):
    try:
        tl, tr, br, bl = bbox  # 좌상, 우상, 우하, 좌하 좌표
        
        # 텍스트 크기 계산 (PIL 최신 버전만 사용)
        bbox_text = font.getbbox(text)
        text_width = bbox_text[2] - bbox_text[0]
        text_height = bbox_text[3] - bbox_text[1]
        
        # 경계 상자 크기 계산
        box_width = max(tr[0], br[0]) - min(tl[0], bl[0])
        box_height = max(bl[1], br[1]) - min(tl[1], tr[1])
        
        # 폰트 크기 자동 조정
        adjusted_font = font
        scale_factor = min(box_width / max(text_width, 1), box_height / max(text_height, 1))
        if scale_factor < 1:  # 경계 상자보다 텍스트가 큰 경우
            adjusted_font_size = max(int(font_size * scale_factor * 0.9), 10)  # 최소 10pt
            adjusted_font = ImageFont.truetype("GmarketSansTTFLight.ttf", adjusted_font_size, encoding="UTF-8")
            
            # 크기 재계산 (최신 버전만 사용)
            bbox_text = adjusted_font.getbbox(text)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
        
        # 텍스트 위치 계산 (중앙 정렬)
        x_center = (min(tl[0], bl[0]) + max(tr[0], br[0])) // 2
        y_center = (min(tl[1], tr[1]) + max(bl[1], br[1])) // 2
        x = x_center - text_width // 2
        y = y_center - text_height // 2
        
        # 텍스트 그리기 (RGB/흑백 이미지 호환)
        fill_color = (255, 0, 0) if img_draw._image.mode in ['RGB', 'RGBA'] else 255
        img_draw.text((x, y), text, font=adjusted_font, fill=fill_color)
    except Exception as e:
        print(f"텍스트 그리기 오류: {e} (텍스트: {text})")  # 오류 상세 정보 출력

def group_by_y_coordinates(result, threshold=15):
    if not result:
        return []
    
    # Y 좌표 중앙값 계산
    def get_y_center(item):
        bbox = item[0]
        y_values = [point[1] for point in bbox]
        return sum(y_values) / len(y_values)  # Y 좌표 평균
    
    sorted_result = sorted(result, key=get_y_center)  # Y 좌표로 정렬
    
    # 같은 줄 텍스트 그룹화
    groups = []
    current_group = [sorted_result[0]]
    current_y = get_y_center(sorted_result[0])
    
    for item in sorted_result[1:]:
        y_center = get_y_center(item)
        if abs(y_center - current_y) <= threshold:  # 같은 줄로 간주할 Y 차이 임계값
            current_group.append(item)
        else:
            groups.append(current_group)  # 현재 그룹 저장
            current_group = [item]  # 새 그룹 시작
            current_y = y_center  # Y 기준점 갱신
    
    if current_group:  # 마지막 그룹 추가
        groups.append(current_group)
    
    return groups

def save_text_with_groups(filepath, grouped_result):
    lines = []
    
    for group in grouped_result:
        # X 좌표로 정렬 (왼쪽→오른쪽 순)
        sorted_group = sorted(group, key=lambda x: min(point[0] for point in x[0]))
        line_text = " ".join(item[1] for item in sorted_group)  # 그룹 내 텍스트 합치기
        line_text = re.sub(r'\b\d{10,}\b', '', line_text)  # 바코드 등 긴 숫자 제거
        lines.append(line_text)
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip():  # 빈 줄은 저장하지 않음
                f.write(f"{line}\n")

def process_single_image(image_path):
    try:
        result = reader.readtext(image_path)  # OCR 수행
        
        if not result:
            print(f"텍스트 없음: {image_path}")
            return []
        
        # 이미지 처리
        img = Image.open(image_path)
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')  # 흑백 이미지를 RGB로 변환
        draw = ImageDraw.Draw(img)
        
        # 인식된 텍스트 시각화
        for bbox, text_data, _ in result:
            if text_data.strip():  # 공백 텍스트 제외
                draw_text_on_original_location(draw, bbox, text_data, font)
        
        # 파일명 처리
        base_filename = os.path.basename(image_path)
        filename_without_ext = os.path.splitext(base_filename)[0]
        
        # 시각화 이미지 저장
        result_img_path = os.path.join(OCR_VIS_PATH, f"{filename_without_ext}_vis.png")
        img.save(result_img_path)
        
        # 인식된 텍스트 저장
        txt_path = os.path.join(OCR_RAW_TXT_PATH, f"{filename_without_ext}_raw.txt")
        grouped_result = group_by_y_coordinates(result)  # 텍스트 줄 단위 그룹화
        save_text_with_groups(txt_path, grouped_result)  # 텍스트 파일로 저장
        
        return result
    except Exception as e:
        print(f"처리 실패: {e}")
        return []

def main():
    print("EasyOCR 텍스트 인식 시작...")
    
    # 출력 디렉토리 생성
    create_output_directories()
    
    # 처리할 이미지 목록 가져오기
    image_files = [f for f in os.listdir(INPUT_IMAGE_PATH) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    
    if not image_files:
        print(f"'{INPUT_IMAGE_PATH}' 폴더에 이미지 없음")
        return
    
    # 이미지 순차 처리
    success_count = 0
    total_count = len(image_files)
    
    print(f"총 {total_count}개 이미지 처리 예정")
    
    for idx, image in enumerate(image_files, 1):
        try:
            image_path = os.path.join(INPUT_IMAGE_PATH, image)
            print(f"\n처리 중: {image} [{idx}/{total_count}]")
            
            if process_single_image(image_path):  # OCR 성공 시
                success_count += 1
                print(f"성공: {image}")
            else:
                print(f"실패: {image}")  # 인식된 텍스트 없음
        except Exception as e:
            print(f"오류: {e}")  # 처리 중 예외 발생
    
    print(f"\n완료: {success_count}/{total_count} 성공")

if __name__ == "__main__":
    main()