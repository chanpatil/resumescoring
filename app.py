# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:57:14 2020

@author: Chanabasagoudap
"""

import os, os.path
import json


from flask import Flask, request, jsonify 
from flask import Response
#from flask_bootstrap import Bootstrap

import requests 
from requests.auth import HTTPBasicAuth 
from base64 import b64decode
import base64
import pypandoc

from flask import Flask
from flask_httpauth import HTTPBasicAuth as HBA
from werkzeug.security import check_password_hash

from config import config as cf
from resume_scoring import main


port = int(os.environ.get('PORT', 3000))

app = Flask(__name__)
auth = HBA()


@auth.verify_password
def verify_password(username, password):
    if username in cf.creds and \
            check_password_hash(cf.creds.get(username), password):
        return username


def job_description_creator(jobReqId):
    # print("\n Entered the Job Description Function")
    
    Url = cf.jobdesc_api
    #print("\n Initial API is:", Url)
    final_URL = Url.replace("2942", jobReqId)
    
    #print("\n Final URL:", final_URL)
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
    #print("Output", output)
    if output is None:
        return "Failure"
    else:
        return "Success"
    
    
def resume_saving(final_URL, jobReqId, newAppID):
    
    # print("\n Entered the Resume Generator Function")
    response = requests.get(final_URL, auth = HTTPBasicAuth(cf.username, cf.password))
    
    val = response.content
    
    new_json = val.decode('utf-8') 
    #print(type(new_json))
    
    final = json.loads(new_json)
    if "d" not in list(final.keys()):
        print("")
    else:
        DocBase = final['d']["fileContent"]
        if DocBase == "null" or DocBase is None:
            print("")
        else:
            #resume_Id = final['d']['ownerId']
            CandidateName_extn = final['d']['fileName']
            #print("Resume ID", resume_Id)
            #print("Doc format", CandidateName_extn)
            file_name =cf.path+ str(jobReqId+str("-1")+newAppID+str(-1)+CandidateName_extn)
            #print("###################################")
            decoded_val = base64.b64decode(DocBase)
            
            #file_name = "filename.docx"
            
            f = open(file_name, 'wb')
            f.write(decoded_val)
            f.close()
            #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            return "Success"


@app.route("/rank_resume", methods=['GET', 'POST'])
@auth.login_required
def rank_resume():
    if str(auth.current_user()) in list(cf.creds.keys()):
        try:
            
            # Housekeeping Task
            for root, dirs, files in os.walk(cf.path):
                for file in files:
                    os.remove(os.path.join(root, file))
            for root, dirs, files in os.walk(cf.tempPath):
                for file in files:
                    os.remove(os.path.join(root, file))
                    
                    
            content = request.json
            if not content:
                temp = {"204" :"No Content"}
                return json.dumps(temp)
            else:
                jobReqId = str(content["jobReqId"])
                appID = list(content["applicationId"])
                
                if not jobReqId  or len(appID) == 0:
                    temp = {"400" :"Enter the JobReqID and list of Application ID for Scoring"}
                    return json.dumps(temp)
                else:
    
                    JobReqResult = job_description_creator(jobReqId)
                    if JobReqResult == "Success":
                        for newAppID in appID:
                            #print("\n Working on Application",newAppID)
                            Url = cf.resume_api
                            #print("\n Initial API is:", Url)
                            newAppID = str(newAppID)
                            final_URL = Url.replace("3120", newAppID)
                            #print("\n Final URL:", final_URL)
                            resume_saving(final_URL, jobReqId, newAppID)
                        final_result = main()
                        
                        return jsonify(final_result), 200
                    else:
                        temp = {"415" :"JD Creation Failure.Maybe JD is in not desired format"}
                        return json.dumps(temp)
        
        except Exception as e:
                raise e
                return "Some Exception Occured. Try again!!!", 

    else:
        temp = {"401" : "You may have entered wrong Username or password. Try again!!!"}
        return json.dumps(temp)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

