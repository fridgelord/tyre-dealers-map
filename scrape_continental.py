import json
import get_country_data
import classes
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        # TimeoutException,
                                        ElementNotInteractableException,
                                        # WebDriverException,
                                        )
from time import sleep
import re

COUNTRY_LIST_FILE = "country_list_co.json"
SWAPFILE = ".continental.swp"
AREA = 20

class Country_conti(classes.Country):
    data_xpaths = {
        "name": ["//h3[contains(@class, 'dealer-basics_name')]", "text"],
        "address": ["//div[contains(@class, 'dealer-basics_location')]/span", "text"],
        "phone": ["//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'tel')]",
                  "text"],
        "mail": ["//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'mailto')]", 
                 "text"],
        "website": ["", ""],
    }
    cookie_path_1 = "//a[contains(@class, 'js-privacyhint-close')]"
    cookie_path_2 = "//button[contains(@class, 'js-privacyhint-close')]"
    iframe_path = "//iframe[contains(@sandbox, 'allow-scripts')]"
    dealers_path = "//li[contains(@class, 'dealer_dealer__26yMr')]"
    coordinates_path = "//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'maps')]"
    back_path = "//button[contains(@class, 'dealer_back')]"

    def cookie_disable(self):
        try:
            self.driver.find_element_by_xpath(self.cookie_path_1).click()
            sleep(1)
        except (NoSuchElementException, ElementNotInteractableException):
            pass
        try:
            self.driver.find_element_by_xpath(self.cookie_path_2).click()
            sleep(1)
        except (NoSuchElementException, ElementNotInteractableException):
            pass

    def get_dealer_info_manuf(self, lat, lon, datafile, ):
        self.driver.get(self.website + lat + "," + lon)
        sleep(5)
        self.cookie_disable()
        frame = self.driver.find_element_by_xpath(self.iframe_path)
        self.driver.switch_to.frame(frame)
        els = self.driver.find_elements_by_xpath(self.dealers_path)
        for el in els:
            print("getting dealer {el}")
            # self.driver.execute_script("arguments[0].scrollIntoView();", el)
            el.click()
            dealers_data = [self.get_dealer_info(self.driver, xpaths[0], xpaths[1])
                            for x, xpaths
                            in self.data_xpaths.items()
                            ]
            try:
                coordinates = self.driver.find_element_by_xpath(self.coordinates_path)
                coordinates = coordinates.get_attribute("href")
                coordinates = re.search("\\@(.*)\\/", coordinates).group(1)
            except NoSuchElementException:
                coordinates = ""
            dealers_data.append(coordinates)
            dealers_data.insert(0, self.name)
            name_address = " ".join(dealers_data[:3])
            if name_address not in self.dealers_list:
                datafile.append(dealers_data)
                self.dealers_list.append(name_address)
            print("coming back")
            self.driver.find_element_by_xpath(self.back_path).click()
            print("came back")


def main():
    # driver = webdriver.Firefox()
    # driver.maximize_window()
    countries = get_country_data.get_country_data()

    with open(COUNTRY_LIST_FILE) as fp:
        countries_co = json.load(fp)
    # country_list = [Country_conti(country_name, countries, countries_co, 500)
        # for country_name
        # in countries_co
        # # if country_name in countries
        # if country_name == "Poland"
            # ]
    f = classes.Datafile("conti.csv")
    with Country_conti("Poland", countries, countries_co, AREA, SWAPFILE) as Poland:
        if Poland.check_robots():
            Poland.loop_coordinates(f)


if __name__ == "__main__":
    main()
