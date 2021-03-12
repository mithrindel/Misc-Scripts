#!/usr/bin/python

import os
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


###SCRIPT VARIABLE###
recordingPath_root = r'\\XXX'
averageFileSizeCriteria = 5000 #bytes

smtpServer = 'XXX'
smtpPort = 25
fromaddr = 'XXX'
toaddr = 'XXX'

###Checks day recording size if not on Saturday or Sunday. Send a Mail if file exist and is too small###
def checkRecordingSize():

    date = datetime.date.today()
    year = date.strftime("%Y")
    month = date.strftime("%m").lstrip('0')
    day = date.strftime("%d").lstrip('0')
    
    folderSize = 0
    nbFiles = 0
    averageFileSize = 0
    
    try:
        recordingPath_date = os.path.join(recordingPath_root, year, month, day)
        
        print ("[checkRecordingSize] - Checking recording average size...")
        
        for root, dirs, files in os.walk(recordingPath_date):
            for recordingFile in files:
                recordingFile = os.path.join(os.path.abspath(root),recordingFile)
                folderSize += os.path.getsize(recordingFile) 
                nbFiles += 1  
        
        averageFileSize = round(folderSize/nbFiles)
        
        print('[checkRecordingSize] - averageFileSize =', averageFileSize/1000, 'KB')
        
        if(averageFileSize < averageFileSizeCriteria):
            print ("[checkRecordingSize] - Average file size abnormally small")
            sendMail("[WARNING] - Average file size abnormally small")
        else:
            print ("[checkRecordingSize] - Average size OK")
            sendMail("[OK] - Average file size OK")
            
    except:
        print ("[checkRecordingSize] - ERROR")
        sendMail("[WARNING] - Error running script")
        
    return

###Send an email using the global variable on top of script. Message content is variable msg###
def sendMail(mailContent):

    try:
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = mailContent
 
        body = ''
        msg.attach(MIMEText(body, 'plain'))
 
        server = smtplib.SMTP(smtpServer, 25)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        
        print("[sendMail] - Mail sending SUCCESS")

    except:
        print("[sendMail] - Mail sending FAIL")

    return

    
###Used to clear the console screen where script is launched###
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


###Main function of the script###
def main():
    clear_screen()
    print ('\n\n')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\t*                                                           *')
    print ('\t*         Welcome to the XXXXXXXX Morning Check             *')
    print ('\t*                                                           *')
    print ('\t*                Developed by mithrindel                    *')
    print ('\t*                                                           *')
    print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print ('\n\n')
    print ("[main_menu] - checkRecordingSize call")
    time.sleep(1)
    checkRecordingSize()
    print ("[main_menu] - End of the execution")
    time.sleep(2)


if __name__ == '__main__':
    main()

