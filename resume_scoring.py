
#importing all required libraries

import PyPDF2
import re
import json
import os

#import spacy
import docx2txt
#import en_core_web_sm
#nlp = en_core_web_sm.load()

#import nltk
#from nltk import Tree
#nltk.download("all")
from nltk.tokenize import sent_tokenize
from pyresparser import ResumeParser
#from nltk import word_tokenize, pos_tag, ne_chunk


from geotext import GeoText
#from commonregex import CommonRegex

from difflib import get_close_matches
from config import config as cf


mypath= cf.path

def file_reader(path_name):
    file_extension = path_name.split(".")[-1]
    # print(file_extension)
    if file_extension == 'docx':
        return docx_reader(path_name)
    elif file_extension == 'pdf':
        return pdf_extract(path_name)
    else:
        return ('\n\tFile extension not supported!\n\n')


def docx_reader(file):
    text = docx2txt.process(open(file,'rb'))
    # print(text)
    return text


def pdf_extract(file):
    fileReader = PyPDF2.PdfFileReader(open(file,'rb'))
    countpage = fileReader.getNumPages()
    count = 0
    text = []
    while count < countpage:    
        pageObj = fileReader.getPage(count)
        count +=1
        t = pageObj.extractText()
        text.append(t)
    text = str(text)
    text = text.replace("\\n", "")
    return text
 
def get_cities(text):
    GeoTestLoc = GeoText(text)
    list_cities = set(GeoTestLoc.cities)
    return list_cities


def calculate_skill_score(text, skill_list):
    no_kws, not_matched_kw = closeMatches(text, skill_list)
    # print("skill_list:",skill_list)
    # print("no_kws:",no_kws)
    # print("not_matched_kw:",not_matched_kw)
    no_skills = get_unq_skill(skill_list)
    try:
        skill_score = round(no_kws/no_skills,2)
    except Exception as e:
        skill_score = 0
    return (skill_score,not_matched_kw)

def get_unq_skill(skill_list):
    try:
        skill_list = set([x.strip().replace(' ','').lower() for x in skill_list])
    except Exception as e:
        skill_list = []
    return(len(skill_list))


def get_close_matches(each_word, sentences):
    for sentence in sentences:
        each_word = "|".join(re.split(r"[^a-zA-Z0-9]", each_word))
        if re.search(re.compile(r"({})".format(each_word),re.IGNORECASE),sentence):
            return True
        else:
            continue


def closeMatches(sentences, words): 
    close_words = []
    for each_word in words:
        # print(each_word)
        if get_close_matches(each_word, sentences):
            close_words.append(each_word)
        else:
            continue
    not_matched_kw = list(set(words)-set(close_words))
    # print("Close words:{},not_matched_kw{}".format(close_words,not_matched_kw))
    return(get_unq_skill(close_words), not_matched_kw)



def get_score(req, given):
#     print("Reqd:",req," Given:",given)
    if(req <=given):
        return 1
    else:
        return 0

# Replace string to Number
def string_to_number(text):
#     print(text)
    dct={'zero':'0','one':'1','two':'2','three':'3','four':'4',
     'five':'5','six':'6','seven':'7','eight':'8','nine':'9',
        'ten':'10','eleven':'11','twelve':'12','thirteen':'13',
         'fourteen':'14','fifteen':'15','sixteen':'16',
         'seventeen':'17','eighteen':'18','nineteen':'19'}

    text_lists = text.lower().split()
    for item in text_lists:
        if item in dct.keys():
            dct_value = dct[item]
            text = text.replace(item,dct_value)
    return text


## Get Total implementation
def get_implementation(text):
    text = re.split('[.,\t\n]',text)
    text = [i.split('and') for i in text]
    try:
        text =sum(text,[])
    except Exception as e:
        pass
    match_string = "implementation"
    matched_sent = [i for i in text if match_string in i.lower()]
#     print(matched_sent)
    not_match_string = "year"
    matched_sent = [i for i in matched_sent if not_match_string not in i.lower()]
    matched_sent = [string_to_number(i) for i in matched_sent]
    # print(matched_sent)
    expr_match = [re.findall(r'[\d]', i, re.IGNORECASE) for i in matched_sent]
    expr_match = sum(expr_match, [])
    # print(expr_match)
    try:
        total_impl = max(list(map(int, expr_match)))
    except Exception as e:
        total_impl = 0
    return total_impl

## Get experience
def get_experience(text):
    text = sent_tokenize(text)
    text = sum([re.split('[\t\n]',i) for i in text],[])
    text = [i.split('and') for i in text]
    try:
        text =sum(text,[])
    except Exception as e:
        pass
    match_string = "year"
    matched_sent = [i for i in text if match_string in i.lower()]
    matched_sent = [string_to_number(i) for i in matched_sent]
    expr_match = [re.findall(r"\d+(?:\.\d+)?", i, re.IGNORECASE) for i in matched_sent]
    expr_match = sum(expr_match, [])
    try:
        expr_match = list(map(float, expr_match))
        expr_match = [i for i in expr_match if i <30.0]
        total_exprns = max(expr_match)
    except Exception as e:
        total_exprns = 0

    return total_exprns

def select_field_dic(profile_dic):
    keys_to_have = ["job_id","candidate_id","email", "mobile_number", "candidate_name", "profile_score", "total_experience","comments"]
    dict_new = { key: profile_dic[key] for key in keys_to_have }
    return(dict_new)



def get_job_id_name(path_name):
    try:
        full_str = path_name.split("/")[-1]
        job_str = full_str.split("-1")
        job_id = job_str[0]
        candidate_id = job_str[1]
        candidate_name = job_str[-1].split(".")[0]
    except Exception as e:
        return('','','')
    return (job_id, candidate_id, candidate_name)


def get_meta_JD(jd_file_path):
    meta_data = {}
    if jd_file_path:
        text_word = docx_reader(jd_file_path)
        text_list = sent_tokenize(text_word)
        text_list = sum([re.split('[\t\n]',i) for i in text_list],[])
        text_list = [text for text in text_list if text]
        # print(text_list)
        try:
            for item in text_list:
                key = item.split(':')[0]
                if key.strip():
                    value = item.split(':')[1:]
                    if len(value):
                        value = sum([i.strip().split(',') for i in value if i],[])
                        value = sum([i.strip().split('and') for i in value if i],[])
                        meta_data[key] = value
                        # print(value)
        except Exception as e:
            pass
    meta_data_dup = meta_data.copy()
    for key, item in meta_data_dup.items():
        if key and len(item):
            # print("key & len(item): ",key,len(item), item)
            pass
        else:
            meta_data.pop(key,None)
    # print(meta_data)
    if not meta_data:
        #print("\n\t Job description is not in specific format.")
        return(" ")
    else:
        return meta_data

def get_optional_mandatory_field(jd_metadata):
    opt_filed = []
    mndtry_field = []
    for key, item in jd_metadata.items():
        #print(key)
        if str('_optional') in key.lower():
            opt_filed.append(key)
        else:
            mndtry_field.append(key)

#     print(opt_filed,mndtry_field)
    return (opt_filed,mndtry_field)

def get_bool_comment(input_value, reqd_value):
    # print("Input: ",input_value,"reqd_value: ",reqd_value)
    if input_value < reqd_value:
        return 'no'
    else:
        return 'yes'


## Get experience
def get_key_num(text,key):
    text = sent_tokenize(text)
    text = sum([re.split('[\t\n]',i) for i in text],[])
    text = [i.split('and') for i in text]
    try:
        text =sum(text,[])
    except Exception as e:
        pass
    match_string = key
    matched_sent = [i for i in text if match_string in i.lower()]
    matched_sent = [string_to_number(i) for i in matched_sent]
    key_match = [re.findall(r"\d+(?:\.\d+)?", i, re.IGNORECASE) for i in matched_sent]
    key_match = sum(key_match, [])
    try:
        key_match = list(map(float, key_match))
        kay_value = max(key_match)
    except Exception as e:
        kay_value = 0

    return kay_value
    

def get_key_Unit(file,key, num_item):
    if key.lower() in 'experiences':
        total_experience = get_experience(file)
        # print(total_experience)
        reqd_expr = num_item
        # print("experiences",total_experience,"reqd_expr", reqd_expr)
        key_score = get_score(reqd_expr, total_experience)
        comments = get_bool_comment(total_experience, reqd_expr)     
    elif key.lower() in 'implementation':
        no_of_implementation = get_implementation(file)
        # print("implementation",no_of_implementation)
        reqd_imp = num_item
        key_score = get_score(reqd_imp, no_of_implementation)
        comments = get_bool_comment(no_of_implementation,reqd_imp)
    else:
        no_of_value = get_key_num(file,key)
        reqd_key_value = num_item
#         print("no_of_value",no_of_value,"reqd_key_value", reqd_key_value)
        key_score = get_score(reqd_key_value, no_of_value)
        comments = get_bool_comment(no_of_value,reqd_key_value)
        
    return (key_score, comments)

def get_key_list_value(text, key, item):
    check_list = item
    key_score, not_matched_item = calculate_skill_score(text,check_list)
    # print("\nkey_score:", key_score)
    # print("\nNot Matched Item",not_matched_item)
    
    if (0<len(not_matched_item) < len(check_list)):
#         comment = 'partial'
        comment = not_matched_item[:5]
    elif len(not_matched_item) ==0:
        comment = 'yes'
    else:
        comment = 'no'
    
#     return (key_score,comment,not_matched_item[:5])
#     return (key_score,not_matched_item[:5])
    return (key_score, comment)
    

#function that does phrase matching and builds a candidate profile
def profile_score(file,profile_dic,jd_metadata):
    comments = {}
    score_list = []
    fields = jd_metadata.keys()
    text = sent_tokenize(file)
    text = sum([re.split('[\t\n]',i) for i in text],[])
    # print(jd_metadata,"\n")
    opt_filed,mndtry_field = get_optional_mandatory_field(jd_metadata)
#     print(opt_filed,mndtry_field)
    flag = 0
    for key, item in jd_metadata.items():
        # print("\t for Key and len of item: ", key,len(item))
        try:
            num_item = item[0].split(" ")      
            num_item = max([[x for x in num_item if x.isdigit()]])
            # print("\t num item :",num_item)
        except Exception as e:
            pass
        if len(num_item) > 0:
            flag = 1
        if (key in mndtry_field and flag == 1):           
            # print("mandatory & flag: ",key,max(num_item))
            no_of_keyUnit, comment = get_key_Unit(file,key,int(num_item[0]))
            score_list.append(no_of_keyUnit)
        elif key in mndtry_field:
            # print("Mandatory:", key)
#             no_of_keyUnit, comment,not_matched_item = get_key_list_value(text,key,item)
            no_of_keyUnit, comment = get_key_list_value(text,key,item)
            score_list.append(no_of_keyUnit)
        elif (key in opt_filed and flag == 1):
            # print('Optional & flag:',key,max(num_item))
            no_of_keyUnit, comment = get_key_Unit(file,key,int(num_item[0]))
        else:
            # print("optional:",key)
#             no_of_keyUnit, comment,not_matched_item = get_key_list_value(text,key,item)
            no_of_keyUnit, comment = get_key_list_value(text,key,item)
                          
        comments[key] = comment
        flag = 0
        

    try:
        total_score = round(sum(score_list)/len(score_list),2)
    except Exception as e:
        total_score = 0
    
    if total_score==0:
        total_score =0.05
        
    return (total_score,comments)
  
    
def main():
    jd_file_path = ""
    total_files = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

    jd_file_path = [path for path in total_files if str('jd_') in path.lower()][0]
    jd_metadata = get_meta_JD(jd_file_path)
    if type(jd_metadata) != dict:
        #print("\n\t** JD format Error **")
        temp = {"415" :"JD is in not specific format"}
        return json.dumps(temp)
        # return ("\n\t**### Error ###**\n \tJD is not in specific format.\n\t Kindly check JD format.\n ")
    # print(jd_metadata)
#     print("files:",total_files)
    resume_files = total_files.copy()
    resume_files.remove(jd_file_path)
#     print("resume_files",resume_files)
    profiles={}
    i = 0 
    while i < len(resume_files):
        file = resume_files[i]  
        #print(file)
        try:
            text = file_reader(file)     
            profile_dic = ResumeParser(file).get_extracted_data()
            profile_dic['total_experience'] = get_experience(text)
            prof_scr_val,comments_list=  profile_score(text,profile_dic,jd_metadata)
            profile_dic['profile_score'] = prof_scr_val
            profile_dic['comments'] = comments_list

            job_id, candidate_id, candidate_name = get_job_id_name(file)
            profile_dic.update({'job_id':job_id,'candidate_id':candidate_id,'candidate_name':candidate_name})
            # print("\n\n",profile_dic)
            profiles[i] = select_field_dic(profile_dic)
        except Exception as e:
            pass
        i += 1
        
    print(profiles)
    return profiles
