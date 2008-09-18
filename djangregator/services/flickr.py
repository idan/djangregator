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

from djangregator.models import FlickrPhoto, FlickrAccount
from datetime import datetime
from dateutil import parser
import calendar
import logging

def fetch(account):
    """
    Fetch a list of recent photos from the flickr servers using the supplied
    credentials, and save them to the DB.
    
    Returns a tuple containing the number of items created, and the number of 
    items updated or skipped.
    """
    
    import flickrapi
    items_existing = 0
    items_created = 0
    flickr = flickrapi.FlickrAPI(account.api_key, format='etree')
    
    # check that the nsid is present, if not fetch it and save to the model
    if not ta.userid:
        try:
            nsidd = flickr.people_findByUsername(username=account.username).user[0]['nsid']
        except:
            return (0, 0) # TODO: gperhaps a more useful exception handler?
        ta.nsid = nsid
        ta.save()
    
    # get the latest photo we already have
    try:
        latestphoto = FlickrPhoto.objects.latest()
        latestdate = latestphoto.published
    except:
        latestdate = datetime.datetime.min
    
    timestamp = calendar.timegm(latestdate)
    recentphotos = flickr.photos_search(userid=account.userid, per_page=500, min_upload_date=timestamp, extras='date_upload, date_taken')
    iter = recentphotos.getiterator('photo');
    for photo in iter:
        upload_date = datetime.fromtimestamp(int(photo.attrib['dateupload']))
        if upload_date <
        entry, created = FlickrPhoto.objects.get_or_create(photo_id=photo.attrib['id'], published=upload_date)
        if created:
            entry.title = photo.attrib['title']
            entry.link = u'http://flickr.com/photos/%s/%s' % (
                account.userid,
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
            entry.taken_on_date = parser.parse(photo.attrib['datetaken'])
            entry.save()
            items_created += 1
        else:
            items_existing += 1
    
    return (items_created, items_existing)