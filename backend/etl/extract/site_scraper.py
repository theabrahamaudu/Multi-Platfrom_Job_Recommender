"""
This module contains the job website scrapers.

Each scraper inherits from the `SiteScraper` and `CassandraIO` class.

To add a new scraper, create a new class that inherits from SiteScraper and
CassandraIO. But to make it easier, simply inherit from the IndeedScraper class
which already has the implementations of the helper methods and database
interface.

"""

import os
import glob
from abc import ABC, abstractmethod
import hashlib
import random
import string
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import yaml
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import time
import random as rand
from uuid import UUID
from etl.load.load_cassandra import CassandraIO, Job
from src.utils.pipeline_log_config import pipeline as logger


def generate_profile() -> str:
    """
    Generates a new Firefox browser profile using Selenium.

    Returns:
    str: The name of the newly created browser profile.

    This function generates a random string and appends it to 'Selenium'
    to create a new browser profile using the Firefox
    command line ('firefox -CreateProfile'). It then executes the command,
    waits for 2 seconds, and returns the name of the created profile.
    """
    # generate random string to append to profile name
    random_string = ''.join(
        random.choice(
            string.ascii_letters + string.digits
        ) for _ in range(10)
    )

    # prepare the command to create new browser profile
    profile = f'firefox -CreateProfile Selenium{random_string}'

    # execute the command
    os.system(
        profile
    )
    time.sleep(2)

    # return the profile name
    return profile[23:]


def scrape_with_retry(SiteScraper):
    """
    Attempts to scrape a website using the provided `SiteScraper` class,
    handling exceptions with retries.

    Args:
    SiteScraper: A class that implements scraping functionality.

    This function initializes a scraper with the default profile, attempts to
    scrape data, creates a dataframe from the scraped data, and updates the
    database. If an exception occurs (e.g., encountering an AuthWall),
    it logs the error, generates a new browser profile, waits for 10 seconds,
    and retries the scraping process with the new profile.

    If the jobs dataframe is empty, indicating an AuthWall,
    it raises an exception.

    Note: 'SiteScraper' should implement necessary methods like 'scrape()',
    'create_dataframe()', 'update_database()', and accept 'profile_name'
    as an optional argument for profile usage.
    """
    try:
        # Initialize scraper with default profile
        scraper = SiteScraper()
        _ = scraper.scrape()
        jobs_df = scraper.create_dataframe()

        # raise exception if the jobs dataframe is
        # empty, signifying authwall
        if len(jobs_df) == 0:
            raise Exception("Ran into AuthWall")
        scraper.update_database()

    except Exception as e:
        # log the error and create new profile
        logger.error(f"Error scraping {SiteScraper.__class__.__name__}: {e}")
        new_profile = generate_profile()
        logger.info(f"New profile: {new_profile}")
        logger.info("Sleeping for 10 seconds...")
        # sleep for 10 seconds and try again
        time.sleep(10)
        logger.info("Retrying...")
        scraper = SiteScraper(profile_name=new_profile)
        _ = scraper.scrape()
        _ = scraper.create_dataframe()
        scraper.update_database()


class SiteScraper(ABC):
    """
    Abstract base class defining the interface for job website scrapers.
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def get_jobs(self):
        pass

    @abstractmethod
    def get_job_details(self):
        pass

    @abstractmethod
    def create_dataframe(self):
        pass

    @abstractmethod
    def generate_uuid(self):
        pass

    @abstractmethod
    def update_database(self):
        pass


class IndeedScraper(SiteScraper, CassandraIO):
    """
    A class for scraping job listings from Indeed, based on
    the SiteScraper abstract base class and CassandraIO class.

    Args:
    - driver_path (str): The path to the geckodriver executable.
    - profile_name (str): The name of the Selenium profile to use.
    - url (str): The URL of the Indeed job search page with default
      parameters for location and keywords.
    - num_jobs (int): The number of job listings to retrieve.

    This class initializes a scraper for Indeed job listings with default
    parameters for the search URL, driver path, profile name, and the number
    of jobs to retrieve.
    """
    def __init__(self,
                 driver_path: str = "/usr/local/bin/geckodriver",
                 profile_name: str = "Selenium",
                 url: str = "https://ng.indeed.com/jobs?q=&l=Nigeria&from=searchOnHP&vjk=701c24acfea16b1d", # noqa
                 num_jobs: int = 25):
        """
        Initializes an instance of a job website scraper.

        Args:
        - driver_path (str): The path to the geckodriver executable.
        - profile_name (str): The name of the Selenium profile to use.
        - url (str): The URL of the website to scrape job listings from.
        - num_jobs (int): The number of job listings to retrieve.

        This method initializes an instance of the class `SiteScraper`.
        It sets up the Selenium webdriver using provided options and
        configurations. It also loads configuration settings from a YAML file,
        configures the Selenium profile based on deployment settings,
        and sets up attributes for URL, number of jobs to retrieve,
        and various lists for job details to construct the final dataframe.
        """
        logger.info(f"Initializing {self.__class__.__name__}")
        CassandraIO.__init__(self)

        # load config yaml file
        with open("./config/config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # set selenium profile path
        self.deployment = self.config["deployment"]

        if self.deployment is True:
            self.profile_path =\
                self.config["selenium"]["profile_path"]["docker"]
        else:
            self.profile_path =\
                self.config["selenium"]["profile_path"]["local"]

        logger.info("Setting up webdriver")
        try:
            # Configure Selenium
            options = Options()
            # set headless mode
            options.add_argument("--headless")
            # set profile
            options.add_argument("-profile")
            options.add_argument(glob.glob(os.path.expanduser(
                f"{self.profile_path}*.{profile_name}"
                ))[0])
            self.driver_path = driver_path
            # set driver
            self.driver = webdriver.Firefox(options=options)
            logger.info("webdriver setup successful")
        except Exception as e:
            logger.error(f"webdriver setup failed: {e}")
            raise e

        # Set url and number of jobs
        self.url = url
        self.num_jobs = num_jobs

        # Set up dataframe lists
        self.uuid = []
        self.job_id = []
        self.job_title = []
        self.company_name = []
        self.location = []
        self.date = []
        self.job_link = []
        self.job_desc = []
        self.seniority = []
        self.emp_type = []
        self.job_func = []
        self.ind = []

    def scrape(self):
        """
        Scrapes job listings from Indeed based on the initialized parameters.

        This method initiates the scraping process for job listings
        from Indeed. It calculates the number of pages required to retrieve
        the desired number of jobs based on the assumption of 15 jobs per page.
        Then, it iterates through each page, fetching job cards, closing the
        email pop-up if present, and retrieving job details.
        Finally, it closes the webdriver after scraping all necessary data.

        Note: The `get_jobs` and `get_job_details` methods should be
        implemented to process job cards and extract detailed information.
        """
        logger.info(f"Scraping {self.num_jobs} jobs from Indeed")
        # set number of pages based on the number
        # of jobs per page on the website
        num_of_pages = ceil(self.num_jobs / 15)

        if num_of_pages == 0:
            num_of_pages = 1
        else:
            pass

        # scrape pages in a loop
        wd = self.driver
        for i in range(0, num_of_pages):
            # dynamically construct the page url
            extension = ""
            if i != 0:
                extension = "&start=" + str(i * 10)

            url = self.url + extension
            # fetch the page and get the job cards
            wd.get(url)
            jobs_lists = wd.find_element(
                By.CSS_SELECTOR,
                "#mosaic-provider-jobcards"
            )
            jobs = jobs_lists.find_elements(By.TAG_NAME, "li")  # return a list

            # close email pop-up
            try:
                close_popup = wd.find_element(By.CSS_SELECTOR, ".css-yi9ndv")
                close_popup.click()
                logger.info("Email pop-up closed")
            except Exception as e:
                logger.error(f"Email pop-up not found: {e}")

            # fetch the details from each job card
            self.get_jobs(jobs)

        # get the rest of the details by loading each job page
        self.get_job_details(self.job_link)
        wd.close()
        logger.info(f"Scraped {len(self.job_link)} jobs")

    def get_jobs(self, jobs: list):
        """
        Extracts job details from the provided list of job cards.

        Args:
        - jobs (list): A list of job card elements containing job details.

        This method processes each job card element passed as an argument.
        It extracts various job details such as job link, job ID, job title,
        company name, location, and creation date.
        It generates UUIDs for the jobs based on their links, checks if the
        job already exists in the database, and appends the details to
        respective lists for further processing.

        Note: This method assumes a specific structure of HTML elements
        representing job details within each job card. Thus, it may need
        to be updated if the structure changes.
        """
        # get existing job UUIDs from cassandra database
        self.get_uuids()

        # loop through each job card and store details
        # in growing lists for each property
        logger.info(f"Parsing {len(jobs)} job cards")
        n = 0
        for job in jobs:
            n += 1
            try:
                # get the job link
                job_link0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[' # noqa
                    f'1]/h2/a').get_attribute('href')

                # check if job already exists by comparing its hashed link
                # with those on the database and skip its scraping if
                # there's a match by raising an assertion error
                temp_uuid = self.generate_uuid(job_link0)
                assert str(temp_uuid) not in self.uuids, f"Job {temp_uuid} already exists" # noqa
                # continue if no assertion error
                self.job_link.append(job_link0)
                self.uuid.append(temp_uuid)

                # get job ID
                job_id0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[' # noqa
                    f'1]/h2/a/span').get_attribute('id')
                self.job_id.append(job_id0)

                # get job title
                job_title0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[' # noqa
                    f'1]/h2').get_attribute('innerText')
                self.job_title.append(job_title0)

                # get company name
                company_name0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[' # noqa
                    f'2]/div/span').get_attribute('innerText')
                self.company_name.append(company_name0)

                # get location
                location0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[' # noqa
                    f'2]/div').get_attribute('innerText')
                self.location.append(location0)

                # get job creation date
                date0 = job.find_element(
                    By.XPATH,
                    f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,' # noqa
                    f'"cardOutline")]/div[1]/div/div[1]/div/table[2]/tbody/tr[2]/td/div[1]/span[' # noqa
                    f'1]').text
                self.date.append(date0)

            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list):
        """
        Retrieves additional job details from the provided
        list of job page links.

        Args:
        - job_link (list): A list containing URLs of job pages.

        This method iterates through each job page URL provided in the list.
        For each URL, it loads the job page, fetches specific details such as
        job description, seniority level, employment type, job function,
        and job industry. It populates respective lists with fetched details
        for further processing.

        Note: This method assumes certain HTML structures for
        job details on the job pages.
        """
        logger.info(f"Getting job page details for {len(job_link)} jobs")

        # loop throught he list of job pages, load each job page
        # and fetch more details

        # initialize page counter
        page = 0

        # set driver as `wd` for easy referencing
        wd = self.driver
        for link in job_link:
            page += 1

            try:
                # Load job page
                wd.get(link)

                try:
                    # Get job description
                    job_description = wd.find_element(
                        By.CLASS_NAME,
                        "jobsearch-jobDescriptionText"
                    ).get_attribute(
                        'innerText'
                    )
                    self.job_desc.append(job_description)
                except Exception as e:
                    logger.error(f"Error getting job description: {e}")
                    self.job_desc.append('NA')

                # Seniority level
                seniority_level = 'Unavailable on Indeed'
                self.seniority.append(seniority_level)

                # Employment type
                selectors = [
                    ".css-1p3gyjy > div:nth-child(1) > div:nth-child(1)",
                    "div.css-1p3gyjy:nth-child(1) > div:nth-child(1) > div:nth-child(1)", # noqa
                    ".css-tvvxwd"
                ]
                employment_type = 'NA'
                # Loop through the selectors and
                # try to find the employment type
                for selector in selectors:
                    try:
                        employment_type = wd.find_element(
                            By.CSS_SELECTOR,
                            selector
                        ).get_attribute('innerText')
                        break  # If found, exit the loop
                    except NoSuchElementException:
                        continue  # If not found, try the next selector

                # Append the employment type to list
                self.emp_type.append(employment_type)

                # Job function
                job_function = 'Unavailable on Indeed'
                self.job_func.append(job_function)

                # Job industry
                industries = 'Unavailable on Indeed'
                self.ind.append(industries)

            except Exception as e:
                # in case of error, log the error and append
                # `NA` to all missing fields to ensure consistency
                # of list indices
                logger.error(f'Error scraping Page {page}: {e}')
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")

    @staticmethod
    def generate_uuid(job_link: str) -> UUID:
        """
        Generates a UUID based on the provided job link string
        using MD5 hashing.

        Args:
        - job_link (str): The job link string used to generate the UUID.

        Returns:
        UUID: The generated UUID based on the hashed job link string.
        """
        # hash the job link using MD5
        hex_string = hashlib.md5(job_link.encode("UTF-8")).hexdigest()
        # convert hex string to UUID and return
        return UUID(hex=hex_string)

    def create_dataframe(self):
        """
        Creates a pandas DataFrame from the scraped job details.

        Returns:
        pandas.DataFrame: A DataFrame containing job details
        extracted during scraping.

        This method constructs a pandas DataFrame using the job details stored
        in various lists such as UUIDs, job IDs, job titles, company names,
        locations, dates, job links, descriptions, seniority, employment types,
        job functions, and industries.
        The DataFrame includes additional metadata like the scraping
        timestamp and source class name.
        """
        logger.info("Creating jobs dataframe")

        # create jobs dataframe using the populated lists
        # as well as the scraped_at timestamp and source of
        # the job as the class name from which it was generated
        jobs_dataframe = pd.DataFrame({
            'uuid': self.uuid,
            'skipped': False,
            'scraped_at': pd.to_datetime('today'),
            'source': str(self.__class__.__name__)[:-7],
            'job_id': self.job_id,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'location': self.location,
            'date': self.date,
            'job_link': self.job_link,
            'job_desc': self.job_desc,
            'seniority': self.seniority,
            'emp_type': self.emp_type,
            'job_func': self.job_func,
            'ind': self.ind
        })
        return jobs_dataframe

    def update_database(self):
        """
        Updates the database with new job listings.

        This method creates a DataFrame from the scraped data and
        checks if it contains new job listings.
        If new listings are found, it formats each job as a `Job` object and
        adds them to the database's `job_listings` table using the `write_jobs`
        method from the `CassandraIO` class. If the DataFrame is
        empty, it skips the update.

        Note: This method assumes the existence of a `Job` class and a
        `write_jobs` method in the `CassandraIO` class.
        """
        logger.info("Updating database")
        # create the dataframe from the scraped data
        new_jobs_df = self.create_dataframe()

        if new_jobs_df.empty:
            # skip the update if the dataframe is empty
            logger.info("No new jobs found")
        else:
            logger.info(f"Found {len(new_jobs_df)} new jobs")
            # initialize list to hold formatted jobs
            jobs = []
            # iterate though each row of the jobs dataframe
            # and format each job as a `Job` object according to
            # the jobs table schema
            for _, row in new_jobs_df.iterrows():
                jobs.append(Job(**row.to_dict()))
            # write the jobs to the database
            logger.info(f"Adding {len(jobs)} new jobs to job_listings table")
            try:
                # use the `write_jobs` method from the `CassandraIO` class
                self.write_jobs(jobs)
                logger.info(f"{len(jobs)} new jobs added successfully")
            except Exception as e:
                logger.error(f"Error writing jobs to database: {e}")


class LinkedinScraper(IndeedScraper):
    """
    A class for scraping job listings from LinkedIn.

    Inherits from IndeedScraper to leverage its functionality and
    customizes parameters specific to LinkedIn job searches.

    Args:
    - driver_path (str): The path to the geckodriver executable.
    - profile_name (str): The name of the Selenium profile to use.
    - url (str): The URL of the LinkedIn job search page with default
      parameters for location and keywords.
    - num_jobs (int): The number of job listings to retrieve.

    This class initializes a scraper for LinkedIn job listings with default
    parameters for the search URL, driver path, profile name, and the number
    of jobs to retrieve. It inherits functionality from the IndeedScraper
    class and customizes LinkedIn-specific parameters.
    """
    def __init__(self, driver_path: str = "/usr/local/bin/geckodriver",
                 profile_name: str = "Selenium",
                 url: str = str("https://www.linkedin.com/jobs/search?" + # noqa
                                "keywords=&location=Nigeria&geoId=" +
                                "105365761&trk=public_jobs_jobs-search-bar_search-submit" + # noqa
                                "&position=1&pageNum=0"),
                 num_jobs: int = 25):
        super().__init__(driver_path, profile_name, url, num_jobs)

    def scrape(self):
        """
        Scrapes job listings from LinkedIn.

        This method performs the scraping process for job listings on LinkedIn.
        It loads the LinkedIn job search page, sets the number of pages to be
        scrolled based on the desired number of jobs, iterates through the
        pages, retrieves job cards, and extracts job details.
        It closes the webdriver after scraping.
        """
        # set driver as `wd` to make code more readable
        wd = self.driver
        try:
            # Load page
            wd.get(self.url)

            # Set number of pages based on number of jobs per page
            num_pages = ceil(self.num_jobs / 25)
            if num_pages == 0:
                num_pages = 1

            # Loop to retrieve jobs on pages
            i = 0
            while i < num_pages:
                wd.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                i += 1
                try:
                    # click button to load more jobs and wait
                    # for page to load
                    wd.find_element(
                        "xpath",
                        '/html/body/main/div/section/button'
                    ).click()
                    time.sleep(5)
                except NoSuchElementException:
                    pass
                    time.sleep(5)

            # Extract job cards list
            jobs_lists = wd.find_element(
                By.CLASS_NAME,
                "jobs-search__results-list"
            )
            jobs = jobs_lists.find_elements(By.TAG_NAME, "li")  # return a list

            # get job card details
            self.get_jobs(jobs)
            # get more job details from full job page
            self.get_job_details(self.job_link)
            wd.close()
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            wd.close()

    def get_jobs(self, jobs: list):
        """
        Retrieves job details from LinkedIn job cards.

        Args:
        - jobs (list): A list of job card elements containing job details.

        This method iterates through each job card element passed
        as an argument. It extracts various job details such as
        job link, job ID, job title, company name, location, and posting date.
        It checks for existing jobs by comparing hashed links to
        the list of hashed links from the database to avoid duplicate entries.

        Note: This method assumes certain HTML structures for job cards.
        As such, it may need to be updated if the structure changes.
        """
        # get existing job UUIDs from cassandra database
        self.get_uuids()

        logger.info(f"Scraping {self.num_jobs} jobs from LinkedIn")
        # loop through job cards and collect details
        n = 0
        for job in jobs:
            n += 1
            try:
                # get job link
                job_link0 = job.find_element(
                    By.CSS_SELECTOR,
                    'a'
                ).get_attribute('href').split(sep="?refId=")[0]

                # check if job already exists by comparing hashed link
                # to list of hashed links from the database and raise
                # an assertion error if it already exists
                temp_uuid = self.generate_uuid(job_link0)
                assert str(temp_uuid) not in self.uuids, f"Job {temp_uuid} already exists" # noqa
                # continue if no assertion error
                self.job_link.append(job_link0)
                self.uuid.append(temp_uuid)

                # get job id
                job_id0 = str(job.get_attribute('data-id'))
                self.job_id.append(job_id0)

                # get job title
                job_title0 = job.find_element(
                    By.CSS_SELECTOR,
                    'h3'
                ).get_attribute('innerText')
                self.job_title.append(job_title0)

                # get company name
                company_name0 = job.find_element(
                    By.CSS_SELECTOR,
                    'h4'
                ).get_attribute('innerText')
                self.company_name.append(company_name0)

                # get location
                location0 = job.find_element(
                    By.CSS_SELECTOR,
                    '[class="job-search-card__location"]'
                ).get_attribute('innerText')
                self.location.append(location0)

                # get job posting date
                date0 = job.find_element(
                    By.CSS_SELECTOR,
                    "div>div>time"
                ).get_attribute('datetime')
                self.date.append(date0)
            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list):
        """
        Retrieves additional job details from individual LinkedIn job pages.

        Args:
        - job_link (list): A list of job page URLs containing job details
          to be scraped.

        This method iterates through each job page URL passed as an argument.
        It extracts job details such as job description, seniority level,
        employment type, job function, and job industry from the HTML content
        of the job pages. It handles errors during scraping and appends 'NA'
        to maintain consistency in scraped data list indices.

        Note: This method assumes certain HTML structures for job details.
        As such, it may need to be updated if the structure changes.
        """
        # loop through each job link to get additional details
        page = 0
        for link in job_link:
            page += 1
            try:
                # Parse job page
                response = uReq(link)
                job_page = response.read()
                job_page_html = bs(job_page, "html.parser")

                # Get job description
                job_description = job_page_html.findAll(
                    "div",
                    {"class": "show-more-less-html__markup"}
                )
                job_description = bs(job_description[0].text).text
                self.job_desc.append(job_description)

                # Get job details
                job_details = job_page_html.findAll(
                    "span",
                    {"class": "description__job-criteria-text description__job-criteria-text--criteria"} # noqa
                )

                # Seniority level
                seniority_level = bs(job_details[0].text).text
                self.seniority.append(seniority_level)

                # Employment type
                employment_type = bs(job_details[1].text).text
                self.emp_type.append(employment_type)

                # Job function
                job_function = bs(job_details[2].text).text
                self.job_func.append(job_function)

                # Job industry
                industries = bs(job_details[3].text).text
                self.ind.append(industries)

                # Sleep for random duration to bypass bot detection
                time.sleep(rand.uniform(0.5, 1))
                logger.info(f"Job {page} page scraped successfully")

            except Exception as e:
                # log error and append `NA` for job details to ensure
                # consistency of scraped data list indices
                print('There was an error scraping Page ', page, ': ', e)
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")


class JobbermanScraper(IndeedScraper):
    """
    A class for scraping job listings from Jobberman.

    Inherits from IndeedScraper to leverage its functionality and customizes
    parameters specific to Jobberman job searches.

    Args:
    - driver_path (str): The path to the geckodriver executable.
    - profile_name (str): The name of the Selenium profile to use.
    - url (str): The URL of the Jobberman job search page.
    - num_jobs (int): The number of job listings to retrieve.

    This class initializes a scraper for Jobberman job listings with default
    parameters for the search URL, driver path, profile name, and the number
    of jobs to retrieve. It inherits functionality from the IndeedScraper
    class and customizes Jobberman-specific parameters.
    """
    def __init__(self,
                 driver_path: str = "/usr/local/bin/geckodriver",
                 profile_name: str = "Selenium",
                 url: str = "https://www.jobberman.com/jobs",
                 num_jobs: int = 25):
        super().__init__(driver_path, profile_name, url, num_jobs)

    def scrape(self):
        """
        Scrapes job listings from Jobberman.

        This method initiates the scraping process by retrieving job listings
        from multiple pages on the Jobberman website.
        It calculates the number of pages based on the number of jobs per page
        and then iterates through each page to collect job cards.
        After gathering job cards from multiple pages, it proceeds to retrieve
        additional job details from the full job page for each job listing.
        Finally, it closes the webdriver after the scraping process.
        """
        logger.info(f"Scraping {self.num_jobs} jobs from Jobberman")
        # Set number of pages based on number of jobs per page
        num_of_pages = ceil(self.num_jobs / 14)
        if num_of_pages == 0:
            num_of_pages = 1
        # Set driver as `wd` for easy referencing
        wd = self.driver
        # Loop through each page and get job cards
        for i in range(num_of_pages):
            i = i + 1
            page = "?page=" + str(i)
            url = self.url + page

            wd = self.driver
            wd.get(url)
            jobs_lists = wd.find_element(
                By.XPATH,
                "/html/body/main/section/div[2]/div[2]/div[1]"
            )
            jobs = jobs_lists.find_elements(
                By.CLASS_NAME,
                "mx-5"
            )  # return a list

            # get job card details
            self.get_jobs(jobs)
        # get more details from full job page
        self.get_job_details(self.job_link)
        wd.close()

    def get_jobs(self, jobs: list):
        """
        Collects job details from Jobberman job cards.

        This method iterates through the list of job cards retrieved from the
        Jobberman website and extracts various job details such as job link,
        title, company name, location, posting date, and job ID.
        It utilizes two different approaches to handle the alternating
        structure of job cards on the webpage.
        It checks for existing job UUIDs in the Cassandra database and appends
        the collected details to respective lists for further processing.

        Args:
        - jobs (list): A list of job card elements containing job information.

        This method parses through the job cards, extracts job details, and
        handles potential exceptions while collecting data from the Jobberman
        website, ensuring the retrieval of pertinent job information for
        further processing.

        Note: This method assumes a specific structure of HTML elements.
        Thus, it may need to be updated if the structure changes.
        """
        # get existing job UUIDs from cassandra database
        self.get_uuids()

        # Loop through job cards and collect details
        logger.info(f"Parsing {len(jobs)} job cards")
        n = 0
        for job in jobs:
            n += 1

            # try two approaches for each job card due alternating
            # structure of job cards
            try:
                if n < 5:
                    # get job link
                    job_link0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]'
                        f'/div[{n}]/div[1]/div[2]/div/div[1]/a'
                    ).get_attribute(
                        'href'
                    )

                    # check if job already exists by comparing its hashed link
                    # with those on the database and skip its scraping if
                    # there's a match by raising an assertion error
                    temp_uuid = self.generate_uuid(job_link0)
                    assert str(temp_uuid) not in self.uuids, f"Job {temp_uuid} already exists" # noqa
                    # continue if no assertion error
                    self.job_link.append(job_link0)
                    self.uuid.append(temp_uuid)

                    # get job title
                    job_title0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div[2]/div/div[1]/a/p'
                    ).get_attribute(
                        'innerText'
                    )
                    self.job_title.append(job_title0)

                    # get company name
                    company_name0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div[2]/div/p[1]'
                    ).get_attribute(
                        'innerText'
                    )
                    self.company_name.append(company_name0)

                    # get location
                    location0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div[2]/div/div[2]/span[1]'
                    ).get_attribute(
                        'innerText'
                    )
                    self.location.append(location0)

                    # get job posting date
                    date0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[2]/p'
                    ).get_attribute(
                        'innerText'
                    )
                    self.date.append(date0)

                    # get job id
                    job_id0 = "Not available on Jobberman"
                    self.job_id.append(job_id0)

                else:
                    # get job link
                    job_link0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div/div/div[1]/a'
                    ).get_attribute(
                        'href'
                    )

                    # check if job already exists by comparing its hashed link
                    # with those on the database and skip its scraping if
                    # there's a match by raising an assertion error
                    temp_uuid = self.generate_uuid(job_link0)
                    assert str(temp_uuid) not in self.uuids, f"Job {temp_uuid} already exists" # noqa
                    # continue if no assertion error
                    self.job_link.append(job_link0)
                    self.uuid.append(temp_uuid)

                    # get job title
                    job_title0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div/div/div[1]/a/p'
                    ).get_attribute(
                        'innerText'
                    )
                    self.job_title.append(job_title0)

                    # get company name
                    company_name0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div/div/p[1]'
                    ).get_attribute(
                        'innerText'
                    )
                    self.company_name.append(company_name0)

                    # get location
                    location0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div[1]/div/div/div[2]/span[1]'
                    ).get_attribute(
                        'innerText'
                    )
                    self.location.append(location0)

                    # get job posting date
                    date0 = job.find_element(
                        By.XPATH,
                        f'/html/body/main/section/div[2]/div[2]/div[1]/'
                        f'div[{n}]/div/p'
                    ).get_attribute(
                        'innerText'
                    )
                    self.date.append(date0)

                    # get job id
                    job_id0 = "Not available on Jobberman"
                    self.job_id.append(job_id0)
            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list): # noqa
        """
        Collects additional job details from individual job pages on Jobberman.

        This method navigates to each job page using the provided list of job
        links, extracts detailed information for each job, including
        job description, seniority level, employment type, job function, and
        job industry.
        It utilizes CSS selectors to locate specific elements on the job page,
        extracts the necessary information, and appends it to their respective
        lists for further processing.

        Args:
        - job_link (list): A list of URLs leading to job pages on Jobberman.

        This method iterates through each job page, extracts job-specific
        details, handles potential exceptions while collecting data from the
        Jobberman website, and ensures the retrieval of pertinent job
        information for further processing.

        Note: This method assumes a specific structure of HTML elements.
        It may need to be updated if the structure changes.
        """
        # loop through each page to get more details
        page = 0
        wd = self.driver
        for link in job_link:
            page += 1
            try:
                # Load job page
                wd.get(link)

                try:
                    # Get job description
                    job_summary = wd.find_element(
                        By.CSS_SELECTOR,
                        f"#tab1 > div.flex.flex-col.rounded-lg.border-gray-"  # noqa 
                        f"300.md\:border.hover\:border-gray-400.md\:mx-0 > "  # noqa # type: ignore
                        f"article > div:nth-child(4)"
                    ).get_attribute(
                        'innerText'
                    )
                    job_req = wd.find_element(
                        By.CSS_SELECTOR,
                        f"#tab1 > div.flex.flex-col.rounded-lg.border-gray-"  # noqa
                        f"300.md\:border.hover\:border-gray-400.md\:mx-0 > "  # noqa # type: ignore
                        f"article > div:nth-child(5)"
                    ).get_attribute(
                        'innerText'
                    )
                    job_description = str(job_summary) + "\n\n" + str(job_req)
                    self.job_desc.append(job_description)
                except NoSuchElementException:
                    self.job_desc.append('NA')

                try:
                    # Seniority level
                    seniority_level = wd.find_element(
                        By.CSS_SELECTOR,
                        f'#tab1 > div.flex.flex-col.rounded-lg.border-gray-'  # noqa
                        f'300.md\:border.hover\:border-gray-400.md\:mx-0 > '  # noqa # type: ignore
                        f'article > div:nth-child(4) > ul > li:nth-child(2) '
                        f'> span.pb-1.text-gray-500'
                    ).get_attribute(
                        'innerText'
                    )
                    self.seniority.append(seniority_level)
                except NoSuchElementException:
                    self.seniority.append('NA')

                try:
                    # Employment type
                    employment_type = wd.find_element(
                        By.CSS_SELECTOR,
                        f"#tab1 > div.flex.flex-col.rounded-lg.border-gray-"  # noqa
                        f"300.md\:border.hover\:border-gray-400.md\:mx-0 > "  # noqa # type: ignore
                        f"article > div.flex.flex-wrap.justify-start.pt-5."
                        f"pb-2.px-4.w-full.border-b.border-gray-300.md\:flex"  # noqa # type: ignore
                        f"-nowrap.md\:px-5 > div.w-full.text-gray-500 > div."  # noqa # type: ignore
                        f"mt-3 > span > a"
                    ).get_attribute(
                        'innerText'
                    )
                    self.emp_type.append(employment_type)
                except NoSuchElementException:
                    self.emp_type.append('NA')

                try:
                    # Job function
                    job_function = wd.find_element(
                        By.CSS_SELECTOR,
                        f"#tab1 > div.flex.flex-col.rounded-lg.border-gray-"  # noqa
                        f"300.md\:border.hover\:border-gray-400.md\:mx-0 > "  # noqa # type: ignore
                        f"article > div.flex.flex-wrap.justify-start.pt-5."
                        f"pb-2.px-4.w-full.border-b.border-gray-300.md\:flex"  # noqa # type: ignore
                        f"-nowrap.md\:px-5 > div.w-full.text-gray-500 > h2:"  # noqa # type: ignore
                        f"nth-child(3) > a"
                    ).get_attribute(
                        'innerText'
                    )
                    self.job_func.append(job_function)
                except NoSuchElementException:
                    self.job_func.append('NA')

                try:
                    # Job industry
                    industries = wd.find_element(
                        By.CSS_SELECTOR,
                        f"#tab1 > div.flex.flex-col.rounded-lg.border-gray-"  # noqa
                        f"300.md\:border.hover\:border-gray-400.md\:mx-0 > "  # noqa # type: ignore
                        f"article > div.flex.flex-wrap.justify-start.pt-5."
                        f"pb-2.px-4.w-full.border-b.border-gray-300.md\:flex"  # noqa # type: ignore
                        f"-nowrap.md\:px-5 > div.w-full.text-gray-500 > div:"  # noqa # type: ignore
                        f"nth-child(5) > a"
                    ).get_attribute(
                        'innerText'
                    )
                    self.ind.append(industries)
                except NoSuchElementException:
                    self.ind.append('NA')

            except Exception as e:
                # log error and append 'NA' to each list to
                # enusre consistency of list indices
                logger.error(f"There was an error scraping Page {page}: {e}")
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")
