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


from djangregator.models import DeliciousLink, DeliciousAccount
import logging

logger = logging.getLogger("Delicious")

def fetch(account):
    """
    Fetch a list of recent bookmarks from the delicious servers using the
    supplied credentials, and save them to the DB.
    
    Returns a tuple containing the number of items created, and the number of 
    items updated or skipped.
    """
    
    # python 2.6-safe import of json module:
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImportError:
            import django.utils.simplejson as json
            
    import urllib
    import dateutil.parser
    
    items_existing = 0
    items_created = 0
    feedurl = "http://feeds.delicious.com/v2/json/%s" % account.username
    bookmarks = json.load(urllib.urlopen(feedurl))
    for bookmark in bookmarks:
        timestamp = dateutil.parser.parse(bookmark['dt'])
        entry, created = DeliciousLink.objects.get_or_create(
            account = account,
            link = bookmark['u'],
            published = timestamp)
        if created:
            entry.title = bookmark['d']
            entry.description = bookmark['n']
            entry.save()
            items_created += 1
        else:
            items_existing += 1
    
    return (items_created, items_existing)