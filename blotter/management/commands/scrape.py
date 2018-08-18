import time

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from blotter.models import RawRecord, Record


class Command(BaseCommand):
    help = 'Scrapes the Colorado Springs Police Department blotter.'

    BASE_URL = 'http://www.springsgov.com/units/police/policeblotter.asp'

    HEADERS = {
        'name': 'Cody Winchester',
        'email': 'cjwinchester@gmail.com',
        'github': 'https://github.com/cjwinchester/cspd-blotter'
    }

    def get_record_count(self):
        '''return the number of records to iterate through.'''

        r = requests.get(self.BASE_URL, headers=self.HEADERS)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'html.parser')

        # find the one bold tag on the page
        bold = soup.find('b').string.strip()
        return int(bold.split()[-1])

    def handle(self, *args, **options):
        '''scrape the CPSD blotter into the db'''

        # how many records to iterate through?
        record_count = self.get_record_count()

        # loop over range from 0 to record_count by 10s
        # to get the correct `offset` parameter
        for i in range(0, record_count, 10):

            # get the page with the offset
            r = requests.get(self.BASE_URL,
                             headers=self.HEADERS,
                             params={'offset': i})

            r.raise_for_status()

            # split the html on the <hr> tags, keep only those with
            # a Record ID (i.e., a blotter item)
            cases = [x for x in r.text.split('<hr>') if 'Record ID' in x]

            # loop over the cases
            for case in cases:

                # hand the HTML off to our nifty class
                raw = RawRecord(case)

                # get the parsed dictionary
                parsed = raw.parsed_case

                # create or update a database record
                obj, created = Record.objects.update_or_create(**parsed)

                # print something to let us know what's happening
                print(obj, created)

            time.sleep(2)
