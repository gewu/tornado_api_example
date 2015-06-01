#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# naviappfeedback
#               -- API for navigation app feedback source 
#
# api.py: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     2015-05-15
#
# Author:   gewu@baidu.com
#
#

__version__ = "0.0.1"
__version_info__ = __version__.split(".")

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

import motor
import pymongo
import urllib
import urllib2
import json
import time
import os
import hashlib
import mmh3

from base import BaseHandler
from config import CONFIG

from tornado import gen
from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------
delim = "G"  # geom delim
CIP_API_URL = "http://testugc.map.baidu.com:8482/task-manager/task/import"
#CIP_API_URL = "http://task-private.ugc.map.baidu.com:8080/task/import"
SIGN_KEY = "Luffyinfo20140723@@xyzGoodLucy!!"

intelligence_dict = {31:"导航APP本地用户反馈"}

def sign(d):
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

#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                    (r"/api/naviappfeedback/?", NAFHandler),
                   ]
        seetings = dict(
                site_title = u"Intelligence System api 1.0"
                        )
        tornado.web.Application.__init__(self, handlers, **seetings)

class NAFHandler(BaseHandler):
    @property           #source db
    def db_s(self):
        if not hasattr(self, "_dbs"):
            self._dbs = motor.MotorClient('10.48.52.62', 27017)
        return self._dbs
    @property           #reform db
    def db_r(self):
        if not hasattr(self, "_dbr"):
            self._dbr = motor.MotorClient('10.48.23.144', 27017)
        return self._dbr

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        status, dinfo = self.storinfo()
        if status == "error":
            self.jsonError({"msg":status})
            return 

        # insert into source_db
        try:
            #sourcedb_result = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.update(\
            #                  {"ugc_id":dinfo['ugc_id']}, dinfo, upsert=True, w=True)
            sourcedb_result = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.insert(dinfo)
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect mongodb timeout"})
            return 
        '''
        dinfo['res_id'] = sourcedb_result.get("upserted", "ERROR")
        if dinfo['res_id'] == "ERROR":
            self.jsonError({"msg": "insert source_db ERROR, ugc_id is duplicated"})
            return 
        '''

        dinfo['res_id'] = sourcedb_result
        hstr = "%snaviappfeedback" % dinfo['res_id']
        dinfo['mid'] = mmh3.hash64(hstr)[0]    #unique
        dinfo['intelligence_source'] = 31
        dinfo['dispatch_flag'] = 0

        #form geom in mongodb
        for geo_field in ("siwei_link1_list", "siwei_link2_list", "current_path_list", "current_track_list"):
            dinfo[geo_field] = self.form_dict_geom(dinfo[geo_field])

        # insert into stand_db
        try:
            standdb_result = yield self.db_r.info.inte_naviapp_feedback.insert(dinfo)
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": e})
            return 
        
        self.jsonOk()

        '''
        #report task platform
        task_d = self.gentask(dinfo)
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(CIP_API_URL, method='POST', body=urllib.urlencode(task_d))
        rtn = yield http_client.fetch(request)
      
        ret = json.loads(rtn.body)
        print ret
        if ret['errno'] == 0:
            self.jsonOk()
        else:
            self.jsonError({'msg': "report task platform Error"})
        '''

    def gentask(self, m):
        d = { "platform_id":'1',
              "priority": 100,
              "x": 0,
              "y": 0
            }
        d['data_id'] = m['mid']
        d['source_id'] = m['intelligence_source']
        d['title'] = "%s %s" % (m['linename'].encode("utf-8"),  intelligence_dict[d['source_id']])
        d['sign'] = sign(d)

        return d

    def report(self, m, API_URL):
        d = { "platform_id":'1',
              "priority": 100,
              "x": 0,
              "y": 0
            }
        d['data_id'] = m['mid']
        d['source_id'] = m['intelligence_source']
        d['title'] = "%s %s" % (m['linename'].encode("utf-8"),  intelligence_dict[d['source_id']])
        d['sign'] = sign(d)

        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(API_URL, method='POST', body=urllib.urlencode(d))
        rtn = http_client.fetch(request, self.rtn_output)

    def storinfo(self):
        params = CONFIG['naviappfeedback']['api'].split(",")
        infos = {}
        for param in params:
            param = param.strip()
            infos[param] = self.get_argument(param, "")

        params_check = ("ugc_id", "administrative_division_id", "user_flag_data",\
                       "siwei_link1_id", "siwei_link1_list", "linename")
        for pc in params_check:
            if infos[pc] == "":
                error = "Error: %s is empty" % pc
                return "error", error
        
        infos['dispatch_flag'] = 1
        infos['commit_time'] = int(time.time())
        
        timeArray = time.strptime(infos['create_time'], "%Y-%m-%d %H:%M:%S")
        infos['create_time'] = int(time.mktime(timeArray)) 

        cities = CONFIG['naviappfeedback']['city_area']
        adid = int(infos['administrative_division_id'])
        infos['province'] = ""
        if adid in range(0, len(cities)):
            infos['province'] = cities[adid]
        
        infos['city'] = infos['province']

        return "ok", infos
    
    def form_dict_geom(self, geom_str):
        if geom_str == "":
            return geom_str
        geom_str = self.trans_geom(geom_str)
        return dict(type="LineString", coordinates=self.form_geom(geom_str))

    def trans_geom(self, geo_str):
        geolist = geo_str.split(",")
        ret = str(float(geolist[0])/100000)
        for i in xrange(1, len(geolist)):
            if i % 2 != 0:
                ret = "%s,"%ret
            else :
                ret = "%s%s"%(ret, delim)                           
            ret = "%s%s"%(ret, float(geolist[i])/100000)

        output = os.popen('../coordtrans/a.out gcj02ll bd09ll %s' % ret)
        return output.read()

    def form_geom(self, geom_str):
        if geom_str == "":
            return geom_str
        geom_list = map(float, geom_str.split(",")[:-1])
        xgeom = geom_list[::2]
        ygeom = geom_list[1::2]

        return map(list, zip(xgeom, ygeom))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
