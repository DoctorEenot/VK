import requests
from bs4 import BeautifulSoup
import base64 
import re
import cv2
import os


def GetPhoto(data,uid):
    #Получение и детектирование лиц на фото
    #data должен содержать только ссылку на фото и имя-фамилию(опционально)
    try:
        os.mkdir('./'+str(uid))
    except:
        pass

    if len(data)<1:
        return [{'Ошибка':'Не введены данные'}]
    
    elif len(data)>1:
        with open('./'+str(uid)+'/data.txt','w') as file_data:
            file_data.write(data[1]+'\n')
            if len(data)==3:
                file_data.write(data[2]+'\n')
            
            file_data.close()
                
    req = requests.get(data[0]) #Получение страницы imgbb с фото

    if req.status_code == 404:
        return [{'Ошибка':'Некорректный адрес фото'}]

    #Получение ссылки на ориг фото на сервере и самого фото с последуюей конвертацией https://ibb.co/
    #!~~~
    soup = BeautifulSoup(req.text, 'html.parser')
    for link in soup.find_all('img'):
        lk_orig = link.get('src')
        #Отсеивание результатов парсинга
        if 'i.ibb.co' in lk_orig:
            #lk - ссылка на ориг фото на сервере
            image_binary = requests.get(lk_orig) #Получение фото с сервера в бинарном виде (шестнадцеричном)
            image_binary = image_binary.content
            break

    #Получение имени фото
    Photo_Name = lk_orig.replace('https://i.ibb.co/','',1)
    Photo_Name_list = list(Photo_Name)
    Photo_Name_list.reverse()
    Photo_Name = ''
    for i in range(len(Photo_Name_list)):
        if Photo_Name_list[i] == '/':
            break
        Photo_Name = Photo_Name + Photo_Name_list[i]
    Photo_Name = Photo_Name[::-1]

    #Сохранение фото, для последующей работы с opencv
   

    with open('./'+str(uid)+'/'+Photo_Name,'wb') as img:
        img.write(image_binary)

    #Запуск классификатора opencv
    try:
        image = cv2.imread('./'+str(uid)+'/'+Photo_Name)
    except:
        return [{'Ошибка':'Неверный формат фото'}]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.3,
                                         minNeighbors=5,
                                         minSize=(50, 50)
                                         )
    counter = 0
    for (x, y, w, h) in faces:
        roi_color = image[y:y + h, x:x + w]
        cv2.imwrite('./'+str(uid)+'/'+str(counter) + '_faces.jpg', roi_color)
        counter = counter + 1

    if counter == 0:
        return [{'Ошибка':'На фото не найдено лицо'}]

    images = []
    for i in range(counter):
        
        try:
            with open('./'+str(uid)+'/'+str(counter) + str(i)+ '_faces.jpg','rb') as img:
                raw_image_base64 = base64.encodestring(img.read())
   
        except:
            break
        raw_image_base64 = str(raw_image_base64)
        raw_image_base64 = raw_image_base64.replace("b'","",1)#Я не знаю как именно обрабатывает фотографии ваш апи
        raw_image_base64 = raw_image_base64.replace("'","",1)#Поэтому добавил эти строки, с ними работало на сайте
        image_base64 = raw_image_base64.replace("\\n","")#Если будет приходить в сообщении от бота не фото, а текст из символов, эти строки надо будет удалить
        
        images.append(image_base64)#Эту строку удалять нельзя, это заполнение массива
    #!
    if counter == 1:
        return [GetInputFromUser([1],uid)]
    else:
        return images


def GetInputFromUser(data,uid):
    #data- в данном случае массив [номер_картинки]
    read = True
    try:
        file_data = open('./'+str(uid)+'/data.txt','r')
    except:
        read = False

    if read:
        first_name1 = file_data.readline()
        first_name = first_name1.replace("\n","")
        try:
            second_name1 = file_data.readline()
            second_name = second_name1.replace("\n","")
        except:
            pass
        file_data.close()
        os.remove('./'+str(uid)+'/data.txt')
    person_data = [0]
    try:
        person_data.append(first_name)
    except:
        pass
    try:
        person_data.append(second_name)
    except:
        pass

    if len(data)<1:
        return [{'Ошибка':'Не введены данные'}]
    try:
        with open('./'+str(uid)+'/'+ str(data[0]-1)+ '_faces.jpg','rb') as img:
            raw_image_base64 = base64.encodestring(img.read())
    except:
        return [{'Ошибка':'Такого фото предложено не было'}]
    #Обработка фото
    raw_image_base64 = str(raw_image_base64)
    raw_image_base64 = raw_image_base64.replace("b'","",1)
    raw_image_base64 = raw_image_base64.replace("'","",1)
    image_base64 = raw_image_base64.replace("\\n","")#Итоговое фото
    #Работа с сайтом https://findmevk.com/

    sess = requests.Session()
    sess.get('https://findmevk.com/')#Получение сессии сайта
    ans = sess.post('https://findmevk.ru/api/recognizeFace',json = {'image0':image_base64,'image1':image_base64})
    return_data = []

    if len(person_data)>1:#Проверка на совпадение имени или фамилии
        for i in range(len(ans.json())):
            if len(data) == 3:
                if (ans.json()[i]['first_name'] == person_data[1] or ans.json()[i]['last_name'] == person_data[1]) and (ans.json()[i]['last_name'] == person_data[2] or ans.json()[i]['first_name'] == person_data[2]):
                    if re.search(r'\D',str(ans.json()[i]['id'])): 
                        return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
                        return return_data
                    else:
                        return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/id'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
                        return return_data
            else:
                if (ans.json()[i]['first_name'] == person_data[1] or ans.json()[i]['last_name'] == person_data[1]):
                    if re.search(r'\D',str(ans.json()[i]['id'])): 
                        return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
                        return return_data
                    else:
                        return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/id'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
                        return return_data
            
    for i in range(len(ans.json())):#Вывод всех найденых людей
        if re.search(r'\D',str(ans.json()[i]['id'])): 
            return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
        else:
            return_data.append({'Имя':ans.json()[i]['first_name'],'Фамилия':ans.json()[i]['last_name'],'VK':'vk.com/id'+str(ans.json()[i]['id']),'Схожесть':ans.json()[i]['similarity']})
    return return_data

print(GetPhoto(['https://ibb.co/60zgjwm'],1))#Тест
print(GetInputFromUser([1],1))#Тест

#ссылки на фото в формате сокращенных ссылок от imagebb,
#т.е. на сайт imgbb загружается фото и в этот скрипт вставляется та ссылка, которую выдаст imgbb
