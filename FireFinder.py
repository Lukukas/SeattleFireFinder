import datetime
import http.client
import json.decoder
import smtplib
import googlemaps
import settings

#Query every day or query every hour?
today = datetime.datetime.today().strftime('%Y-%m-%d')
print(today)
today += "T00:00:00.000"
print(today)
uri = "/resource/grwu-wqtk.json?$query=SELECT%20datetime,%20address,%20type%20WHERE%20datetime%20>%20\""
uri += today
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
    print(object["address"])
    address = object["address"]
    if "/" in address:
        address = address[0:address.index("/")]
    address += "Seattle, WA"
    distance_matrix = gmaps.distance_matrix(settings.ggAddress(), address, "driving", "", "", "imperial")
    distance = distance_matrix["rows"][0]["elements"][0]["distance"]
    print(distance)


#SEND EMAIL if it's within .1 miles of GG's house
mailServer = smtplib.SMTP('smtp.gmail.com', 587)
mailServer.ehlo()
mailServer.starttls()
mailServer.login(settings.emailLogin(), settings.emailPw())
msg = """From: Seattle FireWatcher <%s>
To: Test Recipient <%s>
Subject: SMTP e-mail test

This is a test e-mail message.
""" % (settings.sender(), settings.recipient())
mailServer.sendmail(settings.sender(), settings.recipient(), msg)

print ("Sent mail")



#OLD OLD OLD
#bodyVal = '{"id":"kzjm-xkqj","name":"Seattle Real Time Fire 911 Calls","attribution":"City of Seattle Fire Department MIS","attributionLink":"http://web5.seattle.gov/MNM/incidentresponse.aspx","category":"Public Safety","description":"Provides Seattle Fire Department 911 dispatches. Updated every 5 minutes.","displayType":"table","licenseId":"CC0_10","publicationAppendEnabled":true,"resourceName":"fire-911","columns":[{"id":3479077,"name":"Address","fieldName":"address","position":1,"description":"Location of Incident","width":227,"dataTypeName":"text","tableColumnId":1290345,"format":{},"flags":null,"metadata":{}},{"id":3479078,"name":"Type","fieldName":"type","position":3,"description":"Response Type","width":198,"dataTypeName":"text","tableColumnId":1290346,"format":{},"flags":null,"metadata":{}},{"id":3479079,"name":"Datetime","fieldName":"datetime","position":4,"description":"The date and time of the call.","width":222,"dataTypeName":"date","tableColumnId":1411673,"format":{"align":"left"},"flags":null,"metadata":{}},{"id":3479080,"name":"Latitude","fieldName":"latitude","position":5,"description":"This is the latitude value. Lines of latitude are parallel to the equator.","width":100,"dataTypeName":"number","tableColumnId":1290349,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479081,"name":"Longitude","fieldName":"longitude","position":6,"description":"This is the longitude value. Lines of longitude run perpendicular to lines of latitude, and all pass through both poles.","width":100,"dataTypeName":"number","tableColumnId":1290350,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479082,"name":"Report Location","fieldName":"report_location","position":7,"width":100,"dataTypeName":"location","tableColumnId":1393474,"format":{},"flags":null,"metadata":{}},{"id":3479083,"name":"Incident Number","fieldName":"incident_number","position":8,"width":100,"dataTypeName":"text","tableColumnId":1419260,"format":{"precisionStyle":"standard","align":"right"},"flags":null,"metadata":{}}],"metadata":{"custom_fields":{"Refresh Frequency":{"Frequency":"5 minutes"},"Data Owner":{"Owner":"Seattle Fire Department"}},"renderTypeConfig":{"visible":{"table":true}},"availableDisplayTypes":["table","fatrow","page"],"thumbnail":{"page":{"created":true}},"rdfSubject":"0","rowIdentifier":"0","rdfClass":"","jsonQuery":{"order":[{"columnFieldName":"datetime","ascending":false}]}},"query":{"orderBys":[{"ascending":false,"expression":{"columnId":3479079,"type":"column"}}]},"tags":["seattle","911","fire","dispatch e911","sfd mobile"],"flags":["default","restorable","restorePossibleForType"],"originalViewId":"kzjm-xkqj","displayFormat":{}}'
#test.request("POST", "/views/INLINE/rows.json?accessType=WEBSITE&method=getByIds&asHashes=true&start=0&length=50&meta=true", bodyVal)