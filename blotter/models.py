from datetime import datetime
import pytz

from django.db import models
from bs4 import BeautifulSoup


class RawRecord:
    '''A hunk of raw HTML representing a blotter item'''

    def __init__(self, html):
        self._raw_html = html
        self.soup = BeautifulSoup(html, 'html.parser')

    @staticmethod
    def parse_section(section):
        '''given a section of the page, return a tuple with label and value'''

        label = section.find('div', {'class': 'col2'}).text.strip()
        value = section.find('div', {'class': 'col1'}).text.strip()
        return (' '.join(label.split()), ' '.join(value.split()))

    @property
    def parsed_case(self):
        '''return a blotter item parsed into a dictionary'''

        # mapping a few errant keys in our data to the django field names
        key_map_fix = {
            'Record ID': '_id',
            'Incident Date': 'date',
            'Time': 'time',
            'Title': 'title',
            'Location': 'location',
            'Summary': 'summary',
            'Adults Arrested': 'arrested'
        }

        # grab all the sections in this blotter item
        sections = self.soup.find_all('div', {'class': 'colmask'})

        # create an empty dictionary
        d = {}

        # loop over the sections
        for sec in sections:

            # call the parsing function to get the label and value
            parsed = self.parse_section(sec)

            # the label will be the dict key
            key = parsed[0]

            # see if the key is in our dict of keys to fix
            if key_map_fix.get(key):
                key = key_map_fix[key]

            # value is the second thing
            value = parsed[1]

            # if this is the date
            if 'date' in key:

                # parse it as a datetime
                value = datetime.strptime(value, '%B %d, %Y')

            # if this is the division info
            if 'Division' in key:

                # split out the shift info
                div, shift = value.split(' -- ')
                d['division'] = div
                d['shift'] = shift.replace('Shift ', '')
                continue

            # if this is the contact bit
            if 'Contact' in key:

                # split out the officer and phone number
                officer, number = value.split(' - ')
                d['officer'] = officer.strip()
                d['phone_number'] = number.strip()
                continue

            # add to the dictionary
            d[key] = value

        # split out the time information
        hour, minute, second = [int(x) for x in d['time'].split(':')]

        # grab the correct timezone
        mst_tz = pytz.timezone('America/Denver')

        # new dict item -- datetime
        d['incident_datetime'] = d['date'].replace(hour=hour,
                                                   minute=minute,
                                                   second=second).astimezone(mst_tz)

        # delete the date and time items
        del d['date']
        del d['time']

        return d


class Record(models.Model):
    '''A blotter item'''

    _id = models.PositiveIntegerField()
    incident_datetime = models.DateTimeField('incident date')
    division = models.CharField(max_length=200)
    shift = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    summary = models.TextField()
    arrested = models.CharField(max_length=100, blank=True)
    officer = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.incident_datetime)

    class Meta:
        ordering = ('-incident_datetime',)
