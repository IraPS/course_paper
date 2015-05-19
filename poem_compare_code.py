# -*- coding: utf-8 -*-

from __future__ import division
import codecs
import os
import re

# Задаём расположение файлов для сравнения
SOURCE_PATH = './source_path'  # название папки, в которой лежат варианты, которые нужно сравнить с каноническим
CANON = './canon.txt'  # название файла, в котором лежит канонический текст

beg_g = '<font color="#008000">'   # начало выделения зеленым цветом в html
beg_r = '<font color="#E80000">'  # начало выделения красным цветом в html
end = '</font>'  # конец выделения цветом в html


# Вычисление расстояния Левенштейна между двумя текстами
def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2+1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1],
                                             distances[index1+1],
                                             new_distances[-1])))
        distances = new_distances
    return distances[-1]


# Принимает имена файлов t. Возвращает список дескрипторов открытых файлов.
def open_files(t):
    text_open1 = codecs.open(t[0], 'r', 'utf-8')
    text_open2 = codecs.open(t[1], 'r', 'utf-8')
    text_write1 = codecs.open(t[2], 'w', 'utf-8')
    return [text_open1, text_open2, text_write1]


# Закрывает открытые файлы
def close_files(t):
    for k in t:
        k.close()


# Возвращает общую последовательность подряд идущих символов - для случаев, когда слова совпадают не полностью
def common_s(s1, s2):
    m = [[0] * (1 + len(s2)) for _ in xrange(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


# Сравнивает строку со строкой. Без '\n' !
def compare(l1, l2):
    same = ''  # строка с совпадениями
    diff = ''  # строка с несовпадениями с первой строке
    new1 = ''
    l1 = l1.strip()
    l2 = l2.strip()
    if len(l1) == 0:
        return ' '  # Если первая строка пуста, вернем пустую строку
    if len(l2) == 0:
        return ''  # Если первая не пуста, а вторая не пуста - вернем ''
    for i in l1.split():  # цикл по словам в 1й строке
        match_ij = False  # Совпадение слов i, j
        full_match = False
        for j in l2.split():
            if i == j:
                same += i + '\n'
                full_match = match_ij = True
                break
        for j in l2.split():
            if not full_match:
                if len(common_s(i, j)) != 0:
                    if len(common_s(i, j)) >= 4 or len(i) == 2 or (len(common_s(i, j))/len(i)) >= 0.75:
                        punct_arr = ['.', ',', ';', ':', '!', '?']
                        if j[-1] in punct_arr and i[-1] not in punct_arr:
                            newi = i.split(common_s(i, j))
                            newii = u'<r>' + newi[0] + u'</r>' + common_s(i, j) + u'<r>' + \
                                    newi[1] + u'</r>' + u'<r>_</r>'
                        else:
                            newi = i.split(common_s(i, j))
                            newii = u'<r>' + newi[0] + u'</r>' + common_s(i, j) + u'<r>' + newi[1] + u'</r>'
                        same += newii + '\n'
                        l1 = l1.replace(i, newii)
                        match_ij = True
                        break
        if not match_ij:
            diff += i + '\n'

    # Условие про минимум одинаковых слов в строках (60% или 75% ?)
    if len(same.split()) != 0:
        if (len(same.split())/len(l1.split())) >= 0.6:
            match = True
        else:
            diff += same
            same = ''
            match = False
    else:
        match = False

    if match:
        for e in l1.split():
            if e in same:
                new1 += e + ' '
            else:
                e = beg_r + e + end
                new1 += e + ' '
        new1 = re.sub(u'<r>', beg_r, new1)
        new1 = re.sub(u'<g>', beg_g, new1)
        new1 = re.sub(u'</r>', end, new1)
        new1 = re.sub(u'</g>', end, new1)
        l1 = new1
        return l1
    else:
        return ''


# t - список дескрипторов 3 файлов. Сравнивает t[0] с t[1]. Но не наоборот. Формирует t[2].
def analysis(t, compare_function):
    header = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'
    header += '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
    header += '\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
    header += '<title></title></head>\n<body>'
    footer = str('</body>\n</html>')
    text1 = t[0].read()
    text1 = unicode(text1)
    text2 = t[1].read()
    text2 = unicode(text2)
    a1 = text1.split('\n')
    a2 = text2.split('\n')
    t[2].write(header)
    for i1 in a1:
        full_match_str = False
        found = False
        for i2 in a2:
            if i1 == i2:
                full_match_str = True
                t[2].write(i1 + '<br>\n')
                found = True
                break
        for i2 in a2:
            if not full_match_str:
                match = compare_function(i1, i2)
                if len(match) != 0:
                    i1 = match
                    found = True
                    t[2].write(i1 + '<br>\n')
                    break
        if not found:
            t[2].write(beg_r + i1 + end + '<br>\n')
    t[2].write('<span style="border:0.8px solid black;">')
    t[2].write(u'Расстояние Левенштейна между <em>' +  lst[q].split('.')[0] + u'</em> и <em>'
               + (CANON.split('/')[1]).split('.')[0]
               + u'</em> = ' + '<strong><big>' + str(levenshtein_distance(text1, text2)) +
               u'</big></strong></span><br>\n')
    t[2].write(footer)


# Анализировать 3 файла
def proceed(file_list, compare_function):
    descriptor_list = open_files(file_list)
    analysis(descriptor_list, compare_function)  # Сравнивает t[0] с t[1]. Формирует t[2].
    close_files(descriptor_list)


# Сравнение канонического CANON с вариантами из SOURCE_PATH . Требует наличия и файла, и папки
lst = os.listdir(SOURCE_PATH)
if '.DS_Store' in lst:          # фикс скрытого файла изменения папки в MacOS
    lst.remove('.DS_Store')
print 'Канонический вариант', CANON.split('/')[1], 'сравнивается с вариантами в папке', \
    SOURCE_PATH.split('/')[1], ' : ', lst
for q in range(0, len(lst)):
    proceed([SOURCE_PATH+'/'+lst[q], CANON, (lst[q].split('.'))[0]+'.html'], compare)
