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


from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

"""
    Filters useful for marking up a lifestream.
"""

register = template.Library()

# (?:\A|[\s\.,:;'"])(@(\w{1,15}))(?!\.?\w)
twitterize_pattern = r'''
    (?:                 # non-capturing group
        \A              # start: match the beginning of line
        | [\s\.,:;'"]   # or any of: whitespace, period, comma, colon, etc...
    )
    (                   # capture group \1, this is where the @username is
        @(\w{1,15})     # @ followed by 1-15 char word captured into \2
    )
    (?!                 # but don't match if followed by
        \.?             # zero or one periods
        \w              # followed by any word character
    )'''

twitterize_replace = r'''
@<a class="tweetreply" href="http://twitter.com/\2">\2</a>'''

twitterize_regex = re.compile(twitterize_pattern, re.VERBOSE)

@register.filter()
@stringfilter
def twitterize(value, autoescape=None):
    """
    Converts all "@replies" in plain text into clickable links, while trying
    to ignore red herrings like email addresses, invalid twitter usernames.
    
    @replies can have some leading punctuation or trailing punctuation,
    but cannot
    """ 
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = twitterize_regex.sub(twitterize_replace, esc(value))
    return mark_safe(result)
twitterize.is_safe = True
twitterize.needs_autoescape = True

# TODO: Implement some test fixtures.
# A sample string to test against...
# @yes XXX @yes:yyy XXX @yes: yyy XXX @no.com XXX @yes XXX foo@no.net @yes XXX @yes15characters XXX @notoomanycharacters XXX thank you @yes. @yes asdas@no.com @no.c foo:@yes XXX @yes,@yes;