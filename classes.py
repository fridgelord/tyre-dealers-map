import get_country_data
import json
import geopy.distance as geodistance
import re
from selenium import webdriver


countries = get_country_data.get_country_data()
COUNTRY_LIST_FILE = 'country_list_co.json'

with open(COUNTRY_LIST_FILE) as fp:
    countries_co = json.load(fp)

print(countries_co)


class Country:
    def __init__(self, name, geo_dict, manuf_countries_dict, km_step, driver):
        self.name = name
        self.website = manuf_countries_dict.get(self.name)
        try:
            self.min_longitude = geo_dict[self.name]["min_lon"]
            self.min_latitude = geo_dict.get(self.name)["min_lat"]
            self.max_longitude = geo_dict.get(self.name)["max_lon"]
            self.max_latitude = geo_dict.get(self.name)["max_lat"]
            self._left_bottom =  (self.min_latitude, self.min_longitude
            self._right_bottom = (self.min_latitude, self.max_longitude)
            self._left_top =     (self.max_latitude, self.min_longitude)
            lat_span = geodistance.distance(self._left_bottom, self._left_top).km
            lon_span = geodistance.distance(self._left_bottom, self._right_bottom).km
            lon_step = (max_lon - min_lon) * km_step / lon_span
            lat_step = (max_lat - min_lat) * km_step / lat_span
        except KeyError:
            self = None

    def check_robots(self):
        """ Check if website we want to scrape is available 
        for robots
        """
        robots_url = re.findall("https:\/\/.+\/", self.website) + "robots.txt"
        example_url = self.website + sefl.min_longitude + "," + self.min_latitude
        robots = Robots.fetch(robots_url)
        if str(robots) == '{"*": []}':
            print("Provide valid url")
            return False
        if not robots.allowed(example_site, "*"):
            print("Couldn't scrape {0} for {1}: disallowed by robots.txt".format(
                example_url, self.name))

    def loop_coordinates(self):
        self.dealers_data = []
        start = self.min_latitude + self.lat_step / 2 
        stop = self.max_latitude
        step = self.lat_step
        for lat in arange(start, stop, step)
            start = self.min_longitude + self.lat_step / 2 
            stop = self.max_longitude
            step = self.lon_step
            for lon in arange(start, stop, step)
                dealers_data = get_dealer_info_manuf(self.website, lat, lon)

    def get_dealer_info(element, xpath_path, attribute):
        try:
            if attribute == "text":
                data = element.find_element_by_xpath(xpath_path).text
            else:
                data = element.find_element_by_xpath(xpath_path).get_attribute(attribute)
                # if data == None:
                    data = ""
            return data
        except NoSuchElementException:
            return ""





class Country_conti(Country):
    data_xpaths = {
        "link": ["", ""],
        "name": ["//h3[contains(@class, 'dealer-basics_name')]", "text"],
        "address": ["//div[contains(@class, 'dealer-basics_location')]/span", "text"],
        "phone": ["//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'tel')]",
                  "text"],
        "mail": ["//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'mailto')]", 
                 "text"],
        "website": ["" , ""],
        "hours_text": ["", ""],
    }
    cookie_path = "//a[contains(@class, 'ci-privacyhint-accept js-cookie-accept')]"
    iframe_path = "//iframe[contains(@sandbox, 'allow-scripts')]"
    dealers_path = "//li[contains(@class, 'dealer_dealer__26yMr')]"
    coordinates_path = "//div[contains(@class, 'dealer-details_detail')]//a[contains(@href, 'https')]"
    driver = webdriver.Firefox()

    def get_dealer_info_manuf(self, lat, lon):
        driver.get(self.website + lat + "," + lon)
        sleep(1)
        try:
            driver.find_element_by_xpath(self.cookie_path).click()
            sleep(1)
        except (NoSuchElementException, ElementNotInteractableException):
            pass
        frame = driver.find_element_by_xpath(iframe_path)
        driver.switch_to.frame(frame)
        els = driver.find_elements_by_xpath(dealers_path)
        for el in els:
            el.click()
            dealers_data = [self.get_dealer_info(driver, xpaths[0], xpaths[1])
                            for x, xpaths
                            in self.data_xpaths.items()
                           ]
            try:
                coordinates = driver.find_element_by_xpath(coordinates_path)
                coordinates = coordinates.get_attribute("href")
                coordinates = re.search("\@(.*)\/", coordinates).group(1)
            except NoSuchElementException:
                coordinates = ""
            dealers_data += coordinates


        



        
        



country_list = [Country(country_name, countries, countries_co, 500)
                for country_name 
                in countries_co
               ]
        
                            

a = [x for x in country_list if x.min_latitude == None]
for i in a:
    print(i.name)


a = {}
a.get


