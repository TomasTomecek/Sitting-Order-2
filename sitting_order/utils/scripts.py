# -*- coding: utf-8 -*-

import csv
import re

import sys, os
sys.path.insert(0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))))

from pprint import pprint

pprint(sys.path)

from sit.models import *
from django.contrib.auth import get_user_model
from django.db import transaction

import uuid

from unidecode import unidecode

@transaction.commit_on_success
def parse_csv():
    with open(sys.argv[1], 'r') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            seat_id = row[0]
            if not seat_id:
                # real data ends when there rows like ",,,,,"
                break

            owner = row[1]

            seat = Seat(number=seat_id)
            if owner.decode('utf-8') == u"0":
                seat.status = Seat.BLANK
                owner = None
                print u"seat %s is empty" % seat_id
            elif re.match("^\s*[rR]:", owner):
                # seat is reserved
                seat.status = Seat.RESERVED
                owner = re.sub("^\s*[rR]:\s*", "", owner)
                print u'Seat reserved for "%s"' % owner.decode('utf-8')
            elif re.search(r"\(.+\)\s*$", owner):
                # cutting users name only
                owner = re.sub(r"\s*\(.+\)\s*$", "", owner)
                print u'extracted name "%s"' % owner.decode('utf-8')
            if owner:
                owner = owner.decode('utf-8')
                owner_translit = unidecode(owner)
                user = get_user_model()(name=owner, name_tl=owner_translit,
                                        email=str(uuid.uuid4()) + "@email.com")
                user.save()
                seat.user = user
            else:
                seat.user = None
            seat.save()


if __name__ == '__main__':
    parse_csv()