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
test = http.client.HTTPSConnection('data.seattle.gov')
test.request("GET", uri)
newtest = test.getresponse()

#Parse JSON
jsonTest = json.loads(newtest.read().decode('utf-8')) #is a list of dicts
print(jsonTest)

#Determine which addresses are close to GG's
# GG's address: 11301 3rd Ave NE Seattle, WA 98125
for object in jsonTest:
    print(object["address"])

gmaps = googlemaps.Client(key=settings.apiKey())
distance = gmaps.distance_matrix('7100 Jennifer Way Sykesville, MD', '7100 Jennifer Way Sykesville, MD', "driving", "", "", "imperial")
print(distance["rows"][0]["elements"][0]["distance"])


#SEND EMAIL if it's within .5 miles of GG's house
mailServer = smtplib.SMTP('smtp.gmail.com', 587)
mailServer.ehlo()
mailServer.starttls()
mailServer.login(settings.emailLogin(), settings.emailPw())
msg = """From: Seattle FireWatcher <%s>
To: Test Recipient <%s>
Subject: SMTP e-mail test

This is a test e-mail message.
""" % (settings.sender(), settings.recipient())
mailServer.sendmail("seafirewatcher@gmail.com", "luke.wiedeman@gmail.com", msg)

print ("Sent mail")



#OLD OLD OLD
#bodyVal = '{"id":"kzjm-xkqj","name":"Seattle Real Time Fire 911 Calls","attribution":"City of Seattle Fire Department MIS","attributionLink":"http://web5.seattle.gov/MNM/incidentresponse.aspx","category":"Public Safety","description":"Provides Seattle Fire Department 911 dispatches. Updated every 5 minutes.","displayType":"table","licenseId":"CC0_10","publicationAppendEnabled":true,"resourceName":"fire-911","columns":[{"id":3479077,"name":"Address","fieldName":"address","position":1,"description":"Location of Incident","width":227,"dataTypeName":"text","tableColumnId":1290345,"format":{},"flags":null,"metadata":{}},{"id":3479078,"name":"Type","fieldName":"type","position":3,"description":"Response Type","width":198,"dataTypeName":"text","tableColumnId":1290346,"format":{},"flags":null,"metadata":{}},{"id":3479079,"name":"Datetime","fieldName":"datetime","position":4,"description":"The date and time of the call.","width":222,"dataTypeName":"date","tableColumnId":1411673,"format":{"align":"left"},"flags":null,"metadata":{}},{"id":3479080,"name":"Latitude","fieldName":"latitude","position":5,"description":"This is the latitude value. Lines of latitude are parallel to the equator.","width":100,"dataTypeName":"number","tableColumnId":1290349,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479081,"name":"Longitude","fieldName":"longitude","position":6,"description":"This is the longitude value. Lines of longitude run perpendicular to lines of latitude, and all pass through both poles.","width":100,"dataTypeName":"number","tableColumnId":1290350,"format":{"precisionStyle":"standard"},"flags":null,"metadata":{}},{"id":3479082,"name":"Report Location","fieldName":"report_location","position":7,"width":100,"dataTypeName":"location","tableColumnId":1393474,"format":{},"flags":null,"metadata":{}},{"id":3479083,"name":"Incident Number","fieldName":"incident_number","position":8,"width":100,"dataTypeName":"text","tableColumnId":1419260,"format":{"precisionStyle":"standard","align":"right"},"flags":null,"metadata":{}}],"metadata":{"custom_fields":{"Refresh Frequency":{"Frequency":"5 minutes"},"Data Owner":{"Owner":"Seattle Fire Department"}},"renderTypeConfig":{"visible":{"table":true}},"availableDisplayTypes":["table","fatrow","page"],"thumbnail":{"page":{"created":true}},"rdfSubject":"0","rowIdentifier":"0","rdfClass":"","jsonQuery":{"order":[{"columnFieldName":"datetime","ascending":false}]}},"query":{"orderBys":[{"ascending":false,"expression":{"columnId":3479079,"type":"column"}}]},"tags":["seattle","911","fire","dispatch e911","sfd mobile"],"flags":["default","restorable","restorePossibleForType"],"originalViewId":"kzjm-xkqj","displayFormat":{}}'
#test.request("POST", "/views/INLINE/rows.json?accessType=WEBSITE&method=getByIds&asHashes=true&start=0&length=50&meta=true", bodyVal)