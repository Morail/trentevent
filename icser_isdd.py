#!/usr/bin/env python

import sys

try:
    from icalendar import Calendar, Event, LocalTimezone
except:
    sys.path.append("icalendar-1.2-py2.5.egg")
    from icalendar import Calendar, Event, LocalTimezone

from htmldecode import decode_htmlentities, remove_html_tags
from eventreader import EventReader
from datetime import datetime, timedelta, tzinfo

default_event_duration = 3

        
########################################################################
class SuoniDelleDolomitiEventReader(EventReader):
    """
    Specialized for www.isuonidelledolomiti.it
    >>> scr = SuoniDelleDolomitiEventReader(True)
    >>> len([e for e in scr.get_events()])
    41
    """

    file_path = "test/data/elenco_%s.txt" % (datetime.today().year,)
    url = "http://www.isuonidelledolomiti.it/cms-01.00/template/st200/fileElEventi/elencoEventi_7906_L1.js"

        
    def get_events(self):
        import re

        events_desc = str(self.doc).split('];')

        # we append the local timezone to each time so that icalendar will convert
        # to UTC in the output
        lt = LocalTimezone()

        base_url = 'http://www.isuonidelledolomiti.it'

        re_url = re.compile('/IT/.*/\?s=\d+')
        re_hours = re.compile('ore (\d{1,2})')
        
        for e in events_desc:

            print e

            location, description, summary = '', '', ''
            date_, hour_ = None, None

            if not e.startswith('Eventi['):
                print 'Not an ISDD event'
                continue

            a = e.split(' = ')

            p = remove_html_tags(decode_htmlentities(a[1])).strip().decode("utf-8")
            if not p:
                continue

            list_ = p[1:-1].split('\',')
            #print list, len(list)

            event = Event()
        
            try:

                date_ = list_[2][1:].split('/')
                print date_

                if date_:

                    try:
                        print list_[4][1:]
                        hours_match = re.search(re_hours, list_[4][1:])
                        if hours_match:
                            print 'MATCH!', hours_match.group()
                            hour_ = hours_match.group().split(' ')[1]
                            print hour_
                        else:
                            hour_ = 0
                    except ValueError:
                        print "ValueError while retrieving hour"
                        hour_ = 0

                    datestart = datetime(int(date_[2]), int(date_[1]), int(date_[0]), int(hour_), tzinfo=lt)
                    dateend = datestart + timedelta(hours=default_event_duration)

                else:
                    print "NON TROVO DATA", p
                    continue

                print "DateStart: ", datestart
                print "DateEnd: ", dateend

                location = list_[-1][1:]
                #print "location: ", location
                summary = list_[1][1:]
                #print "summary: ", summary
                description = list_[-2][2:]
                #print "description: ", description

                url_match = re.search(re_url, p)
                if url_match:
                    url = base_url + url_match.group()
                    if description:
                        description = description + " - " + url
                    else :
                        description = url

                event.add('dtstart', datestart)
                event.add('dtstamp', datestart) # maybe it's better to use NOW()
                event.add('dtend', dateend)

                #print summary, location, description

                event.add('location', location)
                event.add('description', description)
                event.add('summary', summary)
                
                #TODO: add other info like the date!!
                
                event['uid'] = list_[0][1:]

                yield event
            except:
                print 'ERRORE', sys.exc_info()[0]
                print p
                print
                continue
    

def main():
    """
    :rtype : None
    """
    scr = SuoniDelleDolomitiEventReader(True)
    events = scr.get_events()
    
    cal = Calendar()
    #cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('summary', 'I Suoni delle Dolomiti')

    for event in events:
        cal.add_component(event)
    
    f = open('isdd.ics', 'wb')
    try:
        f.write(cal.to_ical())
    except:
        f.write(cal.as_string())

    f.close()

if __name__ == "__main__":
    main()
