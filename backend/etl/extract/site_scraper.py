from abc import ABC, abstractmethod
import hashlib
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import time 
import random as rand
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
        logger.info(f"Initializing {self.__class__.__name__}")
        logger.info("Setting up webdriver")
        try:
            # Configure Selenium
            options = Options()
            # options.add_argument("--headless")
            options.add_argument("-profile")
            options.add_argument("/home/abraham-pc/snap/firefox/common/.cache/mozilla/firefox/i4zb3sr8.Selenium")
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

            # close email pop-up
            try:
                close_popup = wd.find_element(By.CSS_SELECTOR, ".css-yi9ndv")
                close_popup.click()
                logger.info("Email pop-up closed")
            except Exception as e:
                logger.error(f"Email pop-up not found: {e}")

            self.get_jobs(jobs)

            if len(self.job_link) == 0:
                start_at = 0
            else:
                start_at = 15 * i

            self.get_job_details(self.job_link, start_at)
            logger.info(f"Scraped {len(self.job_link)} jobs")

    def get_jobs(self, jobs: list):

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
                                                f'2]/div/span').get_attribute('innerText')
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

                # Employment type
                selectors = [
                    ".css-1p3gyjy > div:nth-child(1) > div:nth-child(1)",
                    "div.css-1p3gyjy:nth-child(1) > div:nth-child(1) > div:nth-child(1)",
                    ".css-tvvxwd"
                ]
                employment_type = 'NA'
                # Loop through the selectors and try to find the employment type
                for selector in selectors:
                    try:
                        employment_type = wd.find_element(By.CSS_SELECTOR, selector).get_attribute('innerText')
                        break  # If found, exit the loop
                    except NoSuchElementException:
                        continue  # If not found, try the next selector

                # Append the employment type to your list
                self.emp_type.append(employment_type)

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
            'scraped_at': pd.to_datetime('today').strftime('%Y-%m-%d'),
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


class LinkedinScraper(IndeedScraper):
    def __init__(self, driver_path: str = "/usr/local/bin/geckodriver",
                 url: str = "https://www.linkedin.com/jobs/search?"\
                            "keywords=&location=Nigeria&geoId="\
                            "105365761&trk=public_jobs_jobs-search-bar_search-submit"\
                            "&position=1&pageNum=0",
                 num_jobs: int = 25):
        super().__init__(driver_path, url, num_jobs)

    def scrape(self):
        # Load page
        wd = self.driver
        wd.get(self.url)

        # Retrieve jobs on page
        i = 2
        while i <= int(self.num_jobs / 25) + 1:
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i = i + 1
            try:
                wd.find_element("xpath", '/html/body/main/div/section/button').click()
                time.sleep(5)
            except NoSuchElementException:
                pass
                time.sleep(5)

        # Extract job details with Selenium
        jobs_lists = wd.find_element(By.CLASS_NAME, "jobs-search__results-list")
        jobs = jobs_lists.find_elements(By.TAG_NAME, "li")  # return a list

        # get jobs
        self.get_jobs(jobs)
        # get job details
        self.get_job_details(self.job_link)

    def get_jobs(self, jobs: list):
        logger.info(f"Scraping {self.num_jobs} jobs from LinkedIn")
        n = 0
        for job in jobs:
            n += 1
            try:
                job_id0 = job.get_attribute('data-id')
                self.job_id.append(job_id0)

                job_title0 = job.find_element(By.CSS_SELECTOR, 'h3').get_attribute('innerText')
                self.job_title.append(job_title0)

                company_name0 = job.find_element(By.CSS_SELECTOR, 'h4').get_attribute('innerText')
                self.company_name.append(company_name0)

                location0 = job.find_element(By.CSS_SELECTOR, '[class="job-search-card__location"]').get_attribute('innerText')
                self.location.append(location0)

                date0 = job.find_element(By.CSS_SELECTOR, "div>div>time").get_attribute('datetime')
                self.date.append(date0)

                job_link0 = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                self.job_link.append(job_link0)
                self.uuid.append(self.generate_uuid(job_link0))
            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list):
        page = 0
        for link in job_link:
            page += 1
            try:
                # Parse job page
                response = uReq(link)
                job_page = response.read()
                job_page_html = bs(job_page, "html.parser")

                # Get job description
                job_description = job_page_html.findAll("div", {"class": "show-more-less-html__markup"})
                job_description = bs(job_description[0].text).text
                self.job_desc.append(job_description)

                # Get job details
                job_details = job_page_html.findAll("span", {
                    "class": "description__job-criteria-text description__job-criteria-text--criteria"})

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

                # Wait a bit...
                time.sleep(rand.uniform(0.5, 1))
                logger.info(f"Job {page} page scraped successfully")

            except Exception as e:
                print('There was an error scraping Page ', page, ': ', e)
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")


class JobbermanScraper(IndeedScraper):
    def __init__(self,
                 driver_path: str = "/usr/local/bin/geckodriver",
                 url: str = "https://www.jobberman.com/jobs",
                 num_jobs: int = 25):
        super().__init__(driver_path, url, num_jobs)

    def scrape(self):
        logger.info(f"Scraping {self.num_jobs} jobs from Jobberman")
        num_of_pages = ceil(self.num_jobs / 14)

        for i in range(num_of_pages):
            i = i + 1
            page = "?page=" + str(i)
            url = self.url + page
            
            wd = self.driver
            wd.get(url)
            jobs_lists = wd.find_element(By.XPATH, "/html/body/main/section/div[2]/div[2]/div[1]")
            jobs = jobs_lists.find_elements(By.CLASS_NAME, "mx-5")  # return a list

            # get job cards
            self.get_jobs(jobs)

            if i == 1:
                start_at = 0
            else:
                start_at = 14 * (i - 1)

            self.get_job_details(self.job_link, start_at)

    def get_jobs(self, jobs: list):
        n = 0
        for job in jobs:
            n += 1
            try:
                if n < 5:
                    job_title0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div[2]/div/div[1]/a/p').get_attribute(
                        'innerText')
                    self.job_title.append(job_title0)

                    company_name0 = job.find_element(By.XPATH,
                                                    f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div[2]/div/p[1]').get_attribute(
                        'innerText')
                    self.company_name.append(company_name0)

                    location0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div[2]/div/div[2]/span[1]').get_attribute(
                        'innerText')
                    self.location.append(location0)

                    date0 = job.find_element(By.XPATH,
                                            f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[2]/p').get_attribute(
                        'innerText')
                    self.date.append(date0)

                    job_link0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div[2]/div/div[1]/a').get_attribute(
                        'href')
                    self.job_link.append(job_link0)
                    self.uuid.append(self.generate_uuid(job_link0))

                    job_id0 = "Not available on Jobberman"
                    self.job_id.append(job_id0)

                else:
                    job_title0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div/div/div[1]/a/p').get_attribute(
                        'innerText')
                    self.job_title.append(job_title0)

                    company_name0 = job.find_element(By.XPATH,
                                                    f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div/div/p[1]').get_attribute(
                        'innerText')
                    self.company_name.append(company_name0)

                    location0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div/div/div[2]/span[1]').get_attribute(
                        'innerText')
                    self.location.append(location0)

                    date0 = job.find_element(By.XPATH,
                                            f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div/p').get_attribute(
                        'innerText')
                    self.date.append(date0)

                    job_link0 = job.find_element(By.XPATH,
                                                f'/html/body/main/section/div[2]/div[2]/div[1]/div[{n}]/div[1]/div/div/div[1]/a').get_attribute(
                        'href')
                    self.job_link.append(job_link0)
                    self.uuid.append(self.generate_uuid(job_link0))

                    job_id0 = "Not available on Jobberman"
                    self.job_id.append(job_id0)
            except Exception as e:
                logger.error(f"Error getting job {n} details: {e}")

    def get_job_details(self, job_link: list, start_at: int):
        if start_at == 0:
            pass
        else:
            job_link = job_link[start_at:]

        page = 0
        for link in job_link:
            page += 1
            try:
                # Load job page
                wd = self.driver
                wd.get(link)

                try:
                    # Get job description
                    job_summary = wd.find_element(By.CSS_SELECTOR,
                                                "#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div:nth-child(4)").get_attribute(
                        'innerText')
                    job_req = wd.find_element(By.CSS_SELECTOR,
                                            "#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div:nth-child(5)").get_attribute(
                        'innerText')
                    job_description = str(job_summary) + "\n\n" + str(job_req)
                    self.job_desc.append(job_description)
                except:
                    self.job_desc.append('NA')

                try:
                    # Seniority level
                    seniority_level = wd.find_element(By.CSS_SELECTOR,
                                                    '#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div:nth-child(4) > ul > li:nth-child(2) > span.pb-1.text-gray-500').get_attribute(
                        'innerText')
                    self.seniority.append(seniority_level)
                except:
                    self.seniority.append('NA')

                try:
                    # Employment type
                    employment_type = wd.find_element(By.CSS_SELECTOR,
                                                    "#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div.flex.flex-wrap.justify-start.pt-5.pb-2.px-4.w-full.border-b.border-gray-300.md\:flex-nowrap.md\:px-5 > div.w-full.text-gray-500 > div.mt-3 > span > a").get_attribute(
                        'innerText')
                    self.emp_type.append(employment_type)
                except:
                    self.emp_type.append('NA')

                try:
                    # Job function
                    job_function = wd.find_element(By.CSS_SELECTOR,
                                                "#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div.flex.flex-wrap.justify-start.pt-5.pb-2.px-4.w-full.border-b.border-gray-300.md\:flex-nowrap.md\:px-5 > div.w-full.text-gray-500 > h2:nth-child(3) > a").get_attribute(
                        'innerText')
                    self.job_func.append(job_function)
                except:
                    self.job_func.append('NA')

                try:
                    # Job industry
                    industries = wd.find_element(By.CSS_SELECTOR,
                                                "#tab1 > div.flex.flex-col.rounded-lg.border-gray-300.md\:border.hover\:border-gray-400.md\:mx-0 > article > div.flex.flex-wrap.justify-start.pt-5.pb-2.px-4.w-full.border-b.border-gray-300.md\:flex-nowrap.md\:px-5 > div.w-full.text-gray-500 > div:nth-child(5) > a").get_attribute(
                        'innerText')
                    self.ind.append(industries)
                except:
                    self.ind.append('NA')

            except Exception as e:
                logger.error(f"There was an error scraping Page {page}: {e}")
                self.job_desc.append("NA")
                self.seniority.append("NA")
                self.emp_type.append("NA")
                self.job_func.append("NA")
                self.ind.append("NA")