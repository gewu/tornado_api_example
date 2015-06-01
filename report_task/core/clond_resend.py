#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import urllib
import urllib2
import json
import logging
from pymongo import MongoClient 

CIP_API_URL = "" 
SIGN_KEY = ""

intelligence_dict = {10: "广播来源开通关闭情报", 11: "网页来源", 12: "微博抓取开通关闭情报" }

class Clond_resend:
    def __init__(self):
                
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("./Clond_resend.log")
        formatter = logging.Formatter('%(asctime)s :  %(message)s ')  
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.client = MongoClient("******", *****)
        self.table = self.client.info.inte_clond_reform

    def sign(self, d):

        dks = d.keys()
        dks.sort()
        l = []
        for k in dks:
            l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(d[k]), '')))
        s1 = '&'.join(l)
        s1 = s1.replace('%20', '+')
        s2 = s1 + SIGN_KEY
        sign_s = hashlib.md5(s2).hexdigest()
        return sign_s

    def report(self): 

        data = self.table.find({"dispatch_flag":3}).sort([("commit_time", -1)])

        for m in data:
            mid = m['mid']
 	    d = { "platform_id":'1',
              	  "priority": 100,
                  "x": 0,
                  "y": 0
                }
            d['data_id'] = m['mid']
            d['source_id'] = m['intelligence_source']
            d['title'] = "%s %s" % (m['linename'].encode("utf-8"),  intelligence_dict[d['source_id']])
            d['sign'] = self.sign(d)
            f = urllib2.urlopen(CIP_API_URL, urllib.urlencode(d))
            rtn = json.load( f )
            if rtn['errno'] == 0:
                self.logger.info("mid: %s" % mid)
                self.table.update({"mid":mid}, {"$set":{"dispatch_flag":1}})
            else :
                self.logger.error(rtn)
        self.client.close()

if __name__ == "__main__":
    
    clond_resend = Clond_resend()
    clond_resend.report()
    


