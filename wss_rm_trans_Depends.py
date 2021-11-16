#!/usr/bin/env python3

import sys
import json
import requests
import time

## Global Vars 
user_key        = sys.argv[1]
org_token       = sys.argv[2]
api_url         = "https://app.whitesourcesoftware.com/api/v1.3"
request_headers = {'Content-type': 'application/json'}

def main():
    print("\n\n-- START OF SCRIPT --\n\n")
    
    numberOfIgnoredAlerts = 0
    allProductsTokens = []
    allProjectsTokens = []


    # Get All Products Tokens
    # - - - - - - - - - - - - - - - - - - - - - - - - 
    request_data = {
        "requestType" : "getAllProducts",
        "userKey" : user_key,
        "orgToken" : org_token,
    }
    response = requests.post(api_url, 
                            headers = request_headers, 
                            data=json.dumps(request_data))
    print("Grabbing all Product Tokens : {}".format(response))

    productJsonGlob = json.loads(response.content)
    #print(json.dumps(productJsonGlob, indent=2, sort_keys=True))

    for item in productJsonGlob["products"]:
        #print("{}:{}".format(item["productName"],item["productToken"]))
        allProductsTokens.append(item["productToken"])

    print("-\n\n-")

    # Get All Projects Tokens
    # - - - - - - - - - - - - - - - - - - - - - - - - 
    for product in allProductsTokens:
        # Sleep to prevent request limit
        time.sleep(3)

        request_data = {
            "requestType" : "getAllProjects",
            "userKey" : user_key,
            "productToken" : "{}".format(product),
        }

        response = requests.post(api_url, 
                                headers = request_headers, 
                                data=json.dumps(request_data))
        print("Grabbing all Project Tokens : {}".format(response))

        projectJsonGlob = json.loads(response.content)
    
        #print(json.dumps(projectJsonGlob, indent=2, sort_keys=True))

        for item in projectJsonGlob["projects"]:
            #print("{}:{}".format(item["projectName"],item["projectToken"]))
            allProjectsTokens.append(item["projectToken"])


    print("-\n\n-")

    # Parse out Alerts based on each Project
    # - - - - - - - - - - - - - - - - - - - - - - - - 
    for project in allProjectsTokens:
        time.sleep(2)
        request_data = {
            "requestType" : "getProjectAlerts",
            "userKey" : user_key,
            "projectToken" : project,
        }

        response = requests.post(api_url, 
                                headers = request_headers, 
                                data=json.dumps(request_data))
        print("\nGrabbing all Alerts Based on Project Tokens : {}".format(response))

        projectAlertsGlob = json.loads(response.content)

        print("Number of Alerts:{}".format(len(projectAlertsGlob["alerts"])))

        alertsUUIDGlob = []

        # Parse out all ""directDependency": false"
        # - - - - - - - - - - - - - - - - - - - - - - - - 
        for alert in projectAlertsGlob["alerts"]:
            if "{}".format(alert["directDependency"]) == "False":
                #print("False:{}".format(alert["directDependency"]))
                alertsUUIDGlob.append("{}".format(alert["alertUuid"]))
            #else:
                #print("True:{}".format(alert["directDependency"]))
        
        print("Ignore Alerts Array:{}".format(alertsUUIDGlob))
        print("Ignore Number of Alerts:{}".format(len(alertsUUIDGlob)))

        numberOfIgnoredAlerts = numberOfIgnoredAlerts + int(len(alertsUUIDGlob))


        # Take Parsed directDependencies and set WhiteSource to Ignore the Alerts
        # - - - - - - - - - - - - - - - - - - - - - - - - 
        request_data = {
            "requestType" : "ignoreAlerts",
            "userKey" : user_key,
            #"orgToken" : org_token,
            "projectToken" : "{}".format(project),
            "alertUuids" : alertsUUIDGlob,
            "comments": "Transitive Dependencies (We do Not Fix Third Party Code)"
        }

        time.sleep(2)
        response = requests.post(api_url, 
                                headers = request_headers, 
                                data=json.dumps(request_data))
        print("Removing Transitive Dependencies: {}\n".format(response))


    print("\n\nNumber Of Alerts Ignored : {}\n\n".format(numberOfIgnoredAlerts))

    print("\n\n-- END OF SCRIPT --\n\n")

    # request_data = {
    #     "requestType" : "getProjectAlerts",
    #     "userKey" : user_key,
    #     "projectToken" : "",
    # }

    # response = requests.post(api_url, 
    #                         headers = request_headers, 
    #                         data=json.dumps(request_data))
    # print("\nGrabbing all Alerts Based on Project Tokens : {}".format(response))

    # projectAlertsGlob = json.loads(response.content)

    # # Used to Create Files to save Json Globs for Development
    # # - - - - - - - - - - - - - - - - - - - - - - - - 
    # with open('t.txt', 'w') as f:
    #     sys.stdout = f # Change the standard output to the file we created.
    #     print(json.dumps(projectAlertsGlob, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()