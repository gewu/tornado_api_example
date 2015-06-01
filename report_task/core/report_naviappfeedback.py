#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# IntelUniq
#               -- Intelligence shall be unique 
#
# report_naviappfeedback.py: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     2015-05-27
#
# Author:   gewu@baidu.com
#
#

from pymongo import MongoClient
from sendtask import Sendtask

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------
intelligence_dict = {31:"导航APP本地用户反馈"}
#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------
class report_naviappfeedback(Sendtask):
    
    def __init__(self):
        super(report_naviappfeedback, self).__init__()
        self.client = MongoClient("10.48.23.144", 27017)
        self.table = self.client.info.inte_naviapp_feedback

    def report_data(self):
        data = self.table.find({"intelligence_source":31, "dispatch_flag":0}).sort([("commit_time",-1)]).limit(100)
        for m in data:
            d = {}
            d['data_id'] = m['mid']
            d['source_id'] = m['intelligence_source']
            d['title'] = "%s %s" % (m['linename'].encode("utf-8"),  intelligence_dict[d['source_id']])

            flag = self.report(d)
            if flag['errno'] == 0:
                self.table.update({"mid":m['mid']}, {"$set":{"dispatch_flag":1}})
                self.logger_i.info("mid:%s" % m['mid'])
            else:
                self.logger_e.error("mid:%s report fail" % m['mid'])

if __name__ == "__main__":
    rn = report_naviappfeedback()
    rn.report_data()

