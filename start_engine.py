# -*- coding: utf-8 -*-

import weather_engine
import db_of_weather
import argparse


class Manager:
    """
    Данный класс выполняет следующие задачи:
    - Добавление прогнозов за диапазон дат в базу данных
    - Получение прогнозов за диапазон дат из базы
    - Создание открыток из полученных прогнозов
    - Выведение полученных прогнозов на консоль
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-data', help='Ввод даты для отображения погоды за выбранный день')
        self.parser.add_argument('-data_end', help='Введите конец диапозона дат для поиска прогноза погоды')
        self.args = self.parser.parse_args()
        self.got_request = None
        self.pars = weather_engine.WeatherMaker().pars_weather()

    def create_bd(self):
        """
        - Добавление прогнозов за диапазон дат в базу данных
        """

        print('\nВы выбрал создать/обновить базуу данных погоды.')
        db_of_weather.DataBD(parser=self.pars).make_data()
        print('База создана/оновлена.\n')

    def request_to_bd(self):
        """
        - Получение прогнозов за диапазон дат из базы
        """

        print('\nВам будет предотавлена информация о погде.')
        db_of_weather.DataBD(parser=self.pars).make_data()
        weather_table = db_of_weather.WeatherTable
        request_to_bd = (weather_table
                         .select()
                         .where((weather_table.date_for_bd == self.args.data) |
                                (weather_table.date_for_bd.between(self.args.data, self.args.data_end))
                                ))
        self.got_request = request_to_bd
        return request_to_bd

    def draw_postcard(self):
        """
        - Создание открыток из полученных прогнозов
        """

        print('\nВы выбрал создание открытки')
        if self.got_request is None:
            self.request_to_bd()
        for item in self.got_request:
            draw_postcard = weather_engine.ImageMaker(weather=item.weather_type, temp=item.temperature,
                                                      date=item.date_for_card)
            draw_postcard.text_and_draw_postcard()

    def get_information(self):
        """
        - Выведение полученных прогнозов на консоль
        """

        print('\nВывод данных в терминале')
        if self.got_request is None:
            self.request_to_bd()
        for item in self.got_request:
            print(f'\n{item.date_for_card} | {item.weather_type} | {item.temperature}\n')

    def use_interaction(self):
        while True:
            if self.args.data is None:
                print('Дата/диапазон дат не был передан.\nВыход из программы')
                break
            print('Выберите что требуется выполнить:\n'
                  'Cоздать/обновить базу данных погоды - "обновить"\n'
                  'Получть прогноз из БД - "прогноз"\n'
                  'Создать открытку - "открытка"\n'
                  'Вывести иноформацию о погоде на консоль - "погода"\n'
                  'Выйти из программы - "выход"\n'
                  )
            input_scenario = input("Поле ввода:")
            if input_scenario in ["обновить", "прогноз", "открытка", "погода", "выход"]:
                if input_scenario == "обновить":
                    self.create_bd()
                if input_scenario == "прогноз":
                    for i in self.request_to_bd():
                        print(f'\nid = {i.id}\n'
                              f'Погода = {i.weather_type}\n'
                              f'Температура = {i.temperature}\n'
                              f'Дата для открытки = {i.date_for_card}\n'
                              f'Дата = {i.date_for_bd}\n')
                if input_scenario == "открытка":
                    self.draw_postcard()
                if input_scenario == "погода":
                    self.get_information()
                if input_scenario == "выход":
                    break
            else:
                print('\nВы ввели не существующую команду.\nПовторите ввод.\n')


start_manager = Manager()
start_manager.use_interaction()
