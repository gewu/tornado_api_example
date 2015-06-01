#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# Generate beautiful python code templates for lidonghui01.
#
#--------------------------------------------------------------
#
# Date:     2012-09-17
#
# Author:   gewu@baidu.com
#
#

import sys
import os
from datetime import date

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No file name specified"
    else:
        td = date.today()
        file_name = sys.argv[1]
        base_file_name = os.path.basename(file_name)
        class_name = base_file_name.split('.')[0] if '.' in base_file_name else base_file_name
        f = open(file_name, 'w')
        f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#--------------------------------------------------------------
#
# naviappfeedback
#               -- API for navigation app feedback source 
#
# %s: #TODO DESC HERE
#
#--------------------------------------------------------------
#
# Date:     %s
#
# Author:   gewu@baidu.com
#
#

#--------------------------------------------------------------
# Globl Constants & Functions
#--------------------------------------------------------------

#--------------------------------------------------------------
# Classes
#--------------------------------------------------------------
class %s(object):
    
    def __init__(self):
        pass

if __name__ == "__main__":
    pass
""" % (base_file_name, td.isoformat(), class_name))
        f.close()
