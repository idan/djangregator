#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2008, Idan Gazit
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the author nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
This script can be used as a cron script to trigger periodic fetching of new
activity from the various online services configured in your project.
"""


import sys
import os
import logging
from optparse import OptionParser

CURRENT_PATH = os.path.realpath(os.path.dirname(__file__))

usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-l", "--loglevel",
                  dest="loglevel",
                  help="Logging verbosity level, one of (DEBUG, INFO, WARNING, ERROR, FATAL) [default: %default]",
                  default="INFO",
                  metavar="LOGLEVEL")
parser.add_option("-p", "--projectpath",
                  dest="projectpath",
                  help="Path to the django project (the directory containing the settings.py file)",
                  default=CURRENT_PATH,
                  metavar="PATH"
                  )

(options, args) = parser.parse_args()

logging.basicConfig(
    level=logging.getLevelName(options.loglevel),
    format="%(asctime)s | %(levelname)8s: %(name)s | %(message)s")
    
logger = logging.getLogger("djangregator_fetch")

selectedpath = os.path.realpath(os.path.normpath(options.projectpath))

if not os.path.exists(selectedpath):
    logger.critical('The specified directory does not exist: "%s"' %
                        selectedpath)

logger.info('Project Path: %s' % selectedpath)
PATH_HEAD, PATH_TAIL = os.path.split(selectedpath)
logger.debug('Project Path Head: %s' % PATH_HEAD)
logger.debug('Project Path Tail: %s' % PATH_TAIL)

os.chdir(options.projectpath)

sys.path.insert(0, selectedpath)
sys.path.insert(1, PATH_HEAD)

logger.debug('sys.path: %s' % sys.path)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PATH_TAIL

logger.debug('os.environ[DJANGO_SETTINGS_MODULE]: %s' % 
                os.environ['DJANGO_SETTINGS_MODULE'])

# check that the project actually has djangregator installed & tables created?
try:
    import djangregator
except ImportError:
    logger.critical("Unable to import Djangregator, aborting.")
else:
    djangregator.fetch()