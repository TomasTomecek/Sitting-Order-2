# -*- coding: utf-8 -*-

import csv

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from sit.models import *
from django.contrib.auth import get_user_model
from django.db import transaction

import uuid

from unidecode import unidecode

@transaction.commit_on_success
def parse_csv():
    with open(sys.args[1], 'r') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            seat_id = row[0]
            if not seat_id:
                break

            owner = row[1].decode('utf-8')
            owner_translit = unidecode(owner)
            print owner_translit

            seat = Seat(number=seat_id)
            user = get_user_model()(name=owner, email=str(uuid.uuid4()) + "@email.com")
            user.save()
            seat.user = user
            seat.save()


if __name__ == '__main__':
    parse_csv()