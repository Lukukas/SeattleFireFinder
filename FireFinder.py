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
today = today - datetime.timedelta(hours=12)
uri = "/resource/grwu-wqtk.json?$query=SELECT%20datetime,%20address,%20type,%20incident_number%20WHERE%20datetime%20>%20\""
uri += today.strftime('%Y-%m-%dT%H:%M:%S.%f')
uri += '"'

#Gather info from Seattle.gov website
seaData = http.client.HTTPSConnection('data.seattle.gov')
header = {"X-App-Token":"xD7zm0umu9QcSt9uH72IidCNx"}
try:
    seaData.request("GET", uri, "", header)
except Exception:
    logging.exception("Get Request to Seattle.gov")
seaDataJson = seaData.getresponse()

#Parse JSON
seaList = json.loads(seaDataJson.read().decode('utf-8')) #is a list of dicts
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
        print(object)
    distance = distance_matrix["rows"][0]["elements"][0]["distance"]
    if 'ft' in distance["text"]:
        testMsg = """From: Seattle FireWatcher <%s>
        To: Test Recipient <%s>
        Subject: 911 call close to %s

    A 911 call was placed from %s.
    This is about %s from %s.
    Call Type: %s.

    For more info: http://www2.seattle.gov/fire/realtime911/getDatePubTab.asp
        """ % (settings.sender(), settings.donRecipient(), settings.ggAddress(), address, distance["text"], settings.ggAddress(), object["type"])
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
            try:
                mailServer.sendmail(settings.sender(), settings.donRecipient(), testMsg)
            except:
                logging.exception("Send Email")
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
    try:
        mailServer.sendmail(settings.sender(), settings.recipient(), msg)
    except Exception:
        logging.exception("Send Daily Email")
    print("Sent mail")
