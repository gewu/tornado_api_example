#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# naviappfeedback
#               -- API for navigation app feedback source 
#
# testapi.py: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     2015-05-17
#
# Author:   gewu@baidu.com
#
#

import urllib
import urllib2
import json

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------

#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------
class testapi(object):
    
    def __init__(self):
        pass
    
    def test_naviappfeedback_handler(self):
        url = 'http://127.0.0.1:8888/api/naviappfeedback/'
        info = {
                 'ugc_id' : "999",
                 'administrative_division_id': "3",
                 'user_flag_data' : "4",
                 'siwei_link1_id' : "1424124",
                 'siwei_link1_list':"[[1,2], [3,4]]",
                 'linename' : 'beijing',
                 'create_time': "2015-05-06"

               }

        f = urllib2.urlopen(url, urllib.urlencode(info))
        result = json.load( f )
        print result
    
    def gen_data(self):
        info = {
                'administrative_division_id': "3",
                'user_flag_data' : "4",
                'siwei_link1_id' : "1424124",
                'siwei_link1_list':"[[1,2], [3,4]]",
                'linename' : 'beijing',
                'create_time': "2015-05-06"
               }

        with open("post_data", "w") as f:
            for i in range(100):
                info['ugc_id'] = i
                f.write("%s\n" % urllib.urlencode(info))


if __name__ == "__main__":

    ta = testapi()
    ta.gen_data()
   # ta.test_naviappfeedback_handler()
