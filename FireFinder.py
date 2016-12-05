#!/usr/bin/env python3
import datetime
import http.client
import json.decoder
import smtplib
import googlemaps
import settings
import logging


#setup email
mailServer = smtplib.SMTP('smtp.gmail.com', 587)
mailServer.ehlo()
mailServer.starttls()
try:
    mailServer.login(settings.emailLogin(), settings.emailPw())
except Exception:
    logging.exception("Email Login")

#Query every day or query every hour?
today = datetime.datetime.now()
print(today)
today = today - datetime.timedelta(hours=12)
print(today.strftime('%Y-%m-%dT%H:%M:%S.%f'))
uri = "/resource/grwu-wqtk.json?$query=SELECT%20datetime,%20address,%20type,%20incident_number%20WHERE%20datetime%20>%20\""
uri += today.strftime('%Y-%m-%dT%H:%M:%S.%f')
uri += '"'

#Gather info from Seattle.gov website
seaData = http.client.HTTPSConnection('data.seattle.gov')
header = {"X-App-Token":"xD7zm0umu9QcSt9uH72IidCNx"}
seaData.request("GET", uri, "", header)
seaDataJson = seaData.getresponse()

#Parse JSON
seaList = json.loads(seaDataJson.read().decode('utf-8')) #is a list of dicts
print(seaList)
#Determine which addresses are close to GG's
gmaps = googlemaps.Client(key=settings.apiKey())

for object in seaList:
    noEmailSent = True
    address = object["address"]
    if "/" in address:
        address = address[0:address.index("/")]
    address += " Seattle, WA"
    try:
        distance_matrix = gmaps.distance_matrix(settings.ggAddress(), address, "driving", "", "", "imperial")
    except Exception:
        logging.exception("Distance Matrix call")
    distance = distance_matrix["rows"][0]["elements"][0]["distance"]
    print(object["address"])
    if 'ft' in distance["text"]:
        testMsg = """From: Seattle FireWatcher <%s>
        To: Test Recipient <%s>
        Subject: It's close

        Address: %s
        Distance: %s
        Type: %s
        """ % (settings.sender(), settings.recipient(), address, distance["text"], object["type"])
        #Make sure we haven't sent this email already
        try:
            readStor = open('localStor.txt')
        except Exception:
            logging.exception("Open File read only")
        for line in readStor:
            if line[0:line.index("\n")] == object["incident_number"]:
                noEmailSent = False
        readStor.close()
        if noEmailSent:
            mailServer.sendmail(settings.sender(), settings.recipient(), testMsg)
            try:
                storage = open('localStor.txt', 'a')
            except Exception:
                logging.exception("Open File in append mode")
            storage.write(object["incident_number"])
            storage.write('\n')
            storage.close()

#Message to confirm program is running
msg = """From: Seattle FireWatcher <%s>
To: Test Recipient <%s>
Subject: I ran today!

I ran today dude!
""" % (settings.sender(), settings.recipient())
if datetime.datetime.now().time() >= datetime.time(9,0,0) and datetime.datetime.now().time() < datetime.time(9,59,0):
    mailServer.sendmail(settings.sender(), settings.recipient(), msg)
    print("Sent mail")




#OLD OLD OLD
#bodyVal = '{"id":"kzjm-xkqj","name":"Seattle Real Time Fire 911 Calls","attribution":"City of Seattle Fire Department MIS","attributionLink":"http://web5.seattle.gov/MNM/incidentresponse.aspx","category":"Public Safety","description":"Provides Seattle Fire Department 911 dispatches. Updated every 5 minutes.","displayType":"table","licenseId":"CC0_10","publicationAppendEnabled":true,"resourceName":"fire-911","columns":[{"id":3479077,"name":"Address","fieldName":"address","position":1,"description":"Location of Incident","width":227,"dataTypeName":"text","tableColumnId":1290345,"format":{},"flags":null,"metadata":{}},{"id":3479078,"name":"Type","fieldName":"type","position":3,"description":"Response Type","width":198,"dataTypeName":"text","tableColumnId":1290346,"format":{},"flags":null,"metadata":{}},{"id":3479079,"name":"Datetime","fieldName":"datetime","position":4,"description":"The date and time of the call.","width":222,"dataTypeName":"date","tableColumnId":1411673,"format":{"align":"left"},"flags":null,"metadata":{}},{"id":3479080,"name":"Latitude","fieldName":"latitude","position":5,"description":"This is the latitude value. Lines of latitude are parallel to the equator.","width":100,"dataTypeName":"number","tableColumnId":1290349,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479081,"name":"Longitude","fieldName":"longitude","position":6,"description":"This is the longitude value. Lines of longitude run perpendicular to lines of latitude, and all pass through both poles.","width":100,"dataTypeName":"number","tableColumnId":1290350,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479082,"name":"Report Location","fieldName":"report_location","position":7,"width":100,"dataTypeName":"location","tableColumnId":1393474,"format":{},"flags":null,"metadata":{}},{"id":3479083,"name":"Incident Number","fieldName":"incident_number","position":8,"width":100,"dataTypeName":"text","tableColumnId":1419260,"format":{"precisionStyle":"standard","align":"right"},"flags":null,"metadata":{}}],"metadata":{"custom_fields":{"Refresh Frequency":{"Frequency":"5 minutes"},"Data Owner":{"Owner":"Seattle Fire Department"}},"renderTypeConfig":{"visible":{"table":true}},"availableDisplayTypes":["table","fatrow","page"],"thumbnail":{"page":{"created":true}},"rdfSubject":"0","rowIdentifier":"0","rdfClass":"","jsonQuery":{"order":[{"columnFieldName":"datetime","ascending":false}]}},"query":{"orderBys":[{"ascending":false,"expression":{"columnId":3479079,"type":"column"}}]},"tags":["seattle","911","fire","dispatch e911","sfd mobile"],"flags":["default","restorable","restorePossibleForType"],"originalViewId":"kzjm-xkqj","displayFormat":{}}'
#test.request("POST", "/views/INLINE/rows.json?accessType=WEBSITE&method=getByIds&asHashes=true&start=0&length=50&meta=true", bodyVal)