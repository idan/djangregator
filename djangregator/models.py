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


from django.db import models
from django.db.models import signals
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

##############################################################################
# Common/Abstract Djangregator Models
##############################################################################

class TimelineEntry(models.Model):
    """
    Generically related to an entry from any online service.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    published = models.DateTimeField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-published']
        get_latest_by = 'published'
        verbose_name = 'Timeline Entry'
        verbose_name_plural = 'Timeline Entries'
    
    def __unicode__(self):
        return self.content_object.__str__()


class OnlinePersona(models.Model):
    """
    Generically related to one or more different service accounts.
    """
    name = models.CharField(null=False, blank=False, max_length=100)
    
    class Meta:
        ordering = ['name',]
        verbose_name = "Online Persona"
        verbose_name_plural = "Online Personas"
    
    def __unicode__(self):
        return self.name
    
    def accounts(self):
        related_managers = [getattr(self, method) for method in dir(self) if method.endswith('_accounts')]
        accounts = []
        for related in related_managers:
            for account in related.iterator():
                accounts.append(account)
        return accounts
            


class AbstractActivityEntry(models.Model):
    """
    An abstract base class which encapsulates the common information which
    describes activities from all sources of online activity.
    """
    published = models.DateTimeField(null=False, blank=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    timelineentry = generic.GenericRelation(TimelineEntry)
    
    class Meta:
        ordering = ['-published']
        get_latest_by = 'published'
        abstract = True
        
    def __unicode__(self):
        return self.title or self.link


class AbstractServiceAccount(models.Model):
    """
    Encapsulates the common credentials necessary to fetch information from
    any online service. Extend this class to implement support for a new
    online service.
    """
    username = models.CharField(blank=False, max_length=100)
    active = models.BooleanField(default=True, help_text="Uncheck to disable synchronization with this account")
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.username
        
    def service(self):
        return self.servicename or u'unknown service'



##############################################################################
# Twitter
##############################################################################

class TwitterAccount(AbstractServiceAccount):
    """
    Encapsulates all of the authentication credentials required for accesing
    tweets from a specific Twitter user.
    """
    persona = models.ForeignKey(OnlinePersona, related_name="twitter_accounts")
    
    class Meta:
        verbose_name = "Twitter Account"
        verbose_name_plural = "Twitter Accounts"
    
    service = u'twitter'


class TwitterStatus(AbstractActivityEntry):
    """
    Represents a single tweet from Twitter.
    """
    account = models.ForeignKey(TwitterAccount, related_name="tweets")
    twitter_id = models.PositiveIntegerField(blank=False, null=False, unique=True)
    
    class Meta(AbstractActivityEntry.Meta):
        verbose_name = 'Twitter Status'
        verbose_name_plural = 'Twitter Statuses'    
    
    servicename = u'twitter'

##############################################################################
# Delicious
##############################################################################

class DeliciousAccount(AbstractServiceAccount):
    """
    Encapsulates all of the authentication credentials required for accesing
    links from a specific Delicious user.
    """
    persona = models.ForeignKey(OnlinePersona, related_name="delicious_accounts")
    
    class Meta:
        verbose_name = "Delicious Account"
        verbose_name_plural = "Delicious Accounts"
    
    service = u'delicious'


class DeliciousLink(AbstractActivityEntry):
    """
    Represents a single link from Delicious.
    """
    account = models.ForeignKey(DeliciousAccount, related_name="links")
    description = models.TextField(blank=True)
    
    class Meta(AbstractActivityEntry.Meta):
        verbose_name = 'Delicious Link'
        verbose_name_plural = 'Delicious Links'
    
    servicename = u'delicious'



##############################################################################
# Flickr
##############################################################################

class FlickrAccount(AbstractServiceAccount):
    """
    Describes all of the authentication credentials required for accesing
    photos from a specific Flickr user.
    """
    persona = models.ForeignKey(OnlinePersona, related_name="flickr_accounts")
    userid = models.CharField(blank=True, max_length=20, editable=False) 
    api_key = models.CharField(blank=False, max_length=32)
    api_secret = models.CharField(blank=True, max_length=20) # max 16?
    
    class Meta:
        verbose_name = "Flickr Account"
        verbose_name_plural = "Flickr Accounts"
    
    def __unicode__(self):
        return self.username or self.userid
    
    service = u'flickr'


class FlickrPhoto(AbstractActivityEntry):
    """
    Represents a single photo from Flickr.
    """
    account = models.ForeignKey(FlickrAccount, related_name="photos")
    photo_id = models.PositiveIntegerField(blank=False, null=False, unique=True)
    square_thumb_link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    image_500px_link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    taken_on_date = models.DateTimeField(blank=True, default=datetime.now)
    
    class Meta(AbstractActivityEntry.Meta):
        verbose_name = 'Flickr Photo'
        verbose_name_plural = 'Flickr Photos'
    
    servicename = u'flickr'

##############################################################################
# Signals
##############################################################################

def update_timeline(sender, instance, created, raw, **kwargs):
    """
    Post-save handler which creates or updates TimelineEntry instances
    whenever service-specific model instances are saved.
    """
    if created:
        item = TimelineEntry()
        item.content_type = ContentType.objects.get_for_model(type(instance))
        item.object_id = instance.id
    else:
        item = instance.timelineentry.all()[0]
    item.published = instance.published
    item.save()


for source in [TwitterStatus, DeliciousLink, FlickrPhoto,]:
    signals.post_save.connect(update_timeline, source,
        dispatch_uid='djangregator.models')