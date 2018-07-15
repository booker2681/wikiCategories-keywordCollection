
# coding: utf-8

# In[1]:


import requests, json, os, time
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


# In[2]:


wiki = 'https://en.wikipedia.org'

def get_category(url, is_next=False): 
    data = {}
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Subcategories
    if soup.select('#mw-subcategories .mw-content-ltr a'): # subcategory
        for word in soup.select('#mw-subcategories .mw-content-ltr a'): 
            print(word.text)
            print(wiki + word['href'])
            get_category(wiki + word['href'])
    
    if soup.select('#mw-subcategories a'): # subcategory have next page ?
        if soup.select('#mw-subcategories a')[0].text == 'next page':
            print(wiki + soup.select('#mw-subcategories a')[0]['href'])
            get_category(wiki + soup.select('#mw-subcategories a')[0]['href'])
    
    # Pages
    if soup.select('#mw-pages .mw-content-ltr a'): # page in category
        for word in soup.select('#mw-pages .mw-content-ltr a'): 
            print(word.text)
            print(wiki + word['href'])
            data[word.text] = get_page(wiki + word['href'])
    
    if soup.select('#mw-pages a'): # page have next page ?
        if soup.select('#mw-pages a')[1].text == 'next page':
            print(wiki + soup.select('#mw-pages a')[1]['href'])
            get_category(wiki + soup.select('#mw-pages a')[1]['href'], True)
    
    # output json   
    file_name = soup.select('#firstHeading')[0].text.split('Category:')[1]
    if(is_next == True): # have next page
        with open( dir_name + '/' + file_name + '.json', 'r') as f:
            origin_data = json.load(f)
            origin_data.update(data)
            data = origin_data
        with open( dir_name + '/' + file_name + '.json', 'w') as f:  
            json.dump(data, f)
    else:
        with open( dir_name + '/' + file_name + '.json', 'w') as f:
            json.dump(data , f)


# In[3]:


def get_page(url):
    page_res = requests.get(url)
    page_soup = BeautifulSoup(page_res.text, 'html.parser')
    contents = ''
    
    for word in page_soup.select('p'):
        # print(word.text)
        contents += word.text
        
    print()
    return contents


# In[4]:


def crawler(category):
    
    # create dir
    global dir_name 
    dir_name = "jsondata-" + time.strftime('%Y-%m-%d %H%M%S') 
    if not os.path.exists(dir_name):    
        os.makedirs(dir_name)
    
    url = 'https://en.wikipedia.org/wiki/Category:' + category
    print('Start get ' + category)
    get_category(url)


# In[5]:


# wiki category 
crawler('Porsche_vehicles')


# In[6]:


def keyword_collection():
    # read all data in dir
    files= os.listdir(dir_name)
    for file in files:
        print(file)
        with open (dir_name + '/' + file, 'r') as f:
            data = json.load(f)
            keyword_filter(data)


# In[7]:


stop_symbols = ['–', '●', '○', '～', '『', '』', '】', '【', '「', '」', 'ˊ', '’', '‘', '﹕', '﹐', '.', '…', '\t', '\n', ' ', ']', '[', ',', '?', '、', '。', '“', '”', '《', '》', '！', '，', '：', '；', '？', '\'', ';', '\"', '{', '}', '/', '(', ')', '\"\"', '``', '\'\'', '\'m', '\'s', ':', '&', '@', '#', '%']
upper_stop_words = []
for word in stopwords.words('english'):
    upper_stop_words.append( word[0].upper() + word[1:len(word)])
stop_words = stopwords.words('english') + upper_stop_words +stop_symbols
print(stop_words)

def keyword_filter(datas):
    datas = list(datas.values()) # get values in dict
    category_keywords = {}
    
    for page_data in datas:
        
        #sentence tokenize
        sentences = sent_tokenize(page_data)
        #print(sentences)
        
        #word tokenize
        for sent in sentences:
            word_list = word_tokenize(sent)
            word_list = list( set(word_list) - set(stop_words) ) # delete stop word
            word_list.sort()
            print(word_list)
            keywords = gen_keywords(word_list)
            
            # store keywords in category_keywords
            for k in keywords:
                if k in category_keywords:
                    for k2 in keywords[k]:
                        if k2 in category_keywords[k]: # same keyword update value
                            category_keywords[k][k2] += keywords[k][k2]
                        else:
                            category_keywords[k][k2] = keywords[k][k2]
                else:
                    category_keywords[k] = keywords[k]
        
    
    # create keyword dir 
    dir_name = "keywords" 
    
    if not os.path.exists(dir_name): # first time generate keyword data
        os.makedirs(dir_name)
        with open( dir_name + '/keywords.json', 'w') as f:  
            json.dump(keywords_sort(category_keywords), f)
            
    else: # keyword data had existed
        origin_keywords = {}
        with open( dir_name + '/keywords.json', 'r') as f: # update keyword data
            origin_keywords = json.load(f) 
            
            for k in category_keywords:
                if k in origin_keywords:
                    for k2 in category_keywords[k]:
                        if k2 in origin_keywords[k]: # same keyword update value
                            origin_keywords[k][k2] += category_keywords[k][k2]
                        else:
                            origin_keywords[k][k2] = category_keywords[k][k2]
                else:
                    origin_keywords[k] = category_keywords[k]
                            
                               
        with open( dir_name + '/keywords.json', 'w') as f:  
            json.dump(keywords_sort(origin_keywords), f)


# In[8]:


def gen_keywords(word_list):
    keywords = {}
    
    # init keyword data
    for i in word_list:  
        count = {}
        for j in word_list:
            if i != j:
                count[j] = 1
        keywords[i] = count # {'i': {'j1': time, 'j2': time ...}}
    
    return keywords


# In[9]:


def keywords_sort(keywords):
    sorted_keywords = {}
    for k in keywords:
        sorts = sorted(keywords[k].items(), key=lambda x:x[1], reverse=True)
        sorted_keywords[k] = {sorts[i][0] : sorts[i][1] for i in range(0, len(sorts))}
    return sorted_keywords


# In[10]:


keyword_collection()


# In[11]:


def get_keyword(keyword):
    with open( 'keywords/keywords.json', 'r') as f:
        keywords = json.load(f)
        if keyword in keywords:
            return keywords[keyword]
        else:
            return 'Not find'


# In[12]:


get_keyword('Porsche')

