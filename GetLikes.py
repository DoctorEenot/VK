import requests
import lxml.html
from bs4 import BeautifulSoup
import re

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


def GetId(VkUrl,session):#Возвращает id пользователя, техническая функция, вызывать не надо.
    #VkUrl - ссылка на аккаунт
    #session - сессия залогиненного аккаунта


    #Начало парсинга id vk
    
    url_raw = VkUrl.replace('https://vk.com/','',1)
    url_list = list(url_raw)
   
    url_list.remove(url_list[0])#Быстрее, чем цикл
    url_list.remove(url_list[0])

    buf_str = ''.join(url_list)

    #окончательная логика парсера
    res = re.search(r'\D',buf_str)
    if res == None:
        id = buf_str
    else:
        response = session.get(VkUrl)
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

    return id

def GetFriends(VkUrl,session):#Возвращает список друзей, техническая функция, вызывать не надо.
    #VkUrl - ссылка на аккаунт
    #session - сессия залогиненного аккаунта
    
    #
    headers = {#Заголовок пост запроса, необходим для получения страницы с друзьями
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        'Referer':VkUrl

        }
    
    post_data = {#Данные для пост запроса
        'act':'box',
        'al':'1',
        'al_ad':'0',
        'oid':GetId(VkUrl,session),
        'tab':'friends'
        }
    response = session.post('https://vk.com/al_page.php',headers = headers,data = post_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return_buf = []
    for link in soup.findAll('a',{'class':'fans_fan_lnk'}):

        
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
            if link.get('href') in return_buf:
                    Stop = True
                    break
            return_buf.append('https://vk.com'+link.get('href'))
    if return_buf == []:
        return [{'Статус':'Либо у данного пользователя нет друзей, либо они скрыты'}] 
    return return_buf

def GetPhotos(VkUrl,targetUrl,session):#Получает фотографии со страницы человека, техническая функция, вызывать не надо.
    MaxPhotos = 100
    id = GetId(VkUrl,session)
    target_name = targetUrl.replace('https://vk.com/','',1)
    target_id = GetId(VkUrl,session)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        'DNT':'1'
        }
    data = {
        'act':'show',
        'al':'1',

        }
    #Парсинг альбомов со страницы пользователя
    ret_buffer = []
    response = session.get(VkUrl+'?z=albums'+id,headers = headers)
    
    soup = BeautifulSoup(response.text,'html.parser')
    albums = ['https://vk.com/album'+id+'_0?rev=1','https://vk.com/album'+id+'_00?rev=1']
    for album in soup.findAll('a',{'class':'page_album_link'}):
        
        if '/album' in album.get('href'):
            albums.append('https://vk.com'+album.get('href')+'?rev=1')

    #Получение фото из альбомов и парсинг лайкнувших
    counter = 0
    Done = False
    for i in range(len(albums)):
        if Done == True:
            break
        response = session.get(albums[i],headers = headers)
        soup = BeautifulSoup(response.text,'html.parser')
        for row in soup.findAll('div',{'class':'photos_row'}):
            if counter > MaxPhotos:
                Done = True
                break
            children = row.findChildren('a')
            photo_raw = children[0].get('href')
            photo_raw = photo_raw.replace('?rev=1','',1)
            photo = photo_raw.replace('/','',1)
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                    'Accept-Encoding':'gzip, deflate',
                    'Connection':'keep-alive',
                    'Referer':'https://vk.com/'+photo,
                    'DNT':'1'
                    }
            data = {
                    'act':'show',
                    'al':'1',
                    'loc':photo,
                    'ref':'',
                    'w':'likes/'+photo
                    }
            ans = session.post('https://vk.com/wkview.php',headers = headers,data = data)
            soup_another = BeautifulSoup(ans.text,'html.parser')
            #Парсинг лайкнувших
            for like in soup_another.findAll('a',{'class':'fans_fan_lnk'}):
                liked = like.get('href')
                if (target_id in liked) or (target_name in liked):
                    ret_buffer.append('https://vk.com/'+photo)
            
            counter += 1
        
           # print(photo)
    return ret_buffer

def site(data,uid):#Основная функция, её надо вызывать
    #data - массив [адрес_на_страницу_цели]
    #В данном случае принимает только одну цель, её и парсит
    dt = login(['79312354494','Yv7Pf1Tr'],1)

    if len(dt)<2:
        return dt
    session = dt[1]
    target = data[0]
    friends = GetFriends(target,session)
    ret_buffer = []
    for i in range(len(friends)):

        #Отладочная Строка! Удалить при добавлении к боту!
        print('Parsing: ',friends[i])#Отладочная Строка! Удалить при добавлении к боту!
        #Отладочная Строка! Удалить при добавлении к боту!

        liked = GetPhotos(friends[i],target,session)
        for n in range(len(liked)):
            ret_buffer.append(liked[n])
    return ret_buffer

#Провека основной работоспособности:

print(site(['https://vk.com/yakov460'],1))#Адрес - страница, человека, чьи лайки парсим



#Проверка отдельных функций, в основном коде не нужны
#dt = login(['79312354494','Yv7Pf1Tr'],1)#Логин в аккаунт, вызвать один раз, после передавать сессию, другим методам,
                                        #Все остальное пояснено в самой функции
                                        #Функцию логина можно вызвать из другого моего модуля, это не принципиально важно
                                        #Он здесь
#dt = [статус,сессия]
#session = dt[1]
#print(GetPhotos('https://vk.com/oktesh','https://vk.com/oktesh',session))
#print(GetFriends('https://vk.com/oktesh',session))
#id = GetId('https://vk.com/oktesh',session)
