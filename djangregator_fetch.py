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
djangregator_sync.py

"""


import sys
import os
import logging

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_PATH, PROJECT_DIR = os.path.split(ROOT_PATH)

logging.basicConfig(level=logging.INFO)

logging.info('ROOT_PATH: %s' % ROOT_PATH)
logging.info('PROJECT_PATH: %s' % PROJECT_PATH)
logging.info('PROJECT_DIR: %s' % PROJECT_DIR)

sys.path.insert(0, ROOT_PATH)
sys.path.insert(1, PROJECT_PATH)

logging.info('sys.path: %s' % sys.path)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_DIR

logging.info('os.environ[DJANGO_SETTINGS_MODULE]: %s' % os.environ['DJANGO_SETTINGS_MODULE'])

from django.conf import settings
from datetime import *
import dateutil
from dateutil.parser import *


# fetch the delicious entries
logging.info('Checking for presence of Delicious username...')
if 'delicious' in settings.DJANGREGATOR_AUTH:
    import deliciousapi
    from djangregator.delicious.models import *
    logging.info('Delicious: syncing')
    items_created = 0
    delicious = deliciousapi.DeliciousAPI()
    for bookmark in delicious.get_bookmarks(username=settings.DJANGREGATOR_AUTH['delicious']):
        entry, created = DeliciousLink.objects.get_or_create(link=bookmark[0], title=bookmark[2], description=bookmark[3], published=bookmark[4])
        if created:
            items_created += 1
    logging.info('Delicious: synced %s new bookmarks.' % items_created)


# fetch the Twitter timeline
logging.info('Checking for presence of Twitter username...')
if 'twitter' in settings.DJANGREGATOR_AUTH:
    import twitter
    from djangregator.twitter.models import *
    logging.info('Twitter: syncing')
    items_created = 0
    twitter = twitter.Api()
    for status in twitter.GetUserTimeline(settings.DJANGREGATOR_AUTH['twitter']):
        tweetdate = datetime.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y')
        entry, created = TwitterStatus.objects.get_or_create(twitter_id=status.id, published=tweetdate)
        if created:
            entry.title = status.text
            entry.link = u'http://twitter.com/%s/%s' % (settings.DJANGREGATOR_AUTH['twitter'], status.id)
            entry.save()
            items_created += 1
    logging.info('Twitter: synced %s new tweets.' % items_created)


# fetch the flickr photos
logging.info('Checking for presence of Flickr username...')
if 'flickr' in settings.DJANGREGATOR_AUTH and 'flickr_api_key' in settings.DJANGREGATOR_AUTH:
    import flickrapi
    from djangregator.flickr.models import *
    logging.info('Flickr: syncing')
    items_created = 0
    flickr = flickrapi.FlickrAPI(settings.DJANGREGATOR_AUTH['flickr_api_key'], format='etree')
    recentphotos = flickr.people_getPublicPhotos(user_id=settings.DJANGREGATOR_AUTH['flickr_userid'], extras='date_upload, date_taken')
    iter = recentphotos.getiterator('photo');
    for photo in iter:
        upload_date = datetime.fromtimestamp(int(photo.attrib['dateupload']))
        entry, created = FlickrPhoto.objects.get_or_create(photo_id=photo.attrib['id'], published=upload_date)
        if created:
            entry.title = photo.attrib['title']
            entry.link = u'http://flickr.com/photos/%s/%s' % (
                settings.DJANGREGATOR_AUTH['flickr_userid'],
                entry.photo_id
            )
            base_url = u'http://farm%s.static.flickr.com/%s/%s_%s' % (
                photo.attrib['farm'],
                photo.attrib['server'],
                entry.photo_id,
                photo.attrib['secret']            
            )
            entry.square_thumb_link = base_url + u'_s.jpg'
            entry.image_500px_link = base_url + u'.jpg'
            entry.taken_on_date = dateutil.parser.parse(photo.attrib['datetaken'])
            entry.save()
            items_created += 1
    logging.info('Flickr: synced %s new photos.' % items_created)