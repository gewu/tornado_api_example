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

from pymongo import MongoClient
import urllib
import json
import time

from base import BaseHandler
from config import CONFIG

from tornado import gen
from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------

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
    @property
    def db(self):
        if not hasattr(self, "_db"):
            #self._db = motor.MotorClient('10.48.23.144', 27017)
            self._db = MongoClient('10.48.23.144', 27017)
        return self._db

    def post(self):
        dinfo = self.storinfo()
        # insert into source_db
        try:
            #sourcedb_result = yield self.db.test.naviappfeedback.update({"ugc_id":1000}, dinfo, upsert=True)
            sourcedb_result = self.db.test.naviappfeedback.update({"ugc_id":1000}, dinfo, upsert=True)
        except pymongo.errors.ConnectionFailure:
            self.jsonError({"msg": "connect mongodb timeout"})
            return 
        
        if sourcedb_result['err'] is not None:
            self.jsonError({"msg": sourcedb_result['err']})
            return 

        if sourcedb_result['updatedExisting'] is True:
            self.jsonError({"msg":"ugc_id is duplicated"})
            return 
        
        dinfo['mid'] = sourcedb_result['upserted']
        # insert into stand_db
        try:
            standdb_result = self.db.info.inte_naviapp_feedback.insert(dinfo)
        except pymongo.errors.PyMongoError as e:
            self.jsonError({"msg": e})
            return 

        self.jsonOk()

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
                self.jsonError({"msg":error})
        
        infos['dispatch_status'] = 1
        infos['commit_time'] = time.time()
        infos['province'] = 'beijing'
        infos['city'] = 'beijing'

        return infos

    def trans_coordinate(self, coor_str):
        if coor_str == "":
            return coor_str
        coor_list = coor_str.split(",")
        xgeom = coor_list[::2]
        ygeom = coor_list[1::2]

        return map(list, zip(xgeom, ygeom))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
