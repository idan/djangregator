About
=====

With a multitude of web services allowing you to share information about yourself in different places, it gets difficult to get a complete view of your activity without visiting many different sites. The solution espoused by many is aggregating all of your social news together into one unified, reverse-chronological list, often called a "lifestream".

There are already services like FriendFeed which accomplish this feat for you. Simply sign up and provide the details of your various social identities, and FriendFeed will provide you with the lifestream.

Djangregator is a Django application which makes it easy to provide a FriendFeed-style lifestream. Using the public APIs that are available for most social networking sites, djangregator will fetch new entries from each of your online identities and provide access to them as well-structured objects within the Django ORM.

Djangregator currently supports the following sources of information:

* Twitter
* Flickr (photos only, no sets)
* Delicious

I wrote it because I wanted to try my hand at a problem that was a little larger than just "Write a blog". Along the way I had to learn about signals, the ORM, writing template tags, model inheritance -- all sorts of subjects that one needs to grok before diving into something larger.


License
=======

Djangregator is yours to use according to the terms of the BSD license. The license text and terms may be read in a file named LICENSE.txt which should be in the same directory as this readme.


Requirements
============

Djangregator requires:

* Python 2.5
* Django 1.0

Sadly, there is no unified API for accessing different sites. The following libraries are required for interfacing with the relevant site. Note that if a library is not present, djangregator will simply skip that site, even if it has been configured in the settings.

* python-twitter - http://code.google.com/p/python-twitter/
* DeliciousAPI - http://pypi.python.org/pypi/DeliciousAPI
    * BeautifulSoup - required for DeliciousAPI
* FlickrAPI - http://flickrapi.sourceforge.net/
    * ElementTree - included in python 2.5 used by FlickrAPI
  
  
Credits
=======

Djangregator is heavily inspired by (read: blatantly ripped off from) several django luminaries' efforts. Each of these are worth reading and knowing if you are learning Django!

* Ryan Berg: the original inspiration for this project. Ryan shows how he implemented his aggregation system on his blog, which has been an endless source of wisdom and education.
    * http://ryanberg.net

* Horst Gutmann: is a talented blogger who also wrote a django application for dealing with lifestreams, appropriately titled "django-lifestream". He also has some very useful advice to impart about using generic relations in the Django ORM in his blog.
    * http://zerokspot.com
    * http://code.google.com/p/django-lifestream/

* Nuno Mariz: shows how to accomplish the same thing as djangregator with a lot less work by leveraging the fact that FriendFeed offers an API into its already-aggregated lifestream. The code for the cron script is largely based on his example.
    * http://mariz.org/blog/2008/apr/04/internet-lifestream-with-django/

* Jesse Legg: authored another project similar to djangregator, if "similar" were a synonym for "a lot more polished" and "written long before mine".
    * http://jesselegg.com/
    * http://code.google.com/p/django-syncr/