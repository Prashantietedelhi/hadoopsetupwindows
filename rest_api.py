# encoding: utf-8
# Rest api
# Authors: <Singh, Prashant <Prashant.Singh@careerbuilder.com>>

'''
This module exposes the rest apis.

Available rest api's are:
getRecommendation
    Accept Method: POST
    Input: user demographic information in json format
    Output: result in json format contains the keys -> best_plan, reason and status.
    Header: Content-Type: application/json
    E.x:
        Input: Body: {
                        "EmployeeStatus":"Active",
                        "Gender":"Female",
                        "EmployeeAge":57,
                        "AnnualSalary":65894.86,
                        "NoofChildren":4,
                        "MaritalStatus":"Married",
                        "Spouse Relation":"Spouse",
                        "CompanyID":864	,
                        "EligibilePlanDesignIDs": "1#1-3-15-21"
                     }
              Header: Content-Type: application/json
              Output: {
                        "best_plan": "[{1: 1}]",
                        "reason": null,
                        "status": 200
                    }

'''

#!/usr/bin/env python
# coding: utf8

from common import get_logger
from insurance_recommendation import  InsuranceRecommendation

import os
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode
import configparser
####################### Config file reading

config_file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "config", "config.cfg")
config_obj = configparser.ConfigParser()

try:
    config_obj.read(config_file_loc)
    debugLevel = int(config_obj.get("REST","debuglevel"))
    logfilename = config_obj.get("REST","logfilename")
    ip = str(config_obj.get("REST", "ip"))
    port = int(config_obj.get("REST", "port"))
    parameters = str(config_obj.get("Common","parameters"))

except Exception as e:
    raise Exception("Config file reading error: "+str(e))

####################### Loggin Functionality

logfilename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logs", logfilename)
loggerobj = get_logger.GetLogger("Rest",logfilename,debugLevel)
logger = loggerobj.getlogger()

##################### Initializing all the objects

try:
    parameters_req = parameters.split(",")
    parameters_req = [i.strip().lower() for i in parameters_req]

except Exception as e:
    raise Exception(
        "Failed to extract parameters. Parameters should be string separated by quoma ','. failed reason : " + str(e))

response = {
    "status":"SUCCESS",
    "reason":""
    }
###################### Creating Recommendation object
BAD_REQUEST = 400
SUCCESS = 200
INTERNAL_SERVER_ERROR = 500

try:
    recommendation_obj = InsuranceRecommendation()
    logger.info("Successfully created the Recommendation object")

except Exception as e:
    logger.error("Failed to create the Recommendation object: "+str(e))
    raise Exception(e)

print("Recommendation REST API Started")
logger.info("Recommendation REST API Started")
class REST(tornado.web.RequestHandler):
    def post(self):
        '''
            Accept Method: POST
            Input: user demographic information in json format
            Output: result in json format contains the keys -> data, reason and status.
            Header: Content-Type: application/json
            :return:
            '''
        ###################### Status Code

        # logger.info("getRecommendation called")

        if self.request.method != 'POST':
            logger.error("getRecommendation: Only accept POST request")
            response["status"] = BAD_REQUEST
            response["best_plan"] = ""
            response["reason"] = "Only Accept POST request"
            print("Only Accept POST request")
            self.write(response)
            self.set_status(BAD_REQUEST)
        elif not self.request.headers['Content-Type'] == 'application/json':
            logger.error("getRecommendation: Only  Accept Content-Type:application/json")
            response["status"] = BAD_REQUEST
            response["best_plan"] = ""
            response["reason"] = "Only  Accept Content-Type:application/json"
            print("Only  Accept Content-Type:application/json")
            self.write(response)
            self.set_status(BAD_REQUEST)
        else:
            try:
                data = json_decode(self.request.body)
            except:
                logger.error(
                    'getRecommendation: Content_Type should be applicatin/json,Expecting json data key as : ' + str(
                        parameters))
                response["status"] = BAD_REQUEST
                response["best_plan"] = ""
                response["reason"] = 'Content_Type should be applicatin/json,Expecting json data key as : ' + str(
                    parameters)
                print('Content_Type should be applicatin/json,Expecting json data key as : ' + str(parameters))
                self.write(response)
                self.set_status(BAD_REQUEST)
            else:
                data = dict((k.lower().strip(), v) for k, v in data.items())

                try:
                    for parameter in parameters_req:
                        if parameter not in data.keys():
                            raise Exception()
                except:
                    logger.error("getRecommendation: Expecting key as : " + str(parameters))
                    response["status"] = BAD_REQUEST
                    response["best_plan"] = ""
                    response["reason"] = 'Expecting key as: ' + str(parameters)
                    print('Expecting key as: ' + str(parameters))
                    self.write(response)
                    self.set_status(BAD_REQUEST)
                else:

                    try:
                        insurance_plan = recommendation_obj.getRecommendation(data)
                    except Exception as e:
                        logger.error("getRecommendation: " + str(e))
                        response["status"] = INTERNAL_SERVER_ERROR
                        response["best_plan"] = ""
                        response["reason"] = str(e)
                        self.write(response)
                        self.set_status(INTERNAL_SERVER_ERROR)
                    else:
                        response["status"] = SUCCESS
                        response["reason"] = None
                        response["best_plan"] = str(insurance_plan)
                        self.write(response)
                        self.set_status(SUCCESS)

application = tornado.web.Application([
    (r"/getRecommendation", REST)
])

if __name__ == "__main__":
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()