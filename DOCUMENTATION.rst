==========================
Djangregator Documentation
==========================

----------------------------------------------------------------
Getting, Installing, Configuring, and Understanding Djangregator
----------------------------------------------------------------

Installation
============

The easiest route to installing djangregator is from the python package index. Using your favorite terminal, type:

  easy_install djangregator

Alternatively, you can download djangregator yourself from the github page (http://github.com/idangazit/djangregator/) and put it somewhere in your python path.

Once it's visible to python, don't forget to add djangregator to your project's INSTALLED_APPS, and run manage.py syncdb to generate the tables which djangregator needs.

Finally, you'll need to set up a recurring, automated task to trigger fetching of updates from each of the remote services. This requires calling djangregator.fetch() from a python instance which is aware of django and knows how to find your project's settings. How you implement this is ultimately up to you and your platform; you can use the supplied djangregator_fetch.py script to accomplish this task:

    ``$ python djangregator_fetch.py --help`` provides usage and syntax.
    
    ``$ python djangregator_fetch.py`` -- will execute under the assumption that it resides in your project directory, that is to say in the directory containing your settings.py file. The default logging level is INFO, meaning that debug information is not displayed.
    
    ``$ python djangregator_fetch.py --loglevel=DEBUG --projectpath=/path/to/your/project`` -- will execute while outputting verbose/debug logging and using the project residing at the specified path.


Configuration
=============

In the interest of flexibility and writeability, djangregator's settings live in the database, not in the project settings.py file.

After adding djangregator to the INSTALLED_APPS and running a syncdb, fire up the admin site and take a look at the new tables:

**Djangregator**
 * Delicious Links
 * Flickr Photos
 * Lifestream Entries
 * Online Personas
 * Twitter Statuses

The configuration information all sits in the Online Personas. Each persona consists of a name and relevant identification details for one or more online services.

When you first create an online persona, you'll be presented with one blank entry for each online service. Fill in the persona name at the top and the details for each service you wish to use. If there are services you don't wish to use, simply leave them blank.

You can synchronize one persona with multiple accounts from the same online service (i.e. multiple twitter accounts), but the django admin interface doesn't make this straightforward. Once you've created a persona and entered details for the first account, click "save and continue editing" -- the admin interface will then generate the blank form fields necessary to configure the next account. Repeat the process as often as needed.

Once you're done with configuration don't forget to run ``djangregator_fetch.py`` in order to fetch the data from all of the remote services you've specified.

Service-specific configuration notes
------------------------------------

**Flickr**
    You must have an API key to talk with the flickr service. To generate one,
    visit http://www.flickr.com/services/api/keys/apply/. Flickr accounts in
    each Online Persona also have a field for something called an "API
    Secret", which is another bit of information you'll get with your API key.
    The API secret is not currently used by Djangregator, but that may change
    in the future.


Caveats / Known Issues
======================

Djangregator fetches the maximum allowed number of items from each of the online services during a fetch -- however djangregator makes no effort to backtrack and verify that it has not "missed" any items. If fetch is setup to occur every 10 minutes, and the user has created more than the fetchable number of items during that time, then the excess items simply go unnoticed.


Service-Specific Backend Notes and Limitations
==============================================

Each of the online services offer APIs with varying limitations. Notably, most of them require that you perform queries no more than a certain amount per time period, and they restrict the returned set to a certain maximum of elements. These limitations and quirks are documented here.


Twitter
-------
* Each query returns at most 20 most-recent tweets.
* Djangregator asks only for tweets newer than the latest tweet it already has.
* The API allows at most 70 queries per 1-hour period.


Flickr
------
* Each query returns at most 500 most-recent photos.
* Djangregator asks only for photos newer than the latest photo it already has.
* The API has no predetermined rate limit, their current rule-of-thumb is no more than one query per second.
* The current flickr backend does not handle sets, favorites, or anything except photos for the given account.
* To configure a flickr account, you must have


Delicious
---------
* Each query returns at most 50 most-recent bookmarks.
* The API's allows at most 1 query per second.


Frequently Asked Questions
==========================

**I'd like to fetch tweets/photos/etc. which are marked private in my feeds, but I don't see anywhere to configure that. What gives?**
    Djangregator was written with the use-case of integration with a blog,
    which is usually a public forum. If you have private items in your
    Flickr photostream, or you have made your tweets private, then it doesn't
    make very much sense to publicly display them elsewhere, does it?
    
    In other words: I don't have any use for this feature. If somebody comes
    up with a compelling reason to add it, I might. Otherwise, fork to your
    heart's content, it's easy with git.


**Why isn't there a backend for my favorite online service?**
    Because you haven't submitted a patch adding support for it yet.


**This is the stinkingest pile of code I've ever seen. What kind of developer are you?**
    Hey, I'm just starting out with django; this is my first stab at a
    reusable app. I tried a few different approaches when designing it and
    the one I ended up with seems to be the simplest solution that feels
    "django-ish" in nature. Critique welcome!