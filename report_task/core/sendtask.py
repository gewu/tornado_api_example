#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# SendTask
#               -- report task from mongo
#
# sendtask.py: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     2015-05-27
#
# Author:   gewu@baidu.com
#
#

import hashlib
import urllib
import urllib2
import json
import logging
import logging.config

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------
CIP_API_URL = "http://testugc.map.baidu.com:8482/task-manager/task/import"
#CIP_API_URL = "http://task-private.ugc.map.baidu.com:8080/task/import"
SIGN_KEY = "Luffyinfo20140723@@xyzGoodLucy!!"
#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------
class Sendtask(object):
    
    def __init__(self):
        logging.config.fileConfig("../conf/logging.conf")
        self.logger_i = logging.getLogger('report')
        self.logger_e = logging.getLogger('err')
        
    def sign(self, d):
        l = []
        for k in sorted(d.keys()):
            l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(d[k]), '')))
        s1 = '&'.join(l)
        s1 = s1.replace('%20', '+')
        s2 = s1 + SIGN_KEY
        sign_s = hashlib.md5(s2).hexdigest()
        return sign_s
            
    def report(self, info):
        task_d = {"platform_id":1,
                  "priority":100,
                  "x":0,
                  "y":0,
                 }
        for key, value in task_d.items():
            info.setdefault(key, value)
        
        info['sign'] = self.sign(info)
        f = urllib2.urlopen(CIP_API_URL, urllib.urlencode(info))
        rtn = json.load( f )
        
        return rtn
        


