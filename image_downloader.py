import sys
from time import sleep
import lxml.html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import os
import requests
import json
LOGIN = '89202600211'
PASSWORD = 'asd456zxc123asd456zxc123'

def login(driver):
    global LOGIN,PASSWORD
    driver.get('https://vk.com/')
    sleep(2)
    driver.find_element_by_xpath('//*[@id="index_email"]').send_keys(LOGIN)    
    driver.find_element_by_xpath('//*[@id="index_pass"]').send_keys(PASSWORD)
    driver.find_element_by_xpath('//*[@id="index_login_button"]').click()
    print('Authorized')
    sleep(1)


def init_driver():
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    #exec_path = f"{os.getcwd()}/chromedriver"
    exec_path = 'chromedriver.exe'
    driver = webdriver.Chrome(executable_path=exec_path,
                              chrome_options=chrome_options)
    try:
        login(driver)
    except:
        print('Problems with auth')
    return driver

def usage():
    print('There must be names of files')



def get_image_url(url,driver):
    driver.get(url)
    #sleep(2)
    for i in range(5):
        try:
            source_html = driver.find_element_by_xpath('//*[@id="pv_photo"]').get_attribute('innerHTML')
        except:
            sleep(0.2)
            continue
        break
    try:
        source_url = source_html[source_html.find('<img src="')+10:source_html.find('" style')]
        return source_url
    except:
        return False


def save_image(source,path_name):
    #print(source)
    name = os.path.basename(source)
    #print(name)
    image = requests.get(source)
    #print(image.code)
    image_f = open(path_name+'\\'+name,'wb')
    image_f.write(image.content)
    image_f.close()

    
def main(targets = None):
    if targets == None:
        try:
            targets = sys.argv[1:]
        except:
           usage()
           return 1
        number_of_targets = len(targets)
    else:
        number_of_targets = len(targets)
        
    print('Working on '+str(number_of_targets)+' targets')
    browser = init_driver()
    for target in targets:
        try:
            file = open(target,'r')
        except:
            print(target, 'can`t open file')
            continue
        
        newpath = '.\\'+target[0:target.find('.')] 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            
        line = file.readline()
        while line:
            print(line,end = '')
            try:
                source = get_image_url(line,browser)
                if source == False:
                    print(' couldn`t get image')
                    line = file.readline()
                    continue
            except:
                continue
            try:
                save_image(source,newpath)
            except:
                print(' couldn`t get image')
                line = file.readline()
                continue
            print(' saved without problems')
            line = file.readline()


if __name__ == '__main__':
    main()
#cookies = login([LOGIN,PASSWORD])
#print(json.load)
#browser = init_driver()  
#source = get_image_url('https://vk.com/photo39020745_367241054',browser)

#save_image(source,1)
