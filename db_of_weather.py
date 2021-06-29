# -*- coding: utf-8 -*-

import peewee

database = peewee.SqliteDatabase('db_weather.db')


class BaseTable(peewee.Model):
    class Meta:
        database = database


class WeatherTable(BaseTable):
    """Создание столюцов базы данных, хранящие в себе информацию о погоде"""

    id = peewee.PrimaryKeyField(unique=True)
    weather_type = peewee.CharField(36)
    temperature = peewee.CharField(36)
    date_for_card = peewee.CharField(36)
    date_for_bd = peewee.DateTimeField()


class DataBD:

    def __init__(self, parser):
        self.pars = parser

    def make_data(self):
        database.create_tables([WeatherTable])
        weather_for_write = self.pars
        for data in weather_for_write:
            weather, created = WeatherTable.get_or_create(
                date_for_bd=data['Дата для БД'],
                defaults={'weather_type': data['Погода'],
                          'temperature': data['Температура'],
                          'date_for_card': data['Дата']}
            )
            if not created:
                query = WeatherTable.update(
                    weather_type=data['Погода'],
                    temperature=data['Температура'],
                    date_for_card=data['Дата']).where(WeatherTable.id == weather.id)
                query.execute()
