#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base Handle class"""
#
#--------------------------------------------------------------
#
# Base handlers.
#
#--------------------------------------------------------------
#
# Date:             2015-05-15
# Author:           gewu@baidu.com
#
# Last-Modified:    gewu@baidu.com
# Modified-Date:    2015-05-15
#
#

'''
__version__ = "0.0.1"
__version_info__ = __version__.split('.')
'''

import hashlib
import motor
import urllib
import urllib2
import tornado.web
import time
from tornado.escape import json_encode

#--------------------------------------------------------------
# Global Constants & Vars
#--------------------------------------------------------------
intelligence_dict = {31:"导航APP本地用户反馈"}
#CIP_API_URL = "http://testugc.map.baidu.com:8482/task-manager/task/import"
#CIP_API_URL = "http://task-private.ugc.map.baidu.com:8080/task/import"
SIGN_KEY = "Luffyinfo20140723@@xyzGoodLucy!!"

#--------------------------------------------------------------
# Global Functions
#--------------------------------------------------------------

#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------

class BaseHandler(tornado.web.RequestHandler):
    """Base Handler"""
    @property           #source db
    def db_s(self):
        """connect to the source DB"""
        if not hasattr(self, "_dbs"):
            self._dbs = motor.MotorClient('10.48.52.62', 27017)
        return self._dbs

    @property           #reform db
    def db_r(self):
        """connect to the stand DB"""
        if not hasattr(self, "_dbr"):
            #self._dbr = motor.MotorClient('10.48.23.144', 27017)  #1012 stand db
            self._dbr = motor.MotorClient('10.40.18.12', 27017)  #03 stand db
        return self._dbr

    @property
    def rc(self):
        """rc"""
        return self.application.rc

    def jsonOk(self, d=None):
        """return OK json"""
        d_ = {"errno": 0, "msg": "ok"}
        if d:
            d_.update(d)
        self.set_header("Content-Type", "application/json")
        self.finish(json_encode(d_))

    def jsonError(self, d=None):
        """return ERROR json"""
        d_ = {"errno": -1, "msg": "unknown error"}
        if d:
            d_.update(d)
        self.set_header("Content-Type", "application/json")
        self.finish(json_encode(d_))

    def gentask(self, m):
        """gen task infor"""
        d = {"platform_id":'1',
              "priority": 100,
              "x": 0,
              "y": 0
            }
        d['data_id'] = m['mid']
        d['source_id'] = m['intelligence_source']
        d['title'] = "%s %s" % (m['linename'].encode("utf-8"), intelligence_dict[d['source_id']])
        d['sign'] = sign(d)

        return d

    def params_check(self, params, infos):
        """check params"""
        for ps in params:
            if infos[ps.strip()] == "":
                return (False, "ERROR: %s is empty" % ps)
        return (True, "")
    
    def sign(self, d):
        """get sign value"""
        l = []
        for k in sorted(d.keys()):
            l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(d[k]), '')))
        s1 = '&'.join(l)
        s1 = s1.replace('%20', '+')
        s2 = s1 + SIGN_KEY
        sign_s = hashlib.md5(s2).hexdigest()
        return sign_s

    def storinfo(self, params):
        """store infomation"""
        infos = {}
        for param in params:
            param = param.strip()
            infos[param] = self.get_argument(param, "")

        infos['dispatch_flag'] = 1
        infos['commit_time'] = int(time.time())

        return infos 
