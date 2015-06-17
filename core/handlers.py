#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""naviappfeedback api handle"""
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

import tornado.web
import tornado.httpclient

import pymongo
import urllib
import urllib2
import time
import os
import mmh3
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_DIR = os.path.join(BASE_DIR, "conf")
os.sys.path.insert(0, CONF_DIR)

from base import BaseHandler
from config import CONFIG
from tornado import gen

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------
delim = "G"  # geom delim
#DATA_API_URL = "http://testugc.map.baidu.com:8482/task-manager/task/data_id"
#DATA_API_URL = "http://task-private.ugc.map.baidu.com:8080/task/data_id"
#PRIORITY_API_URL = "http://testugc.map.baidu.com:8482/task-manager/task/update/priority"
PRIORITY_API_URL = "http://task-private.ugc.map.baidu.com:8080/task/update/priority"


#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------

class NAFHandler(BaseHandler):
    """naviappfeedback handle"""

    def post(self):
        """post method"""
        self.common()

    def get(self):
        """get method"""
        self.common()

    @tornado.web.asynchronous
    @gen.coroutine
    def common(self):
        """common method"""
        params_a = CONFIG['naviappfeedback']['api'].split(",")
        dinfo = self.storinfo(params_a)
        
        params_c = CONFIG['naviappfeedback']['check'].split(",")
        status, msg = self.params_check(params_c, dinfo)
        if status is False:
            self.jsonError({"msg":msg})
            return 
        
        self.params_source(dinfo) #Assign to certain fields

        # insert into source_db
        try:
            sourcedb_result = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.insert(dinfo)  #online database
            #sourcedb_result = yield self.db_s.test_db.rf_naviapp_feedback.insert(dinfo)           #offline databases
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect source db timeout"})
            return 

        self.params_stand(dinfo, sourcedb_result) #Assign to certain fields

        #form geom in mongodb
        for geo_field in ("siwei_link1_list", "siwei_link2_list",\
                          "current_path_list", "current_track_list"):
            dinfo[geo_field] = self.form_dict_geom(dinfo[geo_field])

        # insert into stand_db
        try:
            standdb_result = yield self.db_r.info.inte_naviapp_feedback.insert(dinfo)     #online offline same name
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": "insert standard db fall"})
            return 
        
        self.jsonOk()

    def params_source(self, infos):
        """params to source DB"""
        infos["user_flag_data"] = int(infos["user_flag_data"])
        if infos["influence_surface"] != "":
            infos["influence_surface"] = float(infos["influence_surface"])
        if infos["repeat_num"] != "":
            infos["repeat_num"] = int(infos["repeat_num"])
        if infos['create_time'] != "":
            timeArray = time.strptime(infos['create_time'], "%Y-%m-%d %H:%M")
            infos['create_time'] = int(time.mktime(timeArray))

        cities = CONFIG['naviappfeedback']['city_area']
        adid = int(infos['administrative_division_id'])
        infos['province'] = ""
        if adid in range(0, len(cities)):
            infos['province'] = cities[adid]
        infos['city'] = infos['province']

    def params_stand(self, infos, res_id):
        """params to stand DB"""
        infos['issue_time'] = infos.pop("create_time")
        infos['res_id'] = res_id
        hstr = "%snaviappfeedback" % infos['res_id']
        infos['mid'] = mmh3.hash64(hstr)[0]    #unique
        infos['intelligence_source'] = 31
        infos['dispatch_flag'] = 0
        infos['update_time'] = infos['commit_time']
    
    def form_dict_geom(self, geom_str):
        """form dict geom"""
        if geom_str == "":
            return geom_str
        geom_str = self.trans_geom(geom_str)
        return dict(type="LineString", coordinates=self.form_geom(geom_str))

    def trans_geom(self, geo_str):
        """trans geom"""
        geolist = geo_str.split(",")
        ret = str(float(geolist[0])/100000)
        for i in xrange(1, len(geolist)):
            if i % 2 != 0:
                ret = "%s," % ret
            else:
                ret = "%s%s" % (ret, delim)                           
            ret = "%s%s" % (ret, float(geolist[i])/100000)

        #output = os.popen('/home/map/users/gewu/feedback_api/coordtrans/a.out gcj02ll bd09ll %s' % ret)   #online
        output = os.popen('../coordtrans/a.out gcj02ll bd09ll %s' % ret)    #offline
        return output.read()

    def form_geom(self, geom_str):
        """form geom"""
        if geom_str == "":
            return geom_str
        geom_list = map(float, geom_str.split(",")[:-1])
        xgeom = geom_list[::2]
        ygeom = geom_list[1::2]

        return map(list, zip(xgeom, ygeom))


class NAFUpdateHandler(BaseHandler):
    """update naviappfeedback data"""
    def get(self):
        """get method"""
        self.common()

    def post(self):
        """post method"""
        self.common()
    
    @tornado.web.asynchronous
    @gen.coroutine
    def common(self):
        "common method"
        #get params
        updateInfo = {}
        updateInfo["repeat_num"] = self.get_argument("repeat_num", "")
        updateInfo["influence_surface"] = self.get_argument("influence_surface", "")
        updateInfo["ugc_id"] = self.get_argument("ugc_id", "")

        #params check
        if updateInfo['ugc_id'] == "":
            self.jsonError({"msg": "ugc_id is empty"})
            return 
        if updateInfo["repeat_num"] == "":
            updateInfo.pop("repeat_num")
        else:
            updateInfo["repeat_num"] = int(updateInfo["repeat_num"])
        if updateInfo["influence_surface"] == "":
            updateInfo.pop("influence_surface")
        else:
            updateInfo["influence_surface"] = float(updateInfo["influence_surface"])

        #update sourceDB
        try:
	                                     #test: test_db	
            sourceDbResult = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.update(\
                {"ugc_id":updateInfo['ugc_id']}, {"$set": updateInfo})
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect source db timeout"})
            return 

        if sourceDbResult.get("updatedExisting") == False:
            self.jsonError({"msg":"This ugc_id is not in db"})
            return 

        # update stand_db
        try:
            standDbResult = yield self.db_r.info.inte_naviapp_feedback.find_and_modify(\
                    {"ugc_id":updateInfo['ugc_id']}, {"$set": updateInfo}, full_response=True)
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": "update standard db fall"})
            return 
        
        if standDbResult["value"]["dispatch_flag"] == 0:
            self.jsonOk()
            return 

        priority = standDbResult["value"]["repeat_num"]
        taskD = {
                 "platform_id": 1,
                 "mids": standDbResult["value"]["mid"],
                 "priority": priority
                }

        taskD['sign'] = self.sign(taskD)
        
        httpClient = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(PRIORITY_API_URL,\
                  method='POST', body=urllib.urlencode(taskD))
        rtn = yield httpClient.fetch(request)
        jsRtn = json.loads(rtn.body)
        if jsRtn["data"]:
            if jsRtn["data"].get("result", "") == "success":
                self.jsonOk()
                return 
        else:
            self.jsonError({"msg": "update fail: %s" % jsRtn["errmsg"]})


