import geopy.distance as geodistance
import re
from selenium.common.exceptions import (NoSuchElementException,
                                        # TimeoutException,
                                        ElementNotInteractableException,
                                        # WebDriverException,
                                        )
from numpy import arange
from reppy import Robots


class Country:
    def __init__(self, name, geo_dict, manuf_countries_dict, km_step, driver):
        self.name = name
        self.website = manuf_countries_dict.get(self.name)
        self.driver = driver
        self.dealers_list = []
        try:
            self.min_longitude = geo_dict[self.name]["min_lon"]
            self.min_latitude = geo_dict.get(self.name)["min_lat"]
            self.max_longitude = geo_dict.get(self.name)["max_lon"]
            self.max_latitude = geo_dict.get(self.name)["max_lat"]
            self._left_bottom = (self.min_latitude, self.min_longitude)
            self._right_bottom = (self.min_latitude, self.max_longitude)
            self._left_top = (self.max_latitude, self.min_longitude)
            self.lat_span = geodistance.distance(self._left_bottom, self._left_top).km
            self.lon_span = geodistance.distance(self._left_bottom, self._right_bottom).km
            self.lon_step = (self.max_longitude - self.min_longitude) * km_step / self.lon_span
            self.lat_step = (self.max_latitude - self.min_latitude) * km_step / self.lat_span
        except KeyError:
            self = None

    def check_robots(self):
        """ Check if website we want to scrape is available
        for robots
        """
        robots_url = re.search("https:\/\/.+?\/", self.website).group(0) + "robots.txt"
        example_url = self.website + str(self.min_longitude) + "," + str(self.min_latitude)
        robots = Robots.fetch(robots_url)
        if str(robots) == '{"*": []}':
            print("Provide valid url")
            return False
        if robots.allowed(example_url, "*"):
            return True
        else:
            print("Couldn't scrape {0} for {1}: disallowed by robots.txt".format(
                example_url, self.name))
            return False

    def loop_coordinates(self, datafile):
        self.dealers_list = []
        start = self.min_latitude + self.lat_step / 2 
        stop = self.max_latitude
        step = self.lat_step
        for lat in arange(start, stop, step):
            start = self.min_longitude + self.lon_step / 2 
            stop = self.max_longitude
            step = self.lon_step
            for lon in arange(start, stop, step):
                # lat = 52.25
                # lon = 21
                self.get_dealer_info_manuf(str(lat), str(lon), datafile)
                # break
            # break

    def get_dealer_info(self, element, xpath_path, attribute):
        try:
            if attribute == "text":
                data = element.find_element_by_xpath(xpath_path).text
            else:
                data = element.find_element_by_xpath(xpath_path).get_attribute(attribute)
                if data is None:
                    data = ""
            return data
        except NoSuchElementException:
            return ""


class Datafile:
    def __init__(self, name):
        self.name = name
        with open(name, 'w') as fp:
            fp.write(
                "Country;Dealer_Name;Dealer_Address;Dealer_Phone;"
                + "Dealer_Mail;Dealer_Website;Dealer_Coordinates;Monday;Tuesday"
                + ";Wednesday;Thursday;Friday;Saturday;Sunday;Manuf_link\n"
            )

    def append(self, data_list):
        with open(self.name, 'a') as fp:
            fp.write(";".join(data_list) + "\n")
