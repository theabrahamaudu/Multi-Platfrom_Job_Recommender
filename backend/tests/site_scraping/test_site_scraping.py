from unittest.mock import patch
from etl.extract.site_scraper import (
    generate_profile
)


def test_generate_profile():
    with patch(
        'etl.extract.site_scraper.os.system',
        return_value=0
    ):
        assert len(generate_profile()) == 18
        assert "Selenium" in generate_profile()

        with patch(
            'etl.extract.site_scraper.random.choice',
            return_value="x"
        ):
            assert len(generate_profile()) == 18
            assert generate_profile() == "Seleniumxxxxxxxxxx"
