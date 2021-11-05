# -*- coding: utf-8 -*- #인코딩 방식 설정
from jamo import h2j, j2hcj
from konlpy.tag import Okt
import re
class sep:

    def similiar(self, want_word, main_list): # API모듈의finder함수에서 받은 리스트 중에서 가장 유사도가 높은 단어를 가진 링크를 반환함 [[단어1, url],[단어2, url]] -> [[단어2, url]]
        greedy = 100
        return_list = [want_word, "NONE"] 
        if len(main_list) != 1:
            for i in main_list:
                word_list = i[0].split(',') 
                
                for j in word_list:
                    
                    j = re.sub(want_word,"",j) 
                    if len(j) == 0: 
                        return_list = i
                        return return_list
                    elif len(j) < greedy: 
                        greedy = len(want_word)
                        return_list = i
        else:
            return_list = main_list[0]
        return return_list
    
    def only_korean(self, str): #정규표현식을 이용해 한국어만 추출함
        a = ' '.join(re.compile('[|ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+').findall(str)).split()
        return a

    def clean(self, sentence): # 형태소를 분리하는 함수
        okt = Okt()
        
        circle = ['께', '으로', '으로서', '같이', '로', '게', '라고', '치고', '치고는', '에서', '으로', '로']
        number = ['이다', '다', '에게다', '야']
        big_gualho = ['이랑', '하고']

        clean_words = []
        for word in okt.pos(sentence, stem=True):   
            if word[1] in ["Josa"]:
                if word[1] in circle:
                    clean_words.append(f"{word[0]}①")
                elif word[0] in number:
                    clean_words.append(f"{word[0]}1")
                elif word[0] in big_gualho:
                    clean_words.append(f"{word[0]}[1]")
                elif word [0] == "만":
                    clean_words.append("만1①")
                elif word[0] == "에":
                    clean_words.append("에[1]①")
                else:
                    clean_words.append(word[0])
            elif word[1] not in ['Eomi', 'Punctuation'] and word[0] != "하다" and word[0] != "\n":
                word = re.sub("하다","",word[0])
                clean_words.append(word)
            
        result = clean_words
        print(result)
        return result

    def jamo_bunri(self, word): # 자음과 모음을 나눔 가->[ㄱ,ㅏ]
        result = j2hcj(h2j(word))
        return list(result)