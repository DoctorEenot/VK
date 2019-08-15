import requests
import lxml.html
from bs4 import BeautifulSoup
import re

vks=[]

def login(data,uid):
    session = requests.session()
    #Функция логина в вк
    #возвращает массив [статус, обьект_сессии]
    #data - [пароль,логин]
    url = 'https://vk.com/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        'DNT':'1'
        }
    #session = requests.session()
    response = session.get(url, headers=headers)
    page = lxml.html.fromstring(response.content)
   
    form = page.forms[0]
    form.fields['email'] = data[0]
    form.fields['pass'] = data[1]
   
    response = session.post(form.action, data=form.form_values())
    if 'onLoginDone' in response.text:
        return [{'Статус':'Сессия создана'},session] #будет возвращаться обьект сессии, он должен быть сохранён и передаваться в другие функции модуля
    else:
        return [{'Ошибка':'Сбой авторизации,сессия не создана'}]
   
session = None
dt = login(['79312354494','Yv7Pf1Tr'],1)
session = dt[1]
def GetUrls_Posts(data,uid): #data - массив [url_страницы_человека , сессия_вк]
    #эта функция ищет посты в которых упоминается человек
    #Возвращает адреса на посты
    session = data[1]
    headers = {#Заголовок гет запроса, необходим для получения страницы с постами
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        

        }
    url_raw = data[0].replace('https://vk.com/','',1)
    url_list = list(url_raw)
   
    url_list.remove(url_list[0])#Быстрее, чем цикл
    url_list.remove(url_list[0])

    buf_str = ''.join(url_list)

    #окончательная логика парсера
    try:
        res = re.search(r'\D',buf_str)
        if res == None:
            id = buf_str
        else:
            response = session.get(data[0])
            soup = BeautifulSoup(response.text,'html.parser')
            for link in soup.findAll('a'):
                url = link.get('href')
            
                if ('photo' in url) and ('profile' in url):
                    id = ''
                    string = url.replace('/photo','',1)
                    string_buf = list(string)
                    for i in range(len(string_buf)):
                        if string_buf[i] == '_':
                            break
                        id = id + string_buf[i]
                    break
    
 
        response = session.get('https://vk.com/feed?obj='+id+'&section=mentions',headers = headers)#Получение страницы с постами
    
        return_buf = []
        soup = BeautifulSoup(response.text, 'html.parser')
        Parse = True
        #Парсинг первой страницы
        for link in soup.find_all('a',{'class':'post_link'}):
        
            url = link.get('href')
            if ('https' in url) :
                #Парсим ответ на комментарий
                return_buf.append(url)
                Parse = False
                continue
            elif Parse:
                #Парсим запись со стены
                return_buf.append('https://vk.com'+url)
            Parse = True

        #Парсинг остальных записей
        headers = {#Заголовок гет запроса, необходим для получения страницы с постами
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
            'Referer':'https://vk.com/feed?obj='+id+'&section=mentions'

            }

        offset = 20 #количество постов
        Done = False
    
        if return_buf == []:
            return [{'Статус':'Записей, в которых есть упоминания об этом человеке, не найдены'}]
        for counter in range(100):#поменяв 100 на меньшее число, например 1, можно уменьшить выдачу
            if Done:
                break
            from_id = ''
            string = return_buf[len(return_buf)-1].replace('/wall','',1)
            last = string.replace('https://vk.com','',1)
            string_buf = list(last)
            for i in range(len(string_buf)):
                if string_buf[i] == '?':
                    break
                from_id = from_id + string_buf[i]
        
            data = {#тело пост запроса
                'al':'1',
                'al_ad':'0',
                'from':from_id,
                'more':'1',
                'obj':id,
                'offset':str(offset),
                'part':'1',
                'section':'mentions'
                }
            offset = offset + 12


            response = session.post('https://vk.com/al_feed.php?sm_mentions',headers = headers,data = data)
        
            if '"all_shown":true' in response.text:
                break
        
            soup = BeautifulSoup(response.text, 'html.parser')
        
            for link in soup.find_all('a',{'class':'post_link'}):

            
                url = link.get('href')
           
                if url in return_buf:
                    continue

                if ('https' in url) :
                    #Парсим ответ на комментарий
                    return_buf.append(url)
                    Parse = False
                    continue
                elif Parse:
                    #Парсим запись со стены
                    return_buf.append('https://vk.com'+url)
                Parse = True
        return return_buf
    except:
        return []

def GetRegistrationDate(data,uid):#data - массив [адрес_страницы_пользователя,сессия]
    session = data[1]
    #Начало парсинга id vk
    
    url_raw = data[0].replace('https://vk.com/','',1)
    url_list = list(url_raw)
   
    url_list.remove(url_list[0])#Быстрее, чем цикл
    url_list.remove(url_list[0])

    buf_str = ''.join(url_list)

    #окончательная логика парсера
    try:
        res = re.search(r'\D',buf_str)
        if res == None:
            id = buf_str
        else:
            response = session.get(data[0])
            soup = BeautifulSoup(response.text,'html.parser')
            for link in soup.findAll('a'):
                url = link.get('href')
            
                if ('photo' in url) and ('profile' in url):
                    id = ''
                    string = url.replace('/photo','',1)
                    string_buf = list(string)
                    for i in range(len(string_buf)):
                        if string_buf[i] == '_':
                            break
                        id = id + string_buf[i]
                    break
   
        #Парсим дату
    
    
        response = session.get('https://vk.com/foaf.php?id='+id)
        soup = BeautifulSoup(response.text,features="lxml")
        for date_raw in soup.findAll('ya:created'):
            date_parsed = date_raw.attrs['dc:date']
            date_parsed_list = list(date_parsed)

        #так быстрее, чем циклом
        year = date_parsed_list[0] + date_parsed_list[1] + date_parsed_list[2] + date_parsed_list[3]
        month = date_parsed_list[5] + date_parsed_list[6]
        day = date_parsed_list[8] + date_parsed_list[9]

        return [year,month,day]
    except:
        return []

def GetFamily(data,uid): #data - массив [адрес_страницы,для_поиска , фамилия, сессия]
    
    session = data[2]
    
    #Парсим корень имени
    root_of_name_list = list(data[1])
    if len(root_of_name_list)<2:
        root_of_name = data[1]
    else:
        root_of_name = ''
        for i in range(int(len(root_of_name_list)/2)):
            root_of_name = root_of_name + root_of_name_list[i]

    #Начало парсинга id vk
    
    url_raw = data[0].replace('https://vk.com/','',1)
    url_list = list(url_raw)
   
    url_list.remove(url_list[0])#Быстрее, чем цикл
    url_list.remove(url_list[0])

    buf_str = ''.join(url_list)

    #окончательная логика парсера
    try:
        res = re.search(r'\D',buf_str)
        if res == None:
            id = buf_str
        else:
            response = session.get(data[0])
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.findAll('a'):
            
                url = link.get('href')
            
                if (('photo' in url) and ('profile' in url)) or ('mvk_entrypoint' in url):
                    id = ''
                    accepted_url = url
                
                    if 'mvk_entrypoint' in accepted_url:
                        accepted_url_raw = accepted_url.replace('/write','',1)
                        id = accepted_url_raw.replace('?mvk_entrypoint=profile_page','',1)
                        break
                    string = url.replace('/photo','',1)
                    string_buf = list(string)
                    for i in range(len(string_buf)):
                        if string_buf[i] == '_':
                            break
                        id = id + string_buf[i]
                    break
    
        headers = {#Заголовок пост запроса, необходим для получения страницы с друзьями
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Connection':'keep-alive',
            'Referer':data[0]

            }
    
        post_data = {#Данные для пост запроса
            'act':'box',
            'al':'1',
            'al_ad':'0',
            'oid':id,
            'tab':'friends'
            }
    
        response = session.post('https://vk.com/al_page.php',headers = headers,data = post_data)
    
        soup = BeautifulSoup(response.text, 'html.parser')
    
        return_buf = []
        for link in soup.findAll('a',{'class':'fans_fan_lnk'}):
            friend_name = ''
            friend_lastname = ''
        
            #print(link.text)
            #Парсим имя и фамилию друга
            if root_of_name in link.text: 
                return_buf.append('https://vk.com'+link.get('href'))
    
    
        offset = 120
        Stop = False
        for i in range(100):
            if Stop:
                break
            post_data = {#Данные для пост запроса
                'act':'box',
                'al':'1',
                'al_ad':'0',
                'offset':offset,
                'oid':id,
                'tab':'friends'
                }
            response = session.post('https://vk.com/al_page.php',headers = headers,data = post_data)
            soup = BeautifulSoup(response.text, 'html.parser')
    
        
            for link in soup.findAll('a',{'class':'fans_fan_lnk'}):
                friend_name = ''
                friend_lastname = ''
            
            
                #Парсим имя и фамилию друга
                if root_of_name in link.text:
                    if link.get('href') in return_buf:
                        Stop = True
                        break
                    return_buf.append('https://vk.com'+link.get('href'))
                
            offset += 120
        if return_buf == []:
            return [{'Статус':'Однофамильцев не найдено'}]
        else:
            return return_buf
    except:
        return []



done_buffer = None
def site(data,uid):
    global vks,session,done_buffer
    done_buffer = []
    vks = data
    dt = login(['79312354494','Yv7Pf1Tr'],1)
    session = dt[1]
    
    for vk in data:
        count = 1
        ret = dict()
        Date = GetRegistrationDate([vk,session],1)
        ret['Дата Регистрации'] = Date[0]+'-'+Date[1]+'-'+Date[2]
        posts = GetUrls_Posts([vk,session],1)
        for post in posts:
            ret[str(count)] = post
            count += 1
        done_buffer.append(ret)

def sname(data,uid):
    global session,done_buffer
    for i in range(len(vks)):
        family = GetFamily([vks[i],data[i],session],1)
        counter = 1
        #print(family)
        for people in family:
            done_buffer[i]['однофамилец '+ str(counter)] = people
            counter += 1
    return done_buffer


site(['https://vk.com/dobrinskii'],1)
print(sname(['Добринский'],1))

input()
