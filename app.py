# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:57:14 2020

@author: Chanabasagoudap
"""

import os, re, os.path
import json
import numpy as np
import pandas as pd

from flask import Flask, render_template, request, url_for, flash, redirect, jsonify 
from flask import Response
from flask_bootstrap import Bootstrap


import requests 
from requests.auth import HTTPBasicAuth 
import json
from base64 import b64decode
import base64, docx
import pypandoc


from config import config as cf
from resume_scoring import main


app = Flask(__name__)


def job_description_creator(jobReqId):
    print("\n")
    print("\n Entered the Job Description Function")
    
    Url = cf.jobdesc_api
    #print("\n Initial API is:", Url)
    final_URL = Url.replace("2942", jobReqId)
    
    print("\n Final URL:", final_URL)
    response = requests.get(final_URL, auth = HTTPBasicAuth(cf.username, cf.password))
    val = response.content
    
    new_json = val.decode('utf-8') 
    #print(type(new_json))
    
    final = json.loads(new_json)
    #print("Final JD:", final)
    sub_results = final['d']['jobReqLocale']['results']
    html_content = sub_results[0]['jobDescription']
    
    
    # Write HTML String to file.html
    tempfile = cf.tempPath + "testingfile.html"
    with open(tempfile, "w") as file:
        file.write(html_content)

    JDpath = cf.path +"/jd_" + str(jobReqId) +".docx" 
    output  = pypandoc.convert(source=tempfile, format='html', to='docx', outputfile=JDpath, extra_args=['-RTS'])
    print("Output", output)
    
    
    return "Success"
    
    
def resume_saving(final_URL, jobReqId, newAppID):
    
    print("\n Entered the Resume Generator Function")
    response = requests.get(final_URL, auth = HTTPBasicAuth(cf.username, cf.password))
    
    val = response.content
    
    new_json = val.decode('utf-8') 
    #print(type(new_json))
    
    final = json.loads(new_json)
    DocBase = final['d']["fileContent"]
    if DocBase == "null" or DocBase is None:
        print("APPLICATION CAN NOT BE NULL VALUE")
    else:
        #resume_Id = final['d']['ownerId']
        CandidateName_extn = final['d']['fileName']
        #print("Resume ID", resume_Id)
        print("Doc format", CandidateName_extn)
        file_name =cf.path+ str(jobReqId+str("-1")+newAppID+str(-1)+CandidateName_extn)
        print("###################################")
        decoded_val = base64.b64decode(DocBase)
        
        #file_name = "filename.docx"
        
        f = open(file_name, 'wb')
        f.write(decoded_val)
        f.close()
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")




@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def hello():
    return "This is AI Model start point"


@app.route("/rank_resume", methods=['GET', 'POST'])
def rank_resume():
    if request.method == 'POST':
        try:
            for root, dirs, files in os.walk(cf.path):
                 for file in files:
                    os.remove(os.path.join(root, file))
            for root, dirs, files in os.walk(cf.tempPath):
                 for file in files:
                    os.remove(os.path.join(root, file))
                    
            content = request.json
            #print(content)
            jobReqId = content["jobReqId"]
            appID = content["applicationId"]
            #print("Job Requisition ID:", jobReqId)
            #print("Application need to be processed :",appID)
            

            print("Now Working on the Job Description")

            JobReqResult = job_description_creator(jobReqId)
            
            if JobReqResult =="Success":
                print("Job Description is Created!!! Congratulations!!!")
            else:
                print("Failure")
                
    
            for newAppID in appID:
                print("\n Working on Application",newAppID)
                Url = cf.resume_api
                #print("\n Initial API is:", Url)
                newAppID = str(newAppID)
                final_URL = Url.replace("3120", newAppID)
                print("\n Final URL:", final_URL)
                resume_saving(final_URL, jobReqId, newAppID)

            print("All Resume Created!!! Congratulations!!!")
            
            print("**********************************************")
            print("**********************************************")
            print("**********************************************")
            print("*****Begining Resume Scoring Functionality****")
            print("**********************************************")
            print("**********************************************")
            print("**********************************************")
            
            final_result = main()
            
            
            print("**********************************************")
            print("**********************************************")
            print("**********************************************")
            print("*****End of a Resume Scoring Functionality****")
            print("**********************************************")
            print("**********************************************")
            print("**********************************************")
            return jsonify(final_result)

        except Exception as e:
            raise e

            return "Exception Occured. Try again!!!"


# run the application
if __name__ == "__main__":
    app.run()

            
