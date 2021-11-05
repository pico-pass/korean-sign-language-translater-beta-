# -*- coding: utf-8 -*- #인코딩 방식 설정
import sys
import threading
from PyQt5 import QtCore
from API import make_driver
import API
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor
from Ui_testui import Ui_MainWindow
import stt as STT
import sep as Sep
import os

# 기능 불러오기
sep =Sep.sep()
stt = STT.stt(500)  #stt
driver = make_driver()
as_driver = make_driver()
Call = API.video(driver)
as_Call = API.video(as_driver)

class MainWindow(QMainWindow): # 메인 GUI 클래스
    # 시그널 설정
    gui_signal = pyqtSignal(str)
    switch_signal = pyqtSignal(bool)
    pin = True

    def __init__(self): # GUI 초기화 설정
        # GUI 초기화
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 버튼에 기능 연결
        self.ui.start_btn.clicked.connect(self.startbtn)
        self.ui.quit_btn.clicked.connect(self.quitbtn)
        self.ui.btn_close.clicked.connect(self.quitbtn)
        self.ui.btn_maximize.clicked.connect(lambda: self.showMinimized())
        self.ui.op_slide.setRange(20,100)
        self.ui.op_slide.setValue(100) 
        self.ui.op_slide.valueChanged.connect(self.opacitychange)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.ui.pin_button.clicked.connect(self.btnpin)
        self.ui.return_btn.clicked.connect(self.returnbtn)
        self.ui.full_size_quit_btn.clicked.connect(self.zoomminus)

        # GUI 추가 설정
        vbox = QVBoxLayout()
        sizegrip = QSizeGrip(self)
        vbox.addWidget(sizegrip, 4)
        
        # GUI와 쓰레드 연결
        self.th = Searcher(parent=self)
        self.gui_signal.connect(self.th.main)
        self.th.thread_signal.connect(self.show_web)

        # GUI 킴
        self.show()

    def show_web(self, url):
        self.ui.webvideo.setUrl(QUrl(url))
        
    def startbtn(self): # Translate Start 버튼 눌렸을 때 실행될 기능
        Searcher.rope = True
        self.ui.stackedWindow.setCurrentWidget(self.ui.page_credits)
        combo = self.ui.text_translate.toPlainText()
        self.gui_signal.emit(combo)     
        self.th.playing = True

    def quitbtn(self): # 프로그램 종료 시의 기능
        QCoreApplication.instance().quit()
        as_driver.quit()
        driver.quit()
        os.system("taskkill /f /im chromedriver.exe /t")

    def opacitychange(self): # 투명도 조절(블랜딩) 기능
        self.setWindowOpacity(float(self.ui.op_slide.value())/100)

    def btnpin(self): # 상단 고정 기능
        on = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not on)
        self.show()

    def mousePressEvent(self, event): # 창에 마우스가 눌렸을 때 커서가 표시되는 기능
        try:
            if event.button()==Qt.LeftButton:
                self.m_flag=True
                self.m_Position=event.globalPos()-self.pos() #Get the position of the mouse relative to the window
                event.accept()
                self.setCursor(QCursor(Qt.OpenHandCursor))  #Change mouse icon
        except AttributeError:
            pass

    def mouseMoveEvent(self, QMouseEvent): # 마우스로 창을 이동시키는 기능
        try:
            if Qt.LeftButton and self.m_flag:  
                self.move(QMouseEvent.globalPos()-self.m_Position) # Change window position
                QMouseEvent.accept()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, QMouseEvent): # 마우스를 뗐을 때 기능
        try:
            self.m_flag=False
            self.setCursor(QCursor(Qt.ArrowCursor))
        except AttributeError:
            pass
    
    def returnbtn(self): # 돌아가기 버튼 기능
        self.ui.stackedWindow.setCurrentWidget(self.ui.page_home)
        self.gui_signal
        self.th.playing = False
    
    def zoomminus(self): # 최소화 기능
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

class Searcher(QThread): # 쓰레드 클래스
    thread_signal = pyqtSignal(str) # 쓰레드에서 발신할 시그널
    def __init__(self, parent=None): # 쓰레드 초기화
        super().__init__()
        self.playing = True

    def Qsleep(self, time = 4): # 쓰레드 내에서 딜레이를 주기위한 기능
        time = time * 1000
        loop = QEventLoop()
        QTimer.singleShot(time, loop.quit) #msec
        loop.exec_()

    def make_one_url(self, word): # 입력받은 2차원 리스트에서 가장 적절한 링크 반환
        print(f"입력받은 단어: {word}")
        url = Call.finder(word)
        url = sep.similiar(word, url)
        print(url)  
        return url[1]

    def main(self, combo): # 마이크 녹음, 문자열 자르기 등 메인GUI에서 모두 처리하기 어려운 작업들
        while self.playing:
            if len(combo) == 0:
                word = stt.stt_live() # 녹음한 단어를 word에 저장
            else:
                word = combo

            self.origin_word = word
            if word == 0:
                pass
            else: # 문자열 처리
                word = sep.clean(word) # 문장을 형태소 형태로 분리한 후 리스트 형식으로 정리
                print(word)
                for i in word:
                    url = self.make_one_url(i)
                    if url != 'NONE':
                        video_len = as_Call.getlength(url)
                    
                    if url == 'NONE' or video_len>60: # url이 없거나 영상 길이가 1분 초과일 경우
                        word = sep.jamo_bunri(i)
                        for i in word:
                            i = sep.only_korean(i)[0]
                            url = self.make_one_url(i)
                            
                            self.thread_signal.emit(url)  # 쓰레드 시그널로 url 발신(지문자)
                            
                            video_len = as_Call.getlength(url) # 영상 길이 출력
                            if video_len > 10:
                                video_len /= 3
                            self.Qsleep(video_len) # 영상 길이만큼 대기
                    else:
                        self.thread_signal.emit(url) # 쓰레드 시그널로 url 발신(단어 형태의 수어)
                        if video_len > 10:
                            video_len /= 2
                        self.Qsleep(video_len) # 영상 길이만큼 대기
            if len(combo) != 0:
                while True:
                    if self.origin_word == word:
                        self.Qsleep(1)
                        continue
                    else:
                        break

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()