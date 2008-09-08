#!/usr/bin/env python
# encoding: utf-8

# Copyright (c) 2008, Idan Gazit
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of the author nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This script can be used as a cron script to trigger periodic fetching of new
activity from the various online services configured in your project.
"""


import sys
import os
import logging
import djangregator

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_PATH, PROJECT_DIR = os.path.split(ROOT_PATH)

#logging.basicConfig(level=logging.INFO)

logging.info('ROOT_PATH: %s' % ROOT_PATH)
logging.info('PROJECT_PATH: %s' % PROJECT_PATH)
logging.info('PROJECT_DIR: %s' % PROJECT_DIR)

sys.path.insert(0, ROOT_PATH)
sys.path.insert(1, PROJECT_PATH)

logging.info('sys.path: %s' % sys.path)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_DIR

logging.info('os.environ[DJANGO_SETTINGS_MODULE]: %s' % os.environ['DJANGO_SETTINGS_MODULE'])

djangregator.fetch()