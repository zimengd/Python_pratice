#!/usr/bin/env python
# coding: utf-8

# In[188]:


import json
import requests
guardian_api = '5c8d119c-169a-42d8-b4a7-f6f1ff180668'
NYT_api = 'PBcA71TaiApUKSdDsu3AAJ1wb79Lr4Pm'


# In[189]:


CACHE_FNAME = 'cache.json'
try:
    f = open(CACHE_FNAME, 'r')
    content_str = f.read()
    CACHE_DICTION = json.loads(content_str)
    f.close()
except:
    CACHE_DICTION = {}


# In[190]:


# create a unique identifier for search
def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)


# In[191]:


# get data from NYT API, store them in a chache file
# convert data into a list of instances
# return a dictionary containing the search term and a list of instances
def NYT_data(search_term,section_name):
    baseurl = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    pd = {}
    pd['api-key'] = NYT_api
    pd['q'] = search_term
    pd['section_name'] = section_name
    pd['type_of_material'] = 'Article'

    unique_id = params_unique_combination(baseurl, pd)

    if unique_id in CACHE_DICTION:
        python_data = CACHE_DICTION[unique_id]

    else:
        NYT_resp = requests.get(baseurl, params = pd)
        python_data = json.loads(NYT_resp.text)

        CACHE_DICTION[unique_id] = python_data
        fileRef = open(CACHE_FNAME, "w")
        data = json.dumps(CACHE_DICTION)
        fileRef.write(data)
        fileRef.close()

    index = {}
    index['search_term'] = search_term
    index['section'] = section_name
    index['data'] = convert(python_data)
    return index


# In[192]:


# get data from guardian API, store them in a chache file
# convert data into a list of instances
# return a dictionary containing the search term and a list of instances
def guardian_data(search_term,section):
    baseurl = 'https://content.guardianapis.com/search'
    pd = {}
    pd['api-key'] = guardian_api
    pd['q'] = search_term
    pd['section'] = section

    unique_id = params_unique_combination(baseurl, pd)

    if unique_id in CACHE_DICTION:
        python_data = CACHE_DICTION[unique_id]
    else:
        NYT_resp = requests.get(baseurl, params = pd)
        python_data = json.loads(NYT_resp.text)

        CACHE_DICTION[unique_id] = python_data
        fileRef = open(CACHE_FNAME, "w")
        data = json.dumps(CACHE_DICTION)
        fileRef.write(data)
        fileRef.close()
    # a dictionary containing the search term and a list of instances
    index = {}
    index['search_term'] = search_term
    index['section'] = section
    index['data'] = convert(python_data) # convert data into a list of instances
    return index


# In[193]:


#define a class representing an article in NYT
class NYT(object):
    def __init__(self,NYT_diction):
        self.title = NYT_diction['headline']['main']
        self.web_url = NYT_diction['web_url']
        self.snippet = NYT_diction['snippet']
        self.word_count = NYT_diction['word_count']
        self.source = 'New York Times'
        self.keywords = NYT_diction['keywords']
#         self.keylist = self.get_keyword(NYT_diction)[1]
#         self.most_common_letter = self.common_letter()[0]
#         self.freq = self.common_letter()[1]

    def __str__(self):
        return '''Article from NYT: {}\nWeb_Url: {}\nSnippet: {}\nKeywords: {}\nWord_count: {}\n'''.format(self.title,self.web_url,self.snippet,self.keywords,self.word_count)

    #extract keywords and combine them into a long string
    def get_keyword(self):
        k_str = ''
        k_lst = []
        for i in self.keywords:
            if k_str == '':
                k_str = i['value']
            else:
                k_str = k_str+', '+i['value']
            k_lst.append(i['value'])
        return k_str

    #find the most common letter in the title
    def common_letter(self):
        d = {}
        t = self.title.replace(' ','')#remove spaces from the title
        for c in t:
            if c not in d:
                d[c] = 0
            d[c] += 1

        letters = sorted(d.items(),key = lambda x:x[1],reverse = True)
        most_common_letter = letters[0][0]
        freq = letters[0][1]
        return most_common_letter,freq



# In[194]:


# define a class representing an article in NYT
class guardian(object):
    def __init__(self,guardian_diction):
        self.title = guardian_diction['webTitle']
        self.web_url = guardian_diction['webUrl']
        self.section = guardian_diction['sectionName']
        self.source = 'The Guardian'
#         self.most_common_letter = self.common_letter()[0]
#         self.freq = self.common_letter()[1]

    def __str__(self):
        return '''Article from Guardian: '{}'\nWeb_Url: {}\nSection: '{}'\n'''.format(self.title,self.web_url,self.section)

    #find the most common letter in the title
    def common_letter(self):
        d = {}
        t = self.title.replace(' ','')#remove spaces from the title
        for c in t:
            if c not in d:
                d[c] = 0
            d[c] += 1

        letters = sorted(d.items(),key = lambda x:x[1],reverse = True)
        most_common_letter = letters[0][0]
        freq = letters[0][1]
        return most_common_letter,freq


# In[195]:


# convert the response to a list of of article instances
def convert(resp):
    ins_lst = []
    try:
        lst = resp['response']['docs']
        for a in lst:
            ins_lst.append(NYT(a))
    except:
        lst = resp['response']['results']
        for a in lst:
            ins_lst.append(guardian(a))
    return ins_lst


# In[196]:


# output a list of article instances in a .txt file
# a .txt file named by 'search term-section-source.txt'
def output_info(dic):
    lst = dic['data']
    search = '{}-{}-{}'.format(dic['search_term'],dic['section'],lst[0].source)
    fname = search + '.txt'
    header = 'No. ,Source ,Title ,WebUrl ,Most Common Letter in title ,Frequency \n'
    file = open(fname,'w')
    #if header not in file:
    file.write(header)
    n = 0
    for i in lst:
        n += 1
        source = i.source
        title = i.title
        web_url = i.web_url
        common_letter = i.common_letter()[0]
        freq = i.common_letter()[1]
        file.write('{} ,{} ,{} ,{} ,{} ,{} \n'.format(n,source,title,web_url,common_letter,freq))
        file.write('\n')
    file.close()


# In[197]:


# get articles about 'China' in Education section from NYT API
NYT_articles = NYT_data('China','Education')
# get articles about 'China' in technology section from guardian API
guardian_articles = guardian_data('China','technology')


# In[198]:


# output information in .txt file
output_info(guardian_articles)
output_info(NYT_articles)


# In[199]:

# get keywords in the first article from NYT
article1 = NYT_articles['data'][0]
article1_keywords = article1.get_keyword()
print(article1_keywords)
