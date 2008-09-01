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
#   * Neither the name of Pixane nor the names of its contributors
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

from django.db import models
from django.db.models import signals
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from tagging.fields import TagField
from tagging.models import Tag
import datetime

class LifestreamItem(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    published = models.DateTimeField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-published']
        get_latest_by = 'published'
        verbose_name = 'Generic Lifestream Entry'
        verbose_name_plural = 'Generic Lifestream Entries'


class ActivityEntry(models.Model):
    published           = models.DateTimeField(null=False, blank=False)
    title               = models.CharField(max_length=255, null=True, blank=True)
    link                = models.URLField(max_length=255, verify_exists=False, null=True, blank=True)
    tags                = TagField()
    lifestream_item     = generic.GenericRelation(LifestreamItem)
    
    class Meta:
        ordering = ['-published']
        verbose_name = 'Entry'
        verbose_name_plural = 'Entries'
        get_latest_by = 'published'
        abstract = True
        
    def __unicode__(self):
        return self.title or self.link
    
    def get_tags(self):
        return Tag.objects.get_for_object(self)
    

def update_lifestream_entry(sender, instance, created, raw, **kwargs):
    if created:
        item = LifestreamItem()
        item.content_type = ContentType.objects.get_for_model(type(instance))
        item.object_id = instance.id
    else:
        item = instance.lifestream_item.all()[0]
    item.published = instance.published
    item.save()
