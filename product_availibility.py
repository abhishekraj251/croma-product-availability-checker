import requests
from time import sleep
import time
import schedule
import smtplib
import json
from datetime import datetime

#The item id/product code which is usually present on the product page or it's URL
product_code = "230955"

pincode = "831005"

#Croma inventory API endpoint
url = "https://api.croma.com/inventory/oms/v2/details-pwa"

recipient_email_id = "xxx@domain.com"

sender_email_id = "xxx@domain.com"

sender_email_password = "xxxxx"

headers = {
    'content-type': "application/json",
    'authority': "api.croma.com",
    'referer': "https://www.croma.com/",
    'origin': "https://www.croma.com/",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    'cache-control': "no-cache",
    }

payload  = {
   "promise":{
      "allocationRuleID":"SYSTEM",
      "checkInventory":"Y",
      "organizationCode":"CROMA",
      "sourcingClassification":"EC",
      "promiseLines":{
         "promiseLine":[
            {
               "fulfillmentType":"HDEL",
               "itemID":product_code,
               "lineId":"1",
               "reEndDate":"2500-01-01",
               "reqStartDate":"",
               "requiredQty":"1",
               "shipToAddress":{
                  "company":"",
                  "country":"",
                  "city":"",
                  "mobilePhone":"",
                  "state":"",
                  "zipCode":pincode,
                  "extn":{
                     "irlAddressLine1":"",
                     "irlAddressLine2":""
                  }
               },
               "extn":{
                  "widerStoreFlag":"N"
               }
            },
            {
               "fulfillmentType":"STOR",
               "itemID":product_code,
               "lineId":"2",
               "reqEndDate":"",
               "reqStartDate":"",
               "requiredQty":"1",
               "shipToAddress":{
                  "company":"",
                  "country":"",
                  "city":"",
                  "mobilePhone":"",
                  "state":"",
                  "zipCode":pincode,
                  "extn":{
                     "irlAddressLine1":"",
                     "irlAddressLine2":""
                  }
               },
               "extn":{
                  "widerStoreFlag":"N"
               }
            },
            {
               "fulfillmentType":"SDEL",
               "itemID":product_code,
               "lineId":"3",
               "reqEndDate":"",
               "reqStartDate":"",
               "requiredQty":"1",
               "shipToAddress":{
                  "company":"",
                  "country":"",
                  "city":"",
                  "mobilePhone":"",
                  "state":"",
                  "zipCode":pincode,
                  "extn":{
                     "irlAddressLine1":"",
                     "irlAddressLine2":""
                  }
               },
               "extn":{
                  "widerStoreFlag":"N"
               }
            }
         ]
      }
   }
}

def check_stock():
    response = requests.request("POST", url, data=str(payload), headers=headers)

    response = json.loads(response.text)

    #The 'promiseLine' key returns an empty list in case of product unavailability
    availibility_list = response.get('promise')['suggestedOption']['option']['promiseLines']['promiseLine']

    if availibility_list:
        delivery_date = availibility_list[0]['assignments']['assignment'][0]['deliveryDate']
        dt = datetime.strptime(delivery_date, "%Y-%m-%dT%H:%M:%S.%f%z").date()

        message = "The product with code {} is available and can be delivered by ".format(product_code) + str(dt)
        sendemail(message, product_code)
    
    else:
        print("No stocks available. I'll check back in sometime.")


def sendemail(message, subject):
    gmail_username = sender_email_id
    gmail_password = sender_email_password
    recipient = recipient_email_id
    body_of_email = message
    email_subject = subject
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    s.login(gmail_username, gmail_password)
    # message to be sent
    headers = "\r\n".join(["from: " + gmail_username,
                            "subject: " + email_subject,
                            "to: " + recipient,
                            "mime-version: 1.0",
                            "content-type: text/html"])

    content = headers + "\r\n\r\n" + body_of_email
    s.sendmail(gmail_username, recipient, content)
    s.quit()


def job():
    print("Checking inventory for available stocks..")
    check_stock()

def heart_beat():
    print("Script is running")
    sendemail("The bot is running.", "Bot heartbeat")
 
schedule.every(5).minutes.do(job)

schedule.every(60).minutes.do(heart_beat)
 
while True:
    # running all pending tasks/jobs
    schedule.run_pending()
    time.sleep(1)