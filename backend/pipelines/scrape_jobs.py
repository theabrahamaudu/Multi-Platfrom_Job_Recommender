"""
This module contains the main entry point for scraping job listings from
Indeed, LinkedIn, and Jobberman.

It calls the `scrape_with_retry` function in the `etl.extract.site_scraper`
module to retry scraping if an error occurs.

It is primarily to be called in a cron job.
"""

from etl.extract.site_scraper import (
    IndeedScraper, LinkedinScraper, JobbermanScraper, scrape_with_retry
)
from etl.load.load_chroma import ChromaIO
from etl.load.load_cassandra import CassandraIO

if __name__ == "__main__":
    # Scrape Job and save to Cassandra
    scrape_with_retry(IndeedScraper)
    scrape_with_retry(JobbermanScraper)
    scrape_with_retry(LinkedinScraper)

    # Update Job embeddings in Chroma
    chroma_io = ChromaIO()
    chroma_io.load_from_cassandra()

    # Scrub older jobs and embeddings
    cassandra_io = CassandraIO()
    cassandra_io.scrub_jobs()
    chroma_io.scrub_jobs()
