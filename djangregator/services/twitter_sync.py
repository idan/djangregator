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

from djangregator.models import TwitterStatus, TwitterAccount
from datetime import datetime

def fetch(twitteruser):
    """
    Fetch a list of recent tweets from the twitter servers using the supplied
    credentials, and save them to the DB.
    
    Returns a tuple containing the number of items created, and the number of 
    items updated or skipped.
    """
    
    import twitter
    import rfc822
    import datetime
    items_existing = 0
    items_created = 0
    twitterapi = twitter.Api()
    
    # get the latest tweet we already have
    try:
        latesttweet = TwitterStatus.objects.latest()
        latestdate = latesttweet.published.strftime("%a %b %d %H:%M:%S +0000 %Y")
    except:
        latestdate = datetime.min.strftime("%a %b %d %H:%M:%S +0000 %Y")
        
    for status in twitterapi.GetUserTimeline(user=twitteruser.username, since=latestdate):
        try:
            tweetdate = datetime.datetime(*rfc822.parsedate(status.created_at)[:6])
        except: # TODO: more specific exception handling?
            continue
        
        entry, created = TwitterStatus.objects.get_or_create(twitter_id=status.id, published=tweetdate)
        if created:
            entry.title = status.text
            entry.link = u'http://twitter.com/%s/%s' % (twitteruser.username, status.id)
            entry.save()
            items_created += 1
        else:
            items_existing += 1
    
    return (items_created, items_existing)