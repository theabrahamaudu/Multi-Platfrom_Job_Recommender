from unittest.mock import patch
from etl.utils.utilities import (
    get_previous_jobs, get_user_data, get_user_searches,
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


def test_get_user_searches_empty():
    response = [
    ]
    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_searches('test', 2) == ''


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


def test_get_previous_clicks_empty():
    response = [
    ]
    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_previous_clicks('test', 5) == [
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


def test_get_previous_jobs_truncated():
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
        assert get_previous_jobs(input, 4) ==\
            'long, long, long'


def test_get_user_data():
    input = UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e')

    response = [{
        'skills': ['skill1', 'skill2', 'skill3'],
        'work_history': [
            {'company': 'company1', 'position': 'position1'},
        ],
        'preferences': {
            'key1': 'value1',
            'key2': 'value2',
        }
    }]

    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_data(input) ==\
            "skill1, skill2, skill3, company1, position1, value1, value2"


def test_get_user_data_no_skills():
    input = UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e')

    response = [{
        'skills': None,
        'work_history': [
            {'company': 'company1', 'position': 'position1'},
        ],
        'preferences': {
            'key1': 'value1',
            'key2': 'value2',
        }
    }]

    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_data(input) ==\
            "company1, position1, value1, value2"


def test_get_user_data_no_work_history():
    input = UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e')

    response = [{
        'skills': ['skill1', 'skill2', 'skill3'],
        'work_history': None,
        'preferences': {
            'key1': 'value1',
            'key2': 'value2',
        }
    }]

    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_data(input) ==\
            "skill1, skill2, skill3, value1, value2"


def test_get_user_data_no_preferences():
    input = UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e')

    response = [{
        'skills': ['skill1', 'skill2', 'skill3'],
        'work_history': [
            {'company': 'company1', 'position': 'position1'},
        ],
        'preferences': None
    }]

    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_data(input) ==\
            "skill1, skill2, skill3, company1, position1, "


def test_get_user_data_empty():
    input = UUID('4703b861-4ddc-421c-a0eb-b8204ee6c78e')

    response = [{
        'skills': None,
        'work_history': None,
        'preferences': None
    }]

    # Mocking the Cassandra Cluster and Session objects
    with patch(
        'etl.utils.utilities.session',
        MockSession(response)
       ):
        assert get_user_data(input) == ""
