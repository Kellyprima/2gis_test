# -*- coding: utf-8 -*-

import csv 

import re 

class Test:

    def __init__(self, file):
        
        '''
        В конструктор класса Test передается исходный файл testdata-small.csv.
        Здесь он преобразуется в массив из словарей, каждый из которых представляет
        строку файла, ключи словарей - названия колонок:
        id - идентификатор организации 2ГИС
        name - название организации в 2ГИС
        address - адрес организации в 2ГИС
        ext_id - идентификатор организации из внешней системы 
        ext_name - название организации из внешней системы 
        ext_address - адрес организации из внешней системы

           
        '''
        self.file = file

        with open(self.file, 'rb') as f:
            reader = csv.DictReader(f, delimiter=';')
            test = list(reader)

        self.source = test[20:31]

        self.make_dicts()

    def make_dicts(self):

        '''
        1. Создаем словарь для хранения уникальных (неповторяющихся) значений организаций
        из 2ГИС, в котором ключ - id организации в 2ГИС, значение каждого
        ключа - массив из словарей с информацией об организации и гипотезами.

        Массив[0] - содержит словарь с информацией об организации в 2ГИС  со следующими ключами:
            id - идентификатор организации в 2ГИС
            name - название заведения в 2ГИС (без типа заведения, написанного через запятую)
            type - тип заведения в 2ГИС 
            street_name - название улицы в адресе заведения в 2ГИС
            street_number - номер дома в адресе заведения в 2ГИС
            build_number - номер 'строения'
            owner_number - номер 'владения'
            corpus_number - номер 'корпуса' 
 
        
        Массив[n] - содержит словарь с n-й гипотезой со следующими ключами:

           id - идентификатор гипотезы

           street_hname - название заведения 

           street_hnumber - адрес заведения

        '''
        orig = {} 
        pattern_name = re.compile('(^[^,]+)') #для отбора названий заведений и названий улиц

        pattern_type = re.compile('^.+\,\s(.+)') #для отбора типа заведений

        pattern_number = re.compile(('^.+\,\s([^ст,к,вл,\s]+)')) #для отбора основного номера в адресе



        for row in self.source:

            if row['id'] not in orig.keys():
                orig[row['id']] = list()
                orig[row['id']].append({})
                orig[row['id']][0]['id'] = row['id']

                orig[row['id']][0]['name'] = ''.join(re.findall(pattern_name, row['name']))
                orig[row['id']][0]['type'] = orig[row['id']][0].get('type', '')+\
                                                        ''.join(re.findall(pattern_type, row['name']))
                
                orig[row['id']][0]['street_name'] = ''.join(re.findall(pattern_name, row['address']))

                orig[row['id']][0]['street_number'] = orig[row['id']][0].get('street_number', '')+\
                                                                 ''.join(re.findall(pattern_number, row['address']))
                
                orig[row['id']][0]['build_number'] = orig[row['id']][0].get('build_number', '')+\
                                                                ''.join(re.findall('.+\sст(\S+)',row['address']))

                orig[row['id']][0]['owner_number'] = orig[row['id']][0].get('owner_number', '')+\
                                                                ''.join(re.findall('.+\sвл(\S+)',row['address']))

                orig[row['id']][0]['corpus_number'] = orig[row['id']][0].get('corpus_number', '')+\
                                                                 ''.join(re.findall('.+\sк(\S+)',row['address']))


            orig[row['id']].append(dict())

            index = len(orig[row['id']])-1

            orig[row['id']][index]['ext_id'] = row['ext_id']

            orig[row['id']][index]['ext_name'] = row['ext_name']

            orig[row['id']][index]['ext_address'] = row['ext_address']

        self.orig = orig
    
    def compare(self, orig, hype):
        '''
        Метод для сравнения параметров записи из 2ГИС (self.orig[id][0]) и произвольной внешней записи(self.orig[id][n]).
        orig - self.orig[id][0]
        hype - self.orig[id][n]



        За каждое совпадение начисляется 1 балл. В итоге возвращается суммарный балл для 
        каждой гипотезы. Он сохраняется отдельным значением 

        '''



















#a = Test('testdata-small.csv')

#test_dict = a.make_dicts()







