#!/usr/bin/python3
# ­*­ coding: utf­8 ­*­
'''
This is the "smart" algorithm to create recommendations for correcting erroneous pairs (brand + number).
'''
import os
import sys
import time
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit

start_time = time.time()

all_synonyms = []
dic_synonym_brand ={} 
dic_brandnumber_name = {}
dic_brandnumber_price = {}
dic_brand_number = {}

f=open('db_all_synonyms.csv','r')
for line in f:
    l = line.strip()
    if l != '':
        all_synonyms.append(line.strip())
f.close()
print('All brands and synonyms are uploaded to the general list')
time0 = time.time()
print("--- %s seconds ---" % (time0 - start_time))


f=open('db_brand_synonyms.csv','r')
for line in f:
    l = line.split(';')
    key = l[1].strip() 
    val = l[0].strip() 
    try:
        arr_brand = dic_synonym_brand[key]
        arr_brand.append(val)
        dic_synonym_brand[key] = arr_brand
    except:
        arr_brand = []
        arr_brand.append(val)
        dic_synonym_brand[key] = arr_brand 

print('The reverse dictionary synonym:brand is loaded')
time1 = time.time()
print("--- %s seconds ---" % (time1 - time0))

f=open('db_all_numbers_prices.csv','r')
count_sku=0
countRowPrice=0
for line in f:
    l = line.strip().split(';')
    if len(l) == 4:
        count_sku += 1
        brand = l[0].strip()
        number = l[1].strip()
        name = l[2].strip()
        price = int(l[3])
        if price > 0:
            countRowPrice = countRowPrice + 1
        cur_arr = []
        try:
            arr_exist = dic_brand_number[brand]
            arr_exist.append(number)
            dic_brand_number[brand] = arr_exist
        except:
            arr_exist = []
            arr_exist.append(number)
            dic_brand_number[brand] = arr_exist
                      
        dic_brandnumber_name[brand+number] = name
        dic_brandnumber_price[brand+number] = price
    else:
        print("Error in line {} of the file all_numbers.csv".format(count_sku+1))

f.close()
print('Nomenclature loaded - three dictionaries (brand:number, brandnumber:name, brandnumber:price)')
time2 = time.time()
print("--- %s seconds ---" % (time.time() - time1))
prep_time = time.time() - start_time


def distance(a, b):
    '''Calculates the Levenshtein distance between a and b. From Wikipedia article'''
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n+1) # Keep current and previous row, not entire matrix
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def get_brand_or_synonym(a):

    arr_exact = []  
    arr_entry = []   
    arr_similar = [] 

    for i in range(len(all_synonyms)):
        d = distance(a.upper(), all_synonyms[i].upper())
        if d == 0:
            arr_exact.append(all_synonyms[i])
        elif d == 1:
            arr_similar.append(all_synonyms[i])        
        elif d <= 2 and len(a) > 4 and len(a) < 7 and len(all_synonyms[i]) == len(a):
            arr_similar.append(all_synonyms[i])            
        elif d <= 3 and len(a) > 6 and len(all_synonyms[i]) == len(a):
            arr_similar.append(all_synonyms[i])                                                                                                
        elif len(a) >= 2 and all_synonyms[i].upper().find(a.upper()) > -1 and len(all_synonyms[i])/len(a) < 3:
            arr_entry.append(all_synonyms[i])
    return [arr_exact, arr_entry, arr_similar]


def get_number_by_one_brand(brand_recom, n):    

    arr_num = dic_brand_number[brand_recom]
    n_comp = n.replace(' ','').replace('.','').replace('-','').replace('/','').replace('\\','').strip().upper()
    n_recom = ''

    for i in range(len(arr_num)):
        x_comp = arr_num[i].replace(' ','').replace('.','').replace('-','').replace('/','').replace('\\','').strip().upper()        
        if n_comp == x_comp:
            n_recom = arr_num[i]
            return n_recom
       
    for i in range(len(arr_num)):
        x_comp = arr_num[i].replace(' ','').replace('.','').replace('-','').replace('/','').replace('\\','').strip().upper()
        if x_comp.find(n_comp) > -1:
            n_recom = arr_num[i]
            break
        elif distance(n_comp, x_comp) < 2:
            n_recom = arr_num[i]
            break
        else:
            n_recom = ''
    return n_recom


def get_number_by_several_brands(arr_brand, n):    
    b_entry = ''
    b_cur_arr = []
    b_all_arr = []
    for j in range(len(arr_brand)): 
        try:
            cur = arr_brand[j]
            b_cur_arr = dic_synonym_brand[cur]
            for j in range(len(b_cur_arr)):
                b_all_arr.append(b_cur_arr[j])
        except:
            continue
                    
    if len(b_all_arr) > 0:
        # find number
        n_recom = ''
        for p in range(len(b_all_arr)):
            try:
                n_recom = get_number_by_one_brand(b_all_arr[p], n)
                if n_recom != '':
                    return [b_all_arr[p],n_recom]
            except:
                continue               
        return ['Empty']              
    else:
        return ['Empty']

def get_number(arr,n):    
    # Exactly
    if len(arr[0]) > 0:
        res = get_number_by_several_brands(arr[0],n)
        if res[0] != 'Empty':
            return res        
    # Entering
    if len(arr[1]) > 0:
        res = get_number_by_several_brands(arr[1],n)
        if res[0] != 'Empty':
            return res   
    # Similar
    if len(arr[2]) > 0:
        res = get_number_by_several_brands(arr[2],n)
        if res[0] != 'Empty':
            return res
    return ['Empty']


def get_recommendation(b,n,pr):
    texec1 = time.time()
    arr = get_brand_or_synonym(b) # [arr_exact, arr_entry, arr_similar]
    print('\n-------------------------------------------------------------')
    print("Wanted    : {}\nExactly   : {}\nEntering  : {}\nSimilar   : {}".
          format(b, arr[0], arr[1], arr[2]))
    print("--- %s seconds ---" % (time.time() - texec1))
    print('-------------------------------------------------------------')
    res = [[b,n]]    
    res.append(get_number(arr,n))  
    # Get the detail name
    name = ''    
    try:
        key = res[1][0]+res[1][1]
        name = dic_brandnumber_name[key]
    except:
        name = ''        
    # Get the price
    price = 0
    try:
        key = res[1][0]+res[1][1]
        price = dic_brandnumber_price[key]
    except:
        price = 0
    
    checkPrice = ''
    if price == 0:
        checkPrice = 'There was no sale'
        window.lineEditPrice2.setStyleSheet("color: rgb(0, 0, 255);")
    elif pr != 0 and pr/price < 2:
        checkPrice = 'The price is adequate'
        window.lineEditPrice2.setStyleSheet("color: rgb(0, 204, 0);")
    elif pr == 0:
        window.lineEditPrice2.setStyleSheet("color: rgb(0, 0, 0);")
        window.lineEditPrice2.setText('')
    else:
        checkPrice = 'The price is too high'
        window.lineEditPrice2.setStyleSheet("color: rgb(255, 0, 0);")
    window.label2prices.setText("{} / {}".format(pr,price))
       
    texec = time.time() - texec1
    print("\nThe resulting array {}".format(res))
    print("\nRequest execution time")
    print("--- %s seconds ---" % (texec))
    return [res,texec,name,checkPrice]


def main():
    print('test')
    QApplication.processEvents()
    b = window.lineEdit1.text()
    n = window.lineEdit2.text()
    pr = 0
    try:
        pr = int(window.lineEditPrice1.text().strip())
    except:
        pr = 0
        
    if b != '' and n != '':
        res = get_recommendation(b,n,pr)
        if res[0][1][0] != 'Empty':
            window.lineEdit3.setText(str(res[0][1][0]))
            window.lineEdit4.setText(str(res[0][1][1]))
            window.textEditName.setText(str(res[2]))
            window.lineEditPrice2.setText(str(res[3]))
        else:
            window.lineEdit3.setText('')
            window.lineEdit4.setText('')    
            window.textEditName.setText('')
            window.lineEditPrice2.setText('')
            window.lineEditPrice2.setStyleSheet("color: rgb(0, 0, 0);")
            window.label2prices.setText('')
        window.label.setText("Request execution time {} seconds".format(str(round(res[1],3))))
        QApplication.processEvents()

def focusLineEdit2():
    window.lineEdit2.setFocus()
    
def focusLineEditPrice1():
    window.lineEditPrice1.setFocus()
   
def focusPushButton():
    window.pushButton.setFocus()

app = QApplication(sys.argv)
window = QMainWindow()
window = uic.loadUi("detector.ui")
window.label2.setText("Nomenclature, prices, brands and synonyms are downloaded in {} seconds".format(round(prep_time,3)))
window.pushButton.setAutoDefault(True)
window.pushButton.clicked.connect(main)
window.lineEdit1.returnPressed.connect(focusLineEdit2)
window.lineEdit2.returnPressed.connect(focusLineEditPrice1)
window.lineEditPrice1.returnPressed.connect(focusPushButton)
window.label3.setText("Nomenclature items are: {} from them {} with the prices".format(count_sku, countRowPrice))
window.show()
sys.exit(app.exec_())

