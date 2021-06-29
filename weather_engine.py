# -*- coding: utf-8 -*-
import datetime

import requests
from bs4 import BeautifulSoup
import re
import cv2


class WeatherMaker:
    REG_TEMP = r'.\d{1,2}.'
    REG_DATE = r'\d+\s\w+\s\d+'

    def __init__(self):
        self.data_of_weather = []

    def pars_weather(self):
        """Парсер прогноза погоды за 10 дней
        с сайта https://pogoda.mail.ru/prognoz/nizhniy_novgorod/
        :return Список словарей данных с сайта
        """

        headers = {
            'accept': '* / *',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48'
        }

        url = 'https://pogoda.mail.ru/prognoz/nizhniy_novgorod/'
        response = requests.get(url, headers)
        src = response.text
        soup = BeautifulSoup(src, 'html.parser')

        today_date = (soup.find('div', class_='information__header__left__date')).text.strip()[0:-7]
        today_temperature = (soup.find('div', class_='information__content__temperature')).text.strip()[0:-1]
        today_weather = soup.find('div', class_='information__content__temperature').find('span')
        today_weather = today_weather.get_attribute_list('title')[0]
        today_date_bd = datetime.date.today()
        today_date = re.search(self.REG_DATE, today_date)[0]
        self.for_saving_data(today_weather, today_temperature, today_date, today_date_bd)

        ten_days = soup.find_all('div', class_='day__date')
        weather_by_days = soup.find_all('div', class_='day__description')
        temperature_by_days = soup.find_all('div', class_='day__temperature')

        count = 1
        for weather, temperature, day in zip(weather_by_days, temperature_by_days, ten_days):
            weather = weather.text
            temperature = re.search(self.REG_TEMP, temperature.text)[0][0:-1]
            day = day.text
            date_bd = today_date_bd + datetime.timedelta(days=count)
            count += 1
            self.for_saving_data(weather, temperature, day, date_bd)
        return self.data_of_weather

    def for_saving_data(self, weather, temperature, day, date_bd):
        """Создание списка и добавление данных сайта"""

        dict_data = {
            'Погода': weather,
            'Температура': temperature,
            'Дата': day,
            'Дата для БД': datetime.datetime.strftime(date_bd, '%d.%m.%Y')
        }
        self.data_of_weather.append(dict_data)


class ImageMaker:

    def __init__(self, weather, temp, date):
        self.weather = weather
        self.temp = temp
        self.date = date
        self.image_cv2 = cv2.imread('python_snippets/external_data/probe.jpg')
        self.state_of_weather = {
            'солнечно': 'img/sun.jpg',
            'ясно': 'img/sun.jpg',
            'малооблачно': 'img/sun.jpg',
            'переменная облачность': 'img/sun.jpg',
            'облачно с прояснениями': 'img/cloud.jpg',
            'дождь': 'img/rain.jpg',
            'снег': 'img/snow.jpg',
            'облачно': 'img/cloud.jpg',
            'пасмурно': 'img/cloud.jpg',
            'дождь/гроза': 'img/rain.jpg'
        }

    def color_of_postcard(self):
        """Создание цветового градиента для карточек"""

        img = self.image_cv2.copy()
        height, width, _ = img.shape
        r = 255
        g = 255
        b = 255
        cv2.line(img, (0, 0), (width, 0), (r, g, b), 10)
        for i in range(height, 0, -1):
            if self.weather in ['ясно', 'солнечно', 'малооблачно', 'переменная облачность', 'облачно с прояснениями']:
                r -= 1
            elif self.weather in ['дождь', 'дождь/гроза']:
                b -= 1
                g -= 1
            elif self.weather == 'снег':
                b -= 1
            elif self.weather in ['облачно', 'пасмурно']:
                r -= 1
                g -= 1
                b -= 1
            cv2.line(img, (0, i), (width, i), (r, g, b), 2)
        return img

    def glue_image(self):
        """Объединение одного изоржения с другим
        :return Объединенное изображение
        """

        main_image = self.color_of_postcard()

        for key in self.state_of_weather.keys():
            if key in self.weather.lower():
                image_2 = cv2.imread(self.state_of_weather[key])
                rows, cols, channel = image_2.shape
                roi = main_image[0: rows, 0: cols]

                img_sun_grey = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(img_sun_grey, 10, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)

                main_image_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
                image_2 = cv2.bitwise_and(image_2, image_2, mask=mask)
                dst = cv2.add(main_image_bg, image_2)
                main_image[0:rows, 0:cols] = dst
                return main_image
            else:
                'Некорректный ввод, повторите еще раз'

    def text_and_draw_postcard(self):
        """Создание текста и его позиционировании и вывод на экран"""

        img = self.glue_image()
        temp = f'temp: {self.temp}'
        date = f'date: {self.date}'
        weather = f'weather: {self.weather}'
        img = cv2.resize(img, (500, 256))
        if self.weather in ['ясно', 'солнечно', 'малооблачно', 'переменная облачность', 'облачно с прояснениями']:
            if self.weather in ['переменная облачность', 'облачно с прояснениями']:
                weather = 'weather: пер.облачность'
            color = (0, 136, 255)
        elif self.weather in ['дождь', 'дождь/гроза']:
            color = (255, 255, 165)
        elif self.weather == 'снег':
            color = (165, 100, 100)
        elif self.weather in ['облачно', 'пасмурно']:
            color = (140, 140, 80)

        cv2.putText(img, date, (115, 60), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=color, thickness=2)
        cv2.putText(img, temp, (100, 135), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=color, thickness=2)
        cv2.putText(img, weather, (50, 210), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=color, thickness=2)

        cv2.imshow(f'temp {self.temp}', img)
        cv2.waitKey(0)

