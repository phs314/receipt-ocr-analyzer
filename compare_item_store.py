import os
import Levenshtein

# 기존 TextPostProcessor 코드에서 가져온 핵심 기능만 추출
class WordSimilarityChecker:
    def __init__(self, dict_path="dictionary_item.txt"):
        self.dictionary = self.load_dictionary(dict_path)
        self.chosung_list = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
                             'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        self.jungsung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
                              'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
        self.jongsung_list = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
                              'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
                              'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    def load_dictionary(self, dict_path):
        if os.path.exists(dict_path):
            with open(dict_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        else:
            print(f"[오류] 사전 파일 없음: {dict_path}")
            return []

    def decompose(self, text):
        result = []
        for char in text:
            if '가' <= char <= '힣':
                code = ord(char) - ord('가')
                cho = code // (21 * 28)
                jung = (code % (21 * 28)) // 28
                jong = code % 28
                result.append(self.chosung_list[cho])
                result.append(self.jungsung_list[jung])
                if jong:
                    result.append(self.jongsung_list[jong])
            else:
                result.append(char)
        return ''.join(result)

    def calculate_similarity(self, word1, word2):
        jamo1 = self.decompose(word1)
        jamo2 = self.decompose(word2)
        if len(word1) <= 2 or len(word2) <= 2:
            return Levenshtein.jaro(jamo1, jamo2)
        else:
            return Levenshtein.ratio(jamo1, jamo2)

    def compare_with_dictionary(self, input_word, top_k=10):
        results = []
        for dict_word in self.dictionary:
            sim = self.calculate_similarity(input_word, dict_word)
            results.append((dict_word, sim))

        # 유사도 높은 순 정렬
        results.sort(key=lambda x: x[1], reverse=True)

        print(f"\n🔎 입력 단어: {input_word} → 유사도 Top {top_k} 결과:")
        for word, score in results[:top_k]:
            print(f"  - {word:10} | 유사도: {score:.4f}")


# 사용 예시
if __name__ == "__main__":
    checker = WordSimilarityChecker(dict_path="dictionary_item.txt")
    input_word = input("비교할 단어를 입력하세요: ")
    checker.compare_with_dictionary(input_word, top_k=10)