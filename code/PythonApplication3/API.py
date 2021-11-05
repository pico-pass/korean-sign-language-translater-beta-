from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller
import re

def make_driver(headless = True): # 크롬 드라이버를 만듬 False: 드라이버 창을 띄움 True: 드라이버가 백그라운드로 돌아감
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument('allow-insecure-localhost')
    #options.add_argument('no-sandbox')
    #options.add_argument('ignore-certificate-errors')
    if headless:
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get('https://sldict.korean.go.kr/front/main/opinionSend.do?r_type=1')

    return driver

class video:
    def __init__(self, driver):# 드라이버 인자를 받음
        self.driver = driver

    def finder(self, val, check_count = -1):# val로 받은 단어를 검색하여 검색한 모든 결과를 2차원 리스트로 반환[[단어, url],[단어, url]]
        self.driver.find_element_by_class_name('n_input').clear()
        self.driver.find_element_by_class_name('n_input').send_keys(val)
        self.driver.find_element_by_class_name('n_btn_search').click()

        all = "/html/body/div[2]/div[2]/div/div[1]/div[4]/div[2]/ul/li[1]/a"
        all = self.driver.find_element_by_xpath(all).text # 검색했을시 나오는 모든 항목의 갯수
        
        curlture = "/html/body/div[2]/div[2]/div/div[1]/div[4]/div[2]/ul/li[4]/a"
        curlture = self.driver.find_element_by_xpath(curlture).text # 불필요한 문화 정보 수어의 갯수

        print(f"총 조회된 수어의 갯수:{all}")
        
        return_list = []
        # 이하의 for과 while은 이중 루프로 for는 일상생활 수어, 전문용어 수어 파트로 들어가고 while은 각 파트에 있는 동영상을 조회함
        try: 
            for big in [3, 6]:
                small = 1
                
                while len(return_list) <= check_count or check_count == -1:
                    try:
                        jpg_xpath = f'/html/body/div[2]/div[2]/div/div[1]/div[4]/div[3]/div[{big}]/ul/li[{small}]/div[1]/div/a/img[2]'
                        txt_xpath = f'/html/body/div[2]/div[2]/div/div[1]/div[4]/div[3]/div[{big}]/ul/li[{small}]/div[2]/div/ul/li/div/p/span[1]/a'

                        txt = self.driver.find_element_by_xpath(txt_xpath).text # 동영상의 제목을 조회하여 얻음
                        jpg = self.driver.find_element_by_xpath(jpg_xpath).get_attribute("src")
                        jpg = re.sub("215X161.jpg","",jpg)
                        jpg += '700X466.webm' # 동영상의 링크를 조회하여 얻음
                        
                        return_list.append([txt, jpg])
                        small += 1

                    except NoSuchElementException:
                        break

        except NoSuchElementException:
            pass
        if len(return_list) == 0: # 만약 조회된 동영상이 없다면
            return_list = [[val, "NONE"]]
        return return_list

    def getlength(self, url):# 동영상의 길이를 얻음
        self.driver.get(url)
        sec = None
        while sec == None:
            sec = self.driver.execute_script("return document.getElementsByName('media')[0].duration")
        return sec