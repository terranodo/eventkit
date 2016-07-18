from __future__ import absolute_import

from django.test import TestCase, TransactionTestCase
from ..voyagersearch import *
import copy
from django.db import IntegrityError, transaction, connections

class EventkitVoyagerTests(TestCase):
    pass