from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymongo
import certifi
import re
from traceback import print_exc
from datetime import datetime, timedelta
import psutil
import logging

class Crawler:

    def __init__(self, mongoConfig = None):
        self.results = []

        self.number_items = 0
        self.last_number_items = 0
        if mongoConfig is not None:
            self.mongoConfig = mongoConfig
        else:
            self.mongoConfig = {'username': 'admin', 'password': '4HhGbJ2R0lhimu8m', 'cluster': 'maincluster.bjppfkw.mongodb.net', 'options': {'retryWrites': 'true', 'w': 'majority'}}

    def initDB(self):
        username = self.mongoConfig['username']
        password = self.mongoConfig['password']
        cluster = self.mongoConfig['cluster']
        options = '&'.join([f"{key}={value}" for key, value in self.mongoConfig['options'].items()])

        self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{cluster}/?{options}", tlsCAFile=certifi.where())
        self.db = self.client["movies_data"]

        self.movies_col = self.db['movies']

    def setChromeOptions(self, chromeOptions: webdriver.ChromeOptions = None):
        if chromeOptions is None:
            self.chromeOptions = webdriver.ChromeOptions()
            self.chromeOptions.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            # self.chromeOptions.add_argument('--headless')
            prefs = {"profile.managed_default_content_settings.images": 2}
            self.chromeOptions.add_experimental_option("prefs", prefs)
            # self.chromeOptions.add_argument('--disable-gpu')
            # self.chromeOptions.add_argument('--disable-extensions')
            self.chromeOptions.add_argument('--disable-logging')
            # self.chromeOptions.add_argument('--no-sandbox')
            prefs = {"profile.default_content_setting_values.notifications": 2}
            self.chromeOptions.add_experimental_option("prefs", prefs)
            self.chromeOptions.add_argument('--disable-blink-features=AutomationControlled')
            self.chromeOptions.add_argument("--enable-precise-memory-info")
            self.chromeOptions.add_argument('--ignore-certificate-errors')
            self.chromeOptions.add_argument('--incognito')
            self.chromeOptions.add_argument("--window-size=1920,1080")

    def initChrome(self):
        return webdriver.Chrome(options=self.chromeOptions)

    def saveData(self):
        self.number_items += len(self.results)
        for doc in self.results:
            movie_id = doc['movie_id']
            self.movies_col.update_one({'movie_id': movie_id}, {
                                '$set': doc}, upsert=True)
        self.results = []

    @staticmethod
    def clean(*argv):
        for arg in argv:
            if isinstance(arg, webdriver.Chrome):
                arg.close()
                arg.quit()
                for proc in psutil.process_iter():
                    if 'chrome' in proc.name():
                        proc.terminate()
            else:
                del arg

    def getData(self, crawl_type, start_date: datetime = datetime(), time_step: timedelta = timedelta(days=365)):
        time_step = timedelta(days=365)

        end_date = start_date - time_step
        self.driver = self.initChrome()

        match crawl_type:
            case 0:
                url = f"https://www.imdb.com/search/title/?release_date={end_date.strftime('%Y-%m-%d')},{start_date.strftime('%Y-%m-%d')}&sort=num_votes,desc"
            case 1:
                url = f"https://www.imdb.com/chart/top/?ref_=nv_mv_250"
            case 2:
                url = f"https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250"
            case _:
                url = f"https://www.imdb.com/search/title/?release_date={end_date.strftime('%Y-%m-%d')},{start_date.strftime('%Y-%m-%d')}&sort=num_votes,desc"

        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, "//li[contains(@class, 'ipc-metadata-list-summary-item')]")))

        self.driver1 = None

        try:
            while True:
                self.driver.execute_script(
                    "Element.prototype.scrollIntoView = function() {};")
                try:
                    self.driver.execute_script("""
                        setTimeout(()=>{
                            const more_btn = document.getElementsByClassName("ipc-see-more__text")[0]
                            more_btn.click()
                        }, 0)""")
                    elements = self.driver.find_elements(
                        by=By.XPATH, value="//li[contains(@class, 'ipc-metadata-list-summary-item')]")
                    if len(elements) > 0:

                        for element in elements:
                            result = {}
                            try:
                                result['movie_image'] = element.find_element(
                                    by=By.CLASS_NAME, value="ipc-image").get_attribute("src").strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                result['movie_name'] = element.find_element(
                                    by=By.CLASS_NAME, value="ipc-title__text").text.split(".", 1)[1].strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                movie_link = element.find_element(
                                    by=By.CLASS_NAME, value="ipc-title-link-wrapper").get_attribute("href")
                                result['movie_link'] = movie_link
                                result['movie_id'] = movie_link.split("/")[-2].strip()
                                self.driver1 = self.initChrome()
                                self.driver1.get(result['movie_link'])
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                if crawl_type == 0:
                                    # for all
                                    meta_datas = element.find_elements(
                                        by=By.CLASS_NAME, value="dli-title-metadata-item")
                                else :
                                    # For top 250
                                    meta_datas = element.find_elements( 
                                        by=By.CLASS_NAME, value="cli-title-metadata-item")
                                result['movie_metadata'] = {}
                                try:
                                    result['movie_metadata']['released_date'] = meta_datas[0].text.strip(
                                    )
                                except Exception as e:
                                    # print_exc()
                                    result['movie_metadata']['released_date'] = "Unknow"

                                try:
                                    result['movie_metadata']['length'] = meta_datas[1].text.strip()
                                except Exception as e:
                                    # print_exc()
                                    result['movie_metadata']['length'] = "Unknow"

                                try:
                                    result['movie_metadata']['film_by_age'] = meta_datas[2].text.strip(
                                    )
                                except Exception as e:
                                    # print_exc()
                                    result['movie_metadata']['film_by_age'] = "Unknow"

                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                result['rating_star'] = element.find_element(
                                    by=By.CLASS_NAME, value="ratingGroup--imdb-rating").get_attribute("aria-label").split(":", 2)[1].strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                result['movie_metadata']['vote_count'] = element.find_element(
                                    by=By.CLASS_NAME, value="ipc-rating-star--voteCount").text.strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                if crawl_type == 0:
                                    result['movie_metadata']['mecritic_score'] = element.find_element(
                                        by=By.CLASS_NAME, value="metacritic-score-box").text.strip()
                                else:
                                    if self.driver1 is not None:
                                        result['movie_metadata']['mecritic_score'] = self.driver1.find_element(
                                            by=By.CLASS_NAME, value="metacritic-score-box").text.strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            try:
                                if crawl_type == 0:
                                    result['movie_description'] = element.find_element(
                                    by=By.CLASS_NAME, value="ipc-html-content-inner-div").text.strip()
                                else:
                                    if self.driver1 is not None:
                                        result['movie_description'] = self.driver1.find_element(
                                            by=By.XPATH, value="//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/p/span[3]").text.strip()
                            except Exception as e:
                                # print_exc()
                                pass
                            if self.driver1 is not None:
                                self.clean(self.driver1)
                            # print(result)
                            self.results.append(result)

                            self.driver.execute_script(
                                "var element = arguments[0]; element.remove()", element)

                        # print(results[0])
                        print(self.number_items)

                        if len(self.results) > 100:
                            self.saveData()
                    else:
                        if crawl_type != 0:
                            break

                        end_date = start_date - time_step

                        self.saveData()

                        self.clean(self.driver)

                        self.driver = self.initChrome()
                        self.driver.get(
                            f"https://www.imdb.com/search/title/?release_date={end_date.strftime('%Y-%m-%d')},{start_date.strftime('%Y-%m-%d')}&sort=num_votes,desc")
                        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
                            (By.XPATH, "//li[contains(@class, 'ipc-metadata-list-summary-item')]")))
                        start_date = end_date

                except:
                    if crawl_type != 0:
                        break

                    end_date = start_date - time_step

                    self.saveData()

                    self.last_number_items = self.number_items

                    self.clean(self.driver)
                    
                    self.driver = self.initChrome()
                    self.driver.get(
                        f"https://www.imdb.com/search/title/?release_date={end_date.strftime('%Y-%m-%d')},{start_date.strftime('%Y-%m-%d')}&sort=num_votes,desc")
                    WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
                        (By.XPATH, "//li[contains(@class, 'ipc-metadata-list-summary-item')]")))

                    start_date = end_date
                    print_exc()

                time.sleep(5)

        except KeyboardInterrupt:
            print("\nExiting on Ctrl+C.")
            self.last_number_items = self.number_items
        self.clean(self.driver, self.driver1)