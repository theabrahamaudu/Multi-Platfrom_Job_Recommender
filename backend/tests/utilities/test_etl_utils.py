from unittest.mock import patch
from etl.utils.utilities import (
    get_user_metadata, get_previous_jobs, get_user_data, get_user_searches,
    get_previous_clicks
)
from uuid import UUID


class MockSession:
    def __init__(self, output, **kwargs):
        self.output = output

    def execute(self, *args, **kwargs):
        return self.output


def test_get_user_searches():
    response = [
        {'search_query': 'test1'},
        {'search_query': 'test2'},
        {'search_query': 'test3'},
    ]
    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_searches('test', 5) == 'test1, test2, test3'


def test_get_previous_clicks():
    response = [
        {'job_id': '4703b861-4ddc-421c-a0eb-b8204ee6c78e'},
        {'job_id': '4703b861-4ddc-421c-a0eb-b8204ee6c78e'},
        {'job_id': '4703b861-4ddc-421c-a0eb-b8204ee6c78e'},
    ]
    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_previous_clicks('test', 5) == [
            UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
            UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
            UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
        ]


def test_get_previous_jobs():
    input = [
        UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
        UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
        UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e'),
    ]

    response = [
        {'job_desc': 'long text1'},
        {'job_desc': 'long text2'},
        {'job_desc': 'long text3'},
    ]
    
    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
    ):
        assert get_previous_jobs(input, -1) ==\
            'long text1, long text2, long text3'
