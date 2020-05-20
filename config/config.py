# -*- coding: utf-8 -*-
"""
Created on Mon May 11 15:07:45 2020

@author: Chanabasagoudap
"""

from werkzeug.security import generate_password_hash

# HTTP Basic Authentication
username = 'sfadmin@SFPART035062'
password = 'Test@123'

# Generic Resume Fectching API
resume_api = "https://apisalesdemo2.successfactors.eu/odata/v2/JobApplication(3120L)/resume?$format=json"

# Generic Job description API
jobdesc_api = "https://apisalesdemo2.successfactors.eu/odata/v2//JobRequisition('2942')?$format=json&$expand=jobReqLocale"

#path ="D:/Final Resume Scoring/FinalResumeReaderApplication/word"
path = "../app/word/"

tempPath = "../app/temp/"

#creds
creds = {
        "MouriTech": generate_password_hash("MouriTech^()@0198")
        }
