#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pymongo import MongoClient


# In[2]:


klient=MongoClient("mongodb://localhost:27017")
db=klient['bazaZaliczenie']


# In[3]:


import requests 
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'} #https://myhttpheader.com/


# In[4]:


import os
def download_and_save_page(link):
    try: 
        response = requests.get(link)
        if response.status_code == 200: # sprawdzanie statusu połączenia aby uniknąć błędów
            r=requests.get(link,headers=headers)
            page ={
            'url':link,
            'content':r.text,
            }
            db.stronywww.insert_one(page)
            print(f"Pobrano i zapisano stronę: {link}")
        else:
            print(f"Błąd pobierania strony {link}. Status kodu: {response.status_code}") # w razie błędu jego kod

    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania strony {link}: {e}")

file_path = 'links.txt' #dostęp do pliku z stronami 
with open(file_path, 'r') as file:
    links = file.read().splitlines()
    for link in links:
        download_and_save_page(link)


# In[5]:


from bs4 import BeautifulSoup

def save_links_info(webpage_content):
    soup = BeautifulSoup(webpage_content, 'html.parser')
    links = soup.find_all('a')
    
    for link in links:
        link_info = {
            'url': link.get('href'),
            'text': link.text.strip(),
            'attributes': dict(link.attrs)
        }
        db.linkiZstron.insert_one(link_info)
        
data=db.stronywww.find({})
for d in data:
    save_links_info(d['content'])
    print(f"Zapisano linki z strony: {d['url']}")


# In[6]:


def download_images(webpage_content):
    soup = BeautifulSoup(webpage_content, 'html.parser')
    images = soup.find_all('img')
           
    for image in images:
        image_info = {
            'url' : image.get('src'),
            'alt' : image.get('alt'),
            'width' : image.get('width'),
            'height' : image.get('height')
        }
        db.zdjeciaZstron.insert_one(image_info)
data=db.stronywww.find({})
for d in data:
    download_images(d['content'])
    print(f"Zapisano zdjecia z strony: {d['url']}")


# In[7]:


from collections import Counter

def analyze_keywords(webpage_content, link, db):
    soup = BeautifulSoup(webpage_content, 'html.parser')
    text = soup.get_text()
    
    # Analiza słów kluczowych
    words = text.split()
    new_words = [word for word in words if len(word) > 3]
    word_frequency = Counter(new_words)

    
    word_to_add = {'url': link, 'words': []} #Lista aby ograniczyć ilość rekordów i mieć 5 słów do 1 strony w jednym miejscu 
    
    for i, (word, count) in enumerate(word_frequency.most_common(5), start=1):
        word_info = {
            f'Slowo {i}': f'{word} : {count}'
        }
        word_to_add['words'].append(word_info)

    db.rankingSlow.insert_one(word_to_add)
data=db.stronywww.find({})
for d in data:
    analyze_keywords(d['content'], d['url'], db)
    print(f"Zapisano ranking słów z strony: {d['url']}")

