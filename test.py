# -*- coding: utf-8 -*-

'''
-----------------------
Код написан под Python3
----------------------- 
'''

'''
Класс Test() обрабатывает исходный файл сsv и создает новый файл с отобранными гипотезами. 
В структуре класса можно выделить три блока:

- Блок для создания внутренней ('рабочей') структуры данных из исходного файла (метод
make_dicts())

- Блок для сравнения полученных данных (методы compare_name(), compare_type(),
compare_street(), compare_number(), compare_build(), compare_owner(), compare_corpus(),
и compare())

- Блок для создания итогового файла с отобранными гипотезами (метод write_file()).

Такое решение и выбранная структура предполагают легкую перенастройку работы класса в случае с выбором другого 
источника исходных данных/вывода результатов (например, записи из базы данных) 
'''



import unicodecsv

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
            reader = unicodecsv.DictReader(f, delimiter=';')
            test = list(reader)

        self.source = test



        self.make_dicts()

        self.final_comparison()

        self.write_file()

    def make_dicts(self):

        '''
        Создаем структуру для хранения уникальных (неповторяющихся) значений организаций
        из 2ГИС, в которой ключ - id организации в 2ГИС, значение каждого
        ключа - массив из словарей с информацией об организации и соответствующими ей гипотезами.

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
        
        pattern_number = re.compile(',\s(\d+\S*)') #паттерн для отбора основного номера в адресе



        
        for row in self.source:

            if row['id'] not in orig.keys():

                first_row = {}  

                first_row['id'] = row['id'].strip()           
                
                name_and_type = row['name'].split(',')

                first_row['name'] = name_and_type[0].strip()

                first_row['type'] = ''

                if len(name_and_type)>1:
                    first_row['type'] = name_and_type[1].strip()


                street_and_number = row['address'].split(',')

                first_row['street_name'] = street_and_number[0].strip()

                first_row['street_number'] = ''.join(re.findall(pattern_number, row['address'])).strip()

                first_row['build_number'] = ''.join(re.findall('.+\sст(\S+)',row['address'])).strip()
                
                first_row['owner_number'] = ''.join(re.findall('.+\sвл(\S+)',row['address'])).strip()

                first_row['corpus_number'] = ''.join(re.findall('.+\sк\s?(\S+)',row['address'])).strip()

                orig[row['id']] = list()
                orig[row['id']].append(first_row) 

            



            orig[row['id']].append(dict())

            index = len(orig[row['id']])-1

            orig[row['id']][index]['ext_id'] = row['ext_id'].strip()

            orig[row['id']][index]['ext_name'] = row['ext_name'].strip()

            orig[row['id']][index]['ext_address'] = row['ext_address'].strip()

            



        self.orig = orig


    def compare_name(self, orig, hype):

        '''
        Метод для сравнения названия заведения из оригинальной записи 2ГИС (orig) и 
        названия из записи с гипотезой (hype). Бьем строки 2ГИС и гипотезы на два массива строк и сравниваем
        их. Метод возврващает максимум 100 баллов в случае совпадения всех слов в массивах.  

        '''

        count = 0

        name = orig['name'].lower().replace('ё', 'е')

        name_list = re.split('[-\s]', name) 

        ext_name = hype['ext_name'].lower()

        to_replace = [('ё', 'е'), ('«', ''), ('»', ''), ('"', ''), ("'", '`'), ('#', '№')] 

        for pair in to_replace:
            ext_name = ext_name.replace(pair[0], pair[1])

        ext_list = re.split('[-\s]', ext_name)

        for word in name_list:
            if word in ext_list:
                count+=1

        
        return (count*100)/len(name_list)

    def compare_type(self, orig, hype):

        '''
        Метод для сравнения типа заведения из оригинальной записи 2ГИС (orig) и 
        типа из записи с гипотезой (hype). Бьем строки 2ГИС и гипотезы на два массива строк и сравниваем
        их. Метод возврващает максимум 100 баллов в случае совпадения всех слов в массивах.  
        
        '''

        count = 0 

        orig_type = orig['type'].lower().replace('ё', 'е')

        if orig_type=='':
            return 0 

        orig_type_list = re.split('[-\s]', orig_type)

        ext_name = hype['ext_name'].lower().replace('ё', 'е')

        ext_list = re.split('[-\s]', ext_name)

        for word in orig_type_list:
            if word in ext_list:
                count+=1
        
        
        return (count*100)/len(orig_type_list)

    def compare_street(self, orig, hype):

        '''
        Метод для сравнения названия улицы из оригинальной записи 2ГИС (orig) и 
        имени адреса из записи с гипотезой (hype).  Метод возвращает 100 баллов в случае совпадения паттерна.  
        
        '''        

        orig_street_name = orig['street_name'].lower().replace('ё', 'е')

        #street_list = re.split('[-\s]', street_name)

        ext_address = hype['ext_address'].lower()

        to_replace = [('ё', 'е'),('ш.', 'шоссе'), ('пр.', 'проспект'),('бул.', 'бульвар'),('ул.', '')]
        
        for pair in to_replace:
            ext_address = ext_address.replace(pair[0], pair[1])

        #если проспекты и шоссе есть и в оригинале и гипотезе - убираем их из сравнения
        
        to_replace1 = ['шоссе','проспект','бульвар']

        for type_street in to_replace1:
        	if orig_street_name.find(type_street)>-1 and ext_address.find(type_street)>-1:
        		orig_street_name = orig_street_name.replace(type_street, '')
        		ext_address = ext_address.replace(type_street, '') 



        pattern = re.search('^'+orig_street_name.strip(), ext_address.strip())
     
        if pattern!=None:
        	return 100
  
        return 0


    def compare_number(self, orig, hype):

        '''
        Метод для сравнения основных номеров в адресах из оригинальной записи 2ГИС (orig) 
        и гипотезы (hype). Подбираем паттерны, которым может соответствовать номер адреса 
        в гипотезе. В случае его совпадения с номером из записи 2ГИС, метод возвращает 50 баллов.  
        
        '''

        orig_street_number = orig['street_number'].lower().replace('ё', 'е')

        if orig_street_number=='':
            return 0


        ext_address = hype['ext_address'].lower().replace('ё', 'е')

        pattern = re.search('[,.]\s'+orig_street_number+'(\s|,|$)', ext_address)

        if pattern!=None:
            return 50
        
        pattern = re.search('[,.]'+orig_street_number+'(\s|,|$)', ext_address)
        
        if pattern!=None:
            return 50

        re_exception = ''


        for exception in ['стр', 'стр.', 'с', 'строение', 'кор.', 'к', 'к.', 'корп.', 'вл.', 'владение']:
            re_exception += '(?<!' + exception + ')'

        
        pattern = re.search('\s' + re_exception + '\s?'+orig_street_number+'(\s|,|$)', ext_address)

        if pattern!=None:
            return 50
        return 0 

     
    def compare_build(self, orig, hype):
        
        '''
        Метод для сравнения номеров строений в адресах из оригинальной записи 2ГИС (orig) 
        и гипотезы (hype). Подбираем паттерны, которым может соответствовать номер строения
        в гипотезе. В случае его совпадения с номером из записи 2ГИС, метод возвращает 50 баллов.  
        
        '''


        orig_build_number = orig['build_number'].lower().replace('ё', 'е')

        if orig_build_number=='':
            return 0

        ext_build_number = hype['ext_address'].lower().replace('ё', 'е')

       
        re_condition = ''

        build_patterns = ['стр', 'стр.', 'с', 'строение', 'ст']

        for token in build_patterns:
            if build_patterns.index(token)==len(build_patterns)-1:
                re_condition+= token
            else:
                re_condition+= token+'|'

        pattern = re.search('\s'+'('+re_condition+')'+'\s?'+orig_build_number+'(\s|,|$)', ext_build_number)

        if pattern!=None:
            return 50 

        return 0 
    

    def compare_owner(self, orig, hype):


        '''
        Метод для сравнения номеров владений в адресах из оригинальной записи 2ГИС (orig) 
        и гипотезы (hype). Подбираем паттерны, которым может соответствовать номер владения
        в гипотезе. В случае его совпадения с номером из записи 2ГИС, метод возвращает 50 баллов.  
        
        '''

        orig_owner_number = orig['owner_number'].lower().replace('ё', 'е')

        if orig_owner_number=='':
            return 0

        ext_owner_number = hype['ext_address'].lower().replace('ё', 'е')

        
        re_condition = ''

        owner_patterns = ['владение', 'вл.', 'вл']

        for token in owner_patterns:
            if owner_patterns.index(token)==len(owner_patterns)-1:
                re_condition+= token
            else:
                re_condition+= token+'|'

        pattern = re.search('\s'+'('+re_condition+')'+'\s?'+orig_owner_number+'(\s|,|$)', ext_owner_number)

        if pattern!=None:
            return 50 

        return 0 


    def compare_corpus(self, orig, hype):

        '''
        Метод для сравнения номеров корпусов адресах из оригинальной записи 2ГИС (orig) 
        и гипотезы (hype). Подбираем паттерны, которым может соответствовать номер корпуса
        в гипотезе. В случае его совпадения с номером из записи 2ГИС, метод возвращает 50 баллов.  
        
        '''


        orig_corpus_number = orig['corpus_number'].lower().replace('ё', 'е')

        if orig_corpus_number=='':
            return 0

        ext_corpus_number = hype['ext_address'].lower().replace('ё', 'е')

        
        re_condition = ''

        corpus_patterns = ['корпус', 'корп.', 'кор.', 'к', 'к.']

        for token in corpus_patterns:
            if corpus_patterns.index(token)==len(corpus_patterns)-1:
                re_condition+= token
            else:
                re_condition+= token+'|'

        pattern = re.search('(^|\s)'+'('+re_condition+')'+'\s?'+orig_corpus_number+'(\s|,|$)', ext_corpus_number)

        if pattern!=None:
            return 50 

        return 0 

    def compare(self, orig, hype):

        '''
        Метод возвращает итоговый результат сравнения оригинальной записи 2ГИС
        '''

        final_count = self.compare_name(orig, hype)+self.compare_type(orig,hype)+self.compare_street(orig, hype)+\
        self.compare_number(orig, hype)+self.compare_build(orig, hype)+self.compare_corpus(orig, hype)+self.compare_owner(orig, hype)
        
        return final_count

    def compareDebug(self, orig, hype):        

        final_count = 'n:'+str(self.compare_name(orig, hype))+' t:'+str(self.compare_type(orig,hype))+' s:'+str(self.compare_street(orig, hype))+' n:'+\
        str(self.compare_number(orig, hype))+' b:'+str(self.compare_build(orig, hype))+' k:'+str(self.compare_corpus(orig, hype))+' ow:'+str(self.compare_owner(orig, hype))
        
        return final_count



    def final_comparison(self):
        '''
        Сравниваем с помощью метода compare() записи из 2ГИС и гипотезы.
        Создаем при каждом сравнении оригинальной записи и ее гипотез
        словарь, в котором каждой гипотезе присваиваем значение 'count'по ключу id.

        Затем отбираем из получившегося словаря id гипотезы с максимальным значением.
        Записываем пару ключ-значение (id гипотезы - максимальный count) в словарь, содержащий
        параметры записи из 2ГИС (self.orig[id][0]). 

        '''

        for key in self.orig:
            temp_count = {}
            for i in range(1,len(self.orig[key])):
                coefficient = self.compare(self.orig[key][0], self.orig[key][i])
                temp_count[self.orig[key][i]['ext_id']] = coefficient
                #лог коэффициента для каждой гипотезы
                self.orig[key][i]['count'] = coefficient

                #self.orig[key][i]['countDebug'] = self.compareDebug(self.orig[key][0], self.orig[key][i])
            
            
            key_value = sorted(temp_count.items(),key=lambda x: x[1], reverse=True)

            self.orig[key][0]['count'] = key_value[0][1]
            self.orig[key][0]['ext_id'] = key_value[0][0]

        


    def write_file(self):
       
       '''
       Метод для создания итогового csv-файла, в котором каждая строка содержит
       уникальную запись из 2ГИС и отобранную для нее гипотезу вместе с полем набранного количества баллов 
       по итогам работы алгоритма. 
       
       '''

       with open('new.csv', 'wb') as csvfile:
            fieldnames = ['id', 'name', 'address', 'ext_id', 'ext_name', 'ext_address', 'count']
            writer = unicodecsv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')


            writer.writeheader() 

            for key in self.orig:
                i = 0
                #Конкатенация адресной строки для адреса в записи из 2ГИС
                orig_address = self.orig[key][0]['street_name']
                if self.orig[key][0]['street_number']!='':
                    orig_address+=', ' +self.orig[key][0]['street_number']
                if self.orig[key][0]['build_number']!='':
                    orig_address+=' ст' +self.orig[key][0]['build_number']
                if self.orig[key][0]['owner_number']!='':
                    orig_address+=' вл' +self.orig[key][0]['owner_number']
                if self.orig[key][0]['corpus_number']!='':
                    orig_address+=' к' +self.orig[key][0]['corpus_number']
                
                #Отбор данных гипотезы с лучшим рейтингом и запись строк в итоговый файл 
                for hyp in self.orig[key]: 
                    if i > 0 and self.orig[key][0]['ext_id']==hyp['ext_id']:
                        writer.writerow({
                        'id': key,
                        'name': self.orig[key][0]['name']+', '+self.orig[key][0]['type'],
                        'address': orig_address,
                        'ext_id': hyp['ext_id'],
                        'ext_name': hyp['ext_name'],
                        'ext_address': hyp['ext_address'],
                        'count' : hyp['count'],
                        #'countDebug' : hyp['countDebug']
                        
                        })
                    i+=1
     
            
        

#Тестируем работу класса, вызывая в конструктор все необходимы методы для создания итогового файла 'new.csv'. 

a = Test('testdata-small.csv')



