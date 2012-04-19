#!/usr/bin/env python

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

class EventReader:
    provider = ""
    doc = None
    location = ""
    file_path = ""
    url = ""

    def __init__(self, from_file=False):
        if from_file:
            f = open(self.file_path)
        else:
            f = urlopen(self.url)

        page = ''.join(f.readlines())
        self.doc = BeautifulSoup(page)
        f.close()

    #----------------------------------------------------------------------
    def get_events(self):
        """
        virtual method
        """
        pass