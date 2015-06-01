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
import tornado.web

from handlers import NAFHandler
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
                site_title = u"Intelligence System api 1.0",
                debug = True
                        )
        tornado.web.Application.__init__(self, handlers, **seetings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
