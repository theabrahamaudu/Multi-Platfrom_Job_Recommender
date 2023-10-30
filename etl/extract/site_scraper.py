from abc import ABC, abstractmethod


class SiteScraper(ABC):
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
    def update_database(self):
        pass


