import os
import re
import csv
from Levenshtein import ratio, distance, jaro

# ✅ 설정값
THRESHOLD = 0.70
dictionary_path = "dictionary.txt"
input_dir = "output/ocr_raw_txt"
output_csv = "ocr_word_similarity_report.csv"

# ✅ 사용자 정의 사전 로드
with open(dictionary_path, "r", encoding="utf-8") as f:
    dictionary = [line.strip() for line in f if line.strip()]

# ✅ 자모 분해 함수
CHOSUNG_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNGSUNG_LIST = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONGSUNG_LIST = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
                 'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

def decompose_hangul(text):
    result = []
    for char in text:
        if '가' <= char <= '힣':
            code = ord(char) - ord('가')
            cho = code // (21 * 28)
            jung = (code % (21 * 28)) // 28
            jong = code % 28
            result.extend([CHOSUNG_LIST[cho], JUNGSUNG_LIST[jung]])
            if jong:
                result.append(JONGSUNG_LIST[jong])
        else:
            result.append(char)
    return ''.join(result)

def best_match(word, candidates, use_jamo=False, threshold=0.7):
    transform = decompose_hangul if use_jamo else (lambda x: x)
    word_trans = transform(word)
    best = {"ratio": ("", 0.0), "jaro": ("", 0.0), "distance": ("", 0.0)}

    for cand in candidates:
        cand_trans = transform(cand)
        if not cand_trans or not word_trans:
            continue
        try:
            r = ratio(word_trans, cand_trans)
            j = jaro(word_trans, cand_trans)
            d = 1 - distance(word_trans, cand_trans) / max(len(word_trans), len(cand_trans))
        except ZeroDivisionError:
            continue

        if r >= threshold and r > best["ratio"][1]:
            best["ratio"] = (cand, r)
        if j >= threshold and j > best["jaro"][1]:
            best["jaro"] = (cand, j)
        if d >= threshold and d > best["distance"][1]:
            best["distance"] = (cand, d)
    return best

# ✅ 파일 처리 및 CSV 저장
rows = []
for filename in os.listdir(input_dir):
    if not filename.endswith(".txt"):
        continue
    with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        words = re.findall(r'[가-힣]{2,}', line)
        for word in words:
            if word in dictionary:
                continue
            plain = best_match(word, dictionary, use_jamo=False, threshold=THRESHOLD)
            jamo = best_match(word, dictionary, use_jamo=True, threshold=THRESHOLD)
            rows.append({
                "파일명": filename,
                "원본 단어": word,
                "ratio(plain)_교정": plain["ratio"][0], "ratio(plain)_유사도": plain["ratio"][1],
                "ratio(jamo)_교정": jamo["ratio"][0], "ratio(jamo)_유사도": jamo["ratio"][1],
                "jaro(plain)_교정": plain["jaro"][0], "jaro(plain)_유사도": plain["jaro"][1],
                "jaro(jamo)_교정": jamo["jaro"][0], "jaro(jamo)_유사도": jamo["jaro"][1],
                "distance(plain)_교정": plain["distance"][0], "distance(plain)_유사도": plain["distance"][1],
                "distance(jamo)_교정": jamo["distance"][0], "distance(jamo)_유사도": jamo["distance"][1]
            })

# ✅ CSV 저장
fieldnames = list(rows[0].keys()) if rows else []
with open(output_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(f"✅ 저장 완료: {output_csv}")