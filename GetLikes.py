down = True
import requests
import lxml.html
from bs4 import BeautifulSoup
import re
import sys
from termcolor import colored
try:
    from image_downloader import main as img_download
except:
    down = False
    print('Couldn`t find image_downloader module')
    


LOGIN = ''
PASSWORD = ''
API_KEY = ''
api_version = '5.89'

def login(data):
    
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

    try:
        res = re.search(r'\D',buf_str)
    except:
        pass
    if True:
        if res == None:
            id = buf_str
        else:
            response = session.get(VkUrl)
            #print(response.text)
            soup = BeautifulSoup(response.text,'html.parser')
            for link in soup.findAll('a'):
                #print(link)
                url = link.get('href')
                try:
                    if (('photo' in url) and ('profile' in url)) or ('mvk_entrypoint' in url): #and ('profile' in url):
                        id = ''
                        string = url.replace('/photo','',1)
                        string_buf = list(string)
                        for i in range(len(string_buf)):
                            if string_buf[i] == '_':
                                break
                            id = id + string_buf[i]
                        break
                    elif ('/friends' in url) and ('id' in url):
                        id = url[url.find('/friends?id=')+12:url.find('§')]
                        try:
                            res = re.search(r'\D',id)
                        except:
                            pass
                        if res != None:
                            id = url[url.find('&id=')+4:]
                        break
                        
                except:
                    continue
    return id

def get_friends(VkUrl,session):
    ret_buf = []
    id = GetId(VkUrl,session)#id друга
    res_users = requests.get(f'https://api.vk.com/method/friends.get?user_id={id}&access_token={API_KEY}&v={api_version}')
    print('Found:',res_users.json()['response']['count'],'friends')
    for fid in res_users.json()['response']['items']:
        ret_buf.append('https://vk.com/id'+str(fid))
    return ret_buf
    



def GetPhotos(VkUrl,targetUrl,target_id,session):#Получает фотографии со страницы человека, техническая функция, вызывать не надо.
    MaxPhotos = 100
    id = GetId(VkUrl,session)
    #print(id)
    target_name = targetUrl.replace('https://vk.com/','',1)
    #target_id = GetId(targetUrl,session)
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
    try:
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
    except:
        return []

def site(data,uid):#Основная функция, её надо вызывать
    #data - массив [адрес_на_страницу_цели]
    #В данном случае принимает только одну цель, её и парсит
    ret_buffer = []
    dt = login([LOGIN,PASSWORD])
    print(dt[0])
    if len(dt)<2:
        return dt
    
    session = dt[1]
    for target in data:
        print('Working on',target)
        target_id = GetId(target,session)
        print(target_id+'.txt','File created')
        out_file = open(target_id+'.txt','w')
        friends = get_friends(target,session)
        
        for friend in friends:

            #Отладочная Строка! Удалить при добавлении к боту!
            print('Parsing: ',friend,end = '')#Отладочная Строка! Удалить при добавлении к боту!
            #Отладочная Строка! Удалить при добавлении к боту!
            try:
                liked = GetPhotos(friend,target,target_id,session)
                print(colored(' Parsed without problems','yellow'))
            except:
                print(colored(' Something wrong with this friend','red'))
                continue
            for like in liked:                
                out_file.write(like+'\n')                
        out_file.close()
        if down:
            print('starting downloading liked pictures')
            img_download([target_id+'.txt'])
        else:
            print('downloading images skiped, \ncouldn`t find module image_downloader')
def usage():
    print('There must be links to pages')
    print('ex: GetLikes.py https://vk.com/restless_linker')


def main():

    try:
        targets = sys.argv[1:]
    except:
       usage()
       return 1
    if targets == []:
        usage()
        return 1
    #print(targets)
    number_of_targets = len(targets)
    print('Working on '+str(number_of_targets)+' targets')
    site(targets,1)

if __name__ == '__main__':
    main()





