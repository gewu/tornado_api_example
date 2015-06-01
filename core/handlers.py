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

import tornado.web
import tornado.httpclient

import pymongo
import urllib
import urllib2
import time
import os
import mmh3

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
#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------

class NAFHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
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
            sourcedb_result = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.insert(dinfo)
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect source db timeout"})
            return 

        self.params_stand(dinfo, sourcedb_result) #Assign to certain fields

        #form geom in mongodb
        for geo_field in ("siwei_link1_list", "siwei_link2_list", "current_path_list", "current_track_list"):
            dinfo[geo_field] = self.form_dict_geom(dinfo[geo_field])

        # insert into stand_db
        try:
            standdb_result = yield self.db_r.info.inte_naviapp_feedback.insert(dinfo)
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": "insert standard db fall"})
            return 

        self.jsonOk()

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
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
            sourcedb_result = yield self.db_s.ns_map_infoplat.rf_naviapp_feedback.insert(dinfo)
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect source db timeout"})
            return 

        self.params_stand(dinfo, sourcedb_result) #Assign to certain fields

        #form geom in mongodb
        for geo_field in ("siwei_link1_list", "siwei_link2_list", "current_path_list", "current_track_list"):
            dinfo[geo_field] = self.form_dict_geom(dinfo[geo_field])

        # insert into stand_db
        try:
            standdb_result = yield self.db_r.info.inte_naviapp_feedback.insert(dinfo)
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": "insert standard db fall"})
            return 
        
        self.jsonOk()

    def params_source(self, infos):
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
        infos['res_id'] = res_id
        hstr = "%snaviappfeedback" % infos['res_id']
        infos['mid'] = mmh3.hash64(hstr)[0]    #unique
        infos['intelligence_source'] = 31
        infos['dispatch_flag'] = 0
        infos['update_time'] = infos['commit_time']
    
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

