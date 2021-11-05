import speech_recognition as sr

class stt:
    r = sr.Recognizer()
    r.energy_threshold = 100

    def __init__(self, respon = 100):
        self.respon = respon
        self.r.energy_threshold = respon
    
    def stt_live(self): # 마이크로 음성 입력 받기
        with sr.Microphone() as source:
            print("듣는중...")
            audio = self.r.listen(source)
            global result
        try: # 오류 무시: 잡음을 인식했을때 오류 코드가 떠 코드가 정지함.
            sentence = self.r.recognize_google(audio, language='ko-KR') # 문장 자르기
        except :
            print("?")
            return False

        try:
            return sentence
        except:
            print("??")