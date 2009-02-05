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
from django.db.models.manager import EmptyManager
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("djangregator_models")

##############################################################################
# Common/Abstract Djangregator Models
##############################################################################

class TimelineEntry(models.Model):
    """
    Generically related to one or more entries from an online service.
    """
    content_type = models.ForeignKey(ContentType)
    span_start = models.DateTimeField(blank=True, default=datetime.max)
    span_end = models.DateTimeField(blank=True, default=datetime.min)
    
    class Meta:
        ordering = ['-span_start']
        get_latest_by = 'span_start'
        verbose_name = 'Timeline Entry'
        verbose_name_plural = 'Timeline Entries'
    
    def __unicode__(self):
        if self.content_type:
            count = self.activities.count()
            m = self.content_type._meta
            base = u"%(count)i %(name)s" % ({
                'count' : count,
                'name' : m.verbose_name if count == 1 else m.verbose_name_plural   
            })
        else:
            base = u"Empty Timeline Entry"
        
        if self.span_start:
            return base + " at %s" % self.span_start.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return base
    
    def get_rendered_html(self):
        return self.content_object.get_rendered_html()
        #try:
        #    return self.content_object.get_rendered_html()
        #except AttributeError:
        #    pass
        #    #return mark_safe("<p>%s</p>" % self.content_object.__str__())
    
    def update_span(self):
        try:
            latest = self.activities.latest().published
            earliest = self.activities.order_by('published').get().published
        except Activity.DoesNotExist:
            logger.error("Timeline Entry has must have related activities in order to set the span.")
            return
        self.span_start = earliest
        self.span_end = latest
        

class Persona(models.Model):
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


class Account(models.Model):
    """
    An ancestor class which encapsulates the common credentials necessary
    to fetch information from an online service.
    """
    username = models.CharField(blank=False, max_length=100)
    active = models.BooleanField(default=True, help_text="Uncheck to disable synchronization with this account")
    batching = models.BooleanField(default=False, help_text="Check to batch nearby entries together in the timeline")
    batch_minutes = models.PositiveIntegerField(default=15, help_text="The window of time (in minutes) over which to batch events together in the timeline. If an entry is less than this number of minutes apart from an existing batch, it will be included in that batch.")
    persona = models.ForeignKey(Persona, related_name="accounts")
    
    def __unicode__(self):
        return self.username
    
    servicename = u'unknown service'
    
    def get_service(self):
        return self.servicename
    
    service = property(get_service)


class Activity(models.Model):
    """
    An ancestor class which encapsulates the common information which
    describes an activity from an online service.
    """
    published = models.DateTimeField(null=False, blank=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    timelineentry = models.ForeignKey(TimelineEntry, null=True, related_name="activities")
    account = models.ForeignKey(Account)
    
    class Meta:
        ordering = ['-published']
        get_latest_by = 'published'
        
    def __unicode__(self):
        return self.title or self.link
    
    def get_rendered_html(self):
        return mark_safe("<p>%s</p>" % self.__str__())
    
    def get_batch(self):
        # find the batch where:
        # the content_type matches this object's content_type
        # the span_start is gte the publication date - window
        # the span_end is lte the publication date + window
        content_type = ContentType.objects.get_for_model(type(self))
        window = timedelta(minutes=self.account.batch_minutes)
        earliest = self.published - window
        latest = self.published + window
        
        return TimelineEntry.objects.get(
            content_type=content_type,
            span_start__gte=earliest,
            span_end__lte=latest
        )


##############################################################################
# Twitter
##############################################################################

class TwitterAccount(Account):
    """
    Encapsulates all of the authentication credentials required for accesing
    tweets from a specific Twitter user.
    """
    
    class Meta:
        verbose_name = "Twitter Account"
        verbose_name_plural = "Twitter Accounts"
    
    servicename = u'twitter'


class TwitterStatus(Activity):
    """
    Represents a single tweet from Twitter.
    """
    twitter_id = models.PositiveIntegerField(blank=False, null=False, unique=True)
    
    class Meta:
        verbose_name = 'Twitter Status'
        verbose_name_plural = 'Twitter Statuses'

##############################################################################
# Delicious
##############################################################################

class DeliciousAccount(Account):
    """
    Encapsulates all of the authentication credentials required for accesing
    links from a specific Delicious user.
    """
    
    class Meta:
        verbose_name = "Delicious Account"
        verbose_name_plural = "Delicious Accounts"
    
    servicename = u'delicious'


class DeliciousLink(Activity):
    """
    Represents a single link from Delicious.
    """
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Delicious Link'
        verbose_name_plural = 'Delicious Links'
        
    def get_rendered_html(self):
        template_name = 'djangregator/timeline/deliciouslink.html'
        return render_to_string(template_name, {'entry': self})


##############################################################################
# Flickr
##############################################################################

class FlickrAccount(Account):
    """
    Describes all of the authentication credentials required for accesing
    photos from a specific Flickr user.
    """
    userid = models.CharField(blank=True, max_length=20, editable=False) 
    api_key = models.CharField(blank=False, max_length=32)
    api_secret = models.CharField(blank=True, max_length=20) # max 16?
    
    class Meta:
        verbose_name = "Flickr Account"
        verbose_name_plural = "Flickr Accounts"
    
    servicename = u'flickr'
    
    def __unicode__(self):
        return self.username or self.userid


class FlickrPhoto(Activity):
    """
    Represents a single photo from Flickr.
    """
    photo_id = models.PositiveIntegerField(blank=False, null=False, unique=True)
    square_thumb_link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    image_500px_link = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    taken_on_date = models.DateTimeField(blank=True, default=datetime.now)
    
    class Meta:
        verbose_name = 'Flickr Photo'
        verbose_name_plural = 'Flickr Photos'


##############################################################################
# Signals
##############################################################################

def activity_pre_save(sender, instance, **kwargs):
    """
    Pre-save handler which creates or updates TimelineEntry instances
    whenever service-specific activity instances are saved.
    """
    
    batching = instance.account.batching
    content_type = ContentType.objects.get_for_model(type(instance))
            
    if batching:
        try:
            tle = instance.get_batch()
        except instance.DoesNotExist:
            tle = TimelineEntry()
            tle.content_type = content_type
        except instance.MultipleObjectsReturned:
            logger.error("Found multiple TimelineEntries for %(name)s at %(date)s" % ({
                'name' : content_type.name,
                'date' : instance.published.strftime('%Y-%m-%d %H:%M:%S'),
            }))
            return
    else:
        tle = TimelineEntry()
        tle.content_type = content_type
    
    # must save the TLE before assignment otherwise it doesn't really get
    # assigned.
    tle.save()
    
    if instance.timelineentry != tle:
        oldtle = instance.timelineentry    
        instance.timelineentry = tle
        if oldtle is not None and oldtle.activities.count() == 0:
            oldtle.delete()

def activity_post_save(sender, instance, created, raw, **kwargs):
    instance.timelineentry.update_span()


for source in [TwitterStatus, DeliciousLink, FlickrPhoto,]:
    signals.pre_save.connect(activity_pre_save, source,
        dispatch_uid='djangregator.models')
    signals.post_save.connect(activity_post_save, source,
        dispatch_uid='djangregator.models')