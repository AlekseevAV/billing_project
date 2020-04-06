from datetime import datetime
from unittest import TestCase

from django.test import override_settings

from ..utils import set_current_timezone


class UtilsTestCase(TestCase):

    @override_settings(TIME_ZONE='Europe/Moscow')
    def test_set_current_timezone(self):
        input_datetime = datetime(2020, 6, 10, 10, 10, 10, 10)
        result = set_current_timezone(input_datetime=input_datetime)
        self.assertEqual(result.isoformat(), '2020-06-10T10:10:10.000010+03:00')
