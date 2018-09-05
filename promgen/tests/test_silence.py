# Copyright (c) 2017 LINE Corporation
# These sources are released under the terms of the MIT license: see LICENSE

import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

from promgen.tests import PromgenTest

TEST_SETTINGS = PromgenTest.data_yaml('examples', 'promgen.yml')
TEST_DURATION = PromgenTest.data_json('examples', 'silence.duration.json')
TEST_RANGE = PromgenTest.data_json('examples', 'silence.range.json')

# Explicitly set a timezone for our test to try to catch conversion errors
TEST_SETTINGS['timezone'] = 'Asia/Tokyo'


class SilenceTest(PromgenTest):
    def setUp(self):
        self.user = User.objects.create_user(id=999, username="Foo")
        self.client.force_login(self.user)

    @override_settings(PROMGEN=TEST_SETTINGS)
    @mock.patch('promgen.util.post')
    def test_duration(self, mock_post):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime.datetime(2017, 12, 14, tzinfo=datetime.timezone.utc)
            # I would prefer to be able to test with multiple labels, but since
            # it's difficult to test a list of dictionaries (the order is non-
            # deterministic) we just test with a single label for now
            self.client.post(reverse('silence'),
                data={
                    'duration': '1m',
                    'label.instance': 'example.com:[0-9]*'
                },
            )
        mock_post.assert_called_with(
            'http://alertmanager:9093/api/v1/silences',
            json=TEST_DURATION
        )

    @override_settings(PROMGEN=TEST_SETTINGS)
    @mock.patch('promgen.util.post')
    def test_range(self, mock_post):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime.datetime(2017, 12, 14, tzinfo=datetime.timezone.utc)
            self.client.post(reverse('silence'),
                data={
                    'start': '2017-12-14 00:01',
                    'stop': '2017-12-14 00:05',
                    'label.instance': 'example.com:[0-9]*'
                },
            )
        mock_post.assert_called_with(
            'http://alertmanager:9093/api/v1/silences',
            json=TEST_RANGE
        )
