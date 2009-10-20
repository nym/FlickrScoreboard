#!/usr/bin/python

import urllib2
import simplejson

class FlickrScoreboard:
    """
    A program to pull down pages of photos from Flickr's API,
    make a count of how many pictures each user contributed to the
    machine tag, and sort them.
    
    Usage:
    
    art  = FlickrScoreboard("burningman:art=")
    for user in art.top():
        print "%s (%d)" % (user['name'], user['count'])
    
    """

    config = {
        "flickr_url": "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=1c292fe000480c2c641cd9aec24d626f&format=json&extras=owner_name&nojsoncallback=1",
        "default_terms": "burningman"
        }

    def __init__(self, terms):
        self.terms = terms
        
        self.retreive_search_results()
        
        self.rankings = self.count_photos_by_user()
        self.rankings.reverse()

    def count_photos_by_user(self):
        self.count = {}
        for item in self.data:
            if self.count.get(item['ownername']) is None:
                self.count[item['ownername']] = 1
            else:
                self.count[item['ownername']] += 1

        # organize the results into a sorted rankings array
        rankings = []
        for user in self.count:
            rankings.append({ "name" : user, "count" : self.count[user] })
        
        rankings.sort(self.sort_by_count)
        
        return rankings

    def sort_by_count(self, a, b):
        return cmp(a['count'], b['count'])
        
    def retreive_search_results(self):
        # retrieve 1st result, use that to retrieve the rest
        append = "&per_page=500" + "&machine_tags=" + self.terms
        
        url = self.config['flickr_url'] + append
        
        pages = []
        
        pages.append(
            simplejson.loads(urllib2.urlopen(url + "&page=1").read())
            )
        page_num = pages[0]['photos']['pages']
        
        for i in range(2,page_num+1):
            pages.append(
                simplejson.loads(urllib2.urlopen("%s&page=%d" % (url, i)).read())
                )
        self.pages = pages
        self.concat_pages()

    def concat_pages(self):
        self.data = []
        for page in self.pages:
            for item in page['photos']['photo']:
                self.data.append(item)

    def top(self):
        """
        Return an array of the users sorted by their number of
        contributed photos
        """
        return self.rankings

    def __unicode__(self):
        """
        Print the top 10 users
        """
        out = ""
        for user in self.rankings[:10]:
            out += "%s (%d)\n" % (user['name'], user['count'])
        return out
