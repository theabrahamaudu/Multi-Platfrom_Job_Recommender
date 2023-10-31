from abc import ABC, abstractmethod
import hashlib
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import pandas as pd
from backend.src.utils.pipeline_log_config import pipeline as logger


class SiteScraper(ABC):
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


class IndeedScraper(SiteScraper):
    def __init__(self,
                 driver_path: str = "/usr/local/bin/geckodriver",
                 url: str = "https://ng.indeed.com/jobs?q=&l=Nigeria&from=searchOnHP&vjk=701c24acfea16b1d",
                 num_jobs: int = 25):
        logger.info("Initializing IndeedScraper")
        logger.info("Setting up webdriver")
        try:
            # Configure Selenium
            options = Options()
            # options.add_argument("--headless")
            options.add_argument("-profile")
            options.add_argument("/home/abraham-pc/snap/firefox/common/.cache/mozilla/firefox/jboe8erx.Selenium")
            self.driver_path = driver_path
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
        logger.info(f"Scraping {self.num_jobs} jobs from Indeed")
        num_of_pages = ceil(self.num_jobs / 15)

        if num_of_pages == 0:
            num_of_pages = 1
        else:
            pass

        for i in range(0, num_of_pages):
            extension = ""
            if i != 0:
                extension = "&start=" + str(i * 10)

            url = self.url + extension
            wd = self.driver
            wd.get(url)
            jobs_lists = wd.find_element(By.CSS_SELECTOR, "#mosaic-provider-jobcards")
            jobs = jobs_lists.find_elements(By.TAG_NAME, "li")  # return a list

            self.get_jobs(jobs)

            if len(self.job_link) == 0:
                start_at = 0
            else:
                start_at = 15 * i

            self.get_job_details(self.job_link, start_at)
            logger.info(f"Scraped {len(self.job_link)} jobs")

    def get_jobs(self, jobs):

        logger.info(f"Parsing {len(jobs)} job cards")
        n = 0
        for job in jobs:
            n += 1
            try:
                job_id0 = job.find_element(By.XPATH,
                                        f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                        f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div['
                                        f'1]/h2/a/span').get_attribute('id')
                self.job_id.append(job_id0)

                job_title0 = job.find_element(By.XPATH,
                                            f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                            f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div['
                                            f'1]/h2').get_attribute('innerText')
                self.job_title.append(job_title0)

                company_name0 = job.find_element(By.XPATH,
                                                f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                                f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div['
                                                f'2]/span').get_attribute('innerText')
                self.company_name.append(company_name0)

                location0 = job.find_element(By.XPATH,
                                            f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                            f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div['
                                            f'2]/div').get_attribute('innerText')
                self.location.append(location0)

                date0 = job.find_element(By.XPATH,
                                        f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                        f'"cardOutline")]/div[1]/div/div[1]/div/table[2]/tbody/tr[2]/td/div[1]/span['
                                        f'1]').text
                self.date.append(date0)

                job_link0 = job.find_element(By.XPATH,
                                            f'//*[@id="mosaic-provider-jobcards"]/ul/li[{n}]/div[contains(@class,'
                                            f'"cardOutline")]/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div['
                                            f'1]/h2/a').get_attribute('href')
                self.job_link.append(job_link0)
                self.uuid.append(self.generate_uuid(job_link0))
            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list, start_at: int):
        logger.info(f"Getting job page details for {len(job_link)} jobs")
        if start_at == 0:
            pass
        else:
            job_link = job_link[start_at:]

        page = 0
        for link in job_link:
            page += 1
            # implement check for job existence on db
            try:
                # Load job page
                wd = self.driver
                wd.get(link)

                try:
                    # Get job description
                    job_description = wd.find_element(By.CLASS_NAME, "jobsearch-jobDescriptionText").get_attribute(
                        'innerText')
                    self.job_desc.append(job_description)
                except:
                    self.job_desc.append('NA')

                # Seniority level
                seniority_level = 'Unavailable on Indeed'
                self.seniority.append(seniority_level)

                try:
                    # Employment type
                    employment_type = wd.find_element(By.CSS_SELECTOR,
                                                    "#jobDetailsSection > div:nth-child(3) > div:nth-child(2)").get_attribute(
                        'innerText')
                    self.emp_type.append(employment_type)
                except:
                    self.emp_type.append('NA')

                # Job function
                job_function = 'Unavailable on Indeed'
                self.job_func.append(job_function)

                # Job industry
                industries = 'Unavailable on Indeed'
                self.ind.append(industries)

            except Exception as e:
                logger.error(f'Error scraping Page {page}: {e}')
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")

    @staticmethod
    def generate_uuid(job_link: str) -> str:
        uuid = hashlib.md5(job_link.encode()).hexdigest()
        return uuid

    def create_dataframe(self):
        logger.info("Creating jobs dataframe")
        jobs_dataframe = pd.DataFrame({
            'uuid': self.uuid,
            'skipped': False,
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
        pass
