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

def fetch(credentials):
    """
    Fetch a list of recent photos from the flickr servers using the supplied
    credentials, and save them to the DB.
    
    Returns a tuple containing the number of items created, and the number of 
    items updated or skipped.
    """   
    
    from djangregator.backends.flickr.models import *
    import flickrapi
    
    items_existing = 0
    items_created = 0
    flickr = flickrapi.FlickrAPI(credentials['api_key'], format='etree')
    recentphotos = flickr.people_getPublicPhotos(user_id=credentials['userid'], extras='date_upload, date_taken')
    iter = recentphotos.getiterator('photo');
    for photo in iter:
        upload_date = datetime.fromtimestamp(int(photo.attrib['dateupload']))
        entry, created = FlickrPhoto.objects.get_or_create(photo_id=photo.attrib['id'], published=upload_date)
        if created:
            entry.title = photo.attrib['title']
            entry.link = u'http://flickr.com/photos/%s/%s' % (
                credentials['userid'],
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
        else:
            items_existing += 1
    
    return (items_created, items_existing)