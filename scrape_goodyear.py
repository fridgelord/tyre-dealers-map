# import logging as log
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from numpy import arange
from time import sleep
from datetime import datetime
import pandas as pd
import get_country_data
import geopy.distance
from reppy.robots import Robots # only library that properly parses michelin.pl
                                # also it's fastest


elements = {
    "dealers": "//div[contains(@class, 'dealer-detail')]",
    "link": ["./h2/a[contains(@class, 'cta-txt no-arrow')]", "href"],
    "name": ["./h2/a[contains(@class, 'cta-txt no-arrow')", "text"],
    "address": ["./p[contains(@class, 'dealer-location')]", "text"],
    "phone": ["./p[contains(@class, 'dealer-location')]", "text"],
    "mail": [".//a[contains(@class, 'cta-icon icon-envelope')]/span", "text"],
    "website": ["./section[contains(@class, 'dealer-info')]//a[contains(@class, 'cta-txt')]"
                , "href"],
    "hours_text": [".//table[contains(@class, 'dealer-opening-hours')]", "outerHTML"],
}


def site(
    base_url,
    dealer_locator_url,
    latitude, 
    longitude, 
    country_tag="", 
    page_no=""
):
    if country_tag:
        country_tag = ("/" + country_tag).replace("//", "/")
    if page_no != "":
        page_no = "&page=" + str(page_no) + "&r=0"
    return (
        base_url + 
        country_tag + 
        dealer_locator_url + 
        str(latitude) + 
        "," +
        str(longitude) +
        page_no  
    )


def open_site(country_tag, latitude, longtitude, page_no=1):
    sleep(1)
    global driver
    try:
        driver.maximize_window()
        driver.get(site(base_url,
                        dealer_locator_url,
                        latitude,
                        longtitude,
                        country_tag=country_tag,
                        page_no=page_no,
                       )
                  )
        try:
            cookie_consent = driver.find_element_by_class_name("cmp-link__link")
            cookie_consent.click()
        except NoSuchElementException:
            pass
        except ElementNotInteractableException:
            pass
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "dealer-detail"))
            )
            # display all phones
            phone_wrappers = driver.find_elements_by_xpath(
                ".//div[contains(@class, 'dealer-phone-wrapper')]"
            )
            for element in phone_wrappers:
                element.click()
            hours_wrappers = driver.find_elements_by_xpath(
                ".//div[contains(@class, 'dealer-hours-wrapper')]"
            )
            for element in hours_wrappers:
                element.click()
            return True
        except TimeoutException:
            return False
    except WebDriverException:
        driver = webdriver.Firefox()
        open_site(country_tag, latitude, longtitude, page_no)


def get_dealer_info(element, xpath_path, attribute):
    try:
        if attribute == "text":
            data = element.find_element_by_xpath(xpath_path).text
        else:
            data = element.find_element_by_xpath(xpath_path).get_attribute(attribute)
            if data == None:
                data = ""
        return data
    except NoSuchElementException:
        return ""


def opening_hours_list(html):
    if html == "":
        return ["" for i in range(0, 7)]
    try:
        df = pd.read_html(html)[0]
        return [df.iloc[x, 1] + "-" + df.iloc[x, 2] for x in range(0, 7)]
    except Exception as e:
        return ["" for i in range(0, 7)]


def get_dealers_info_from_page(elements_dict, filename, dealers_data):
    dealers = driver.find_elements_by_xpath(elements_dict["dealers"])
    for dealer in dealers:
        link = get_dealer_info(
            dealer,
            elements_dict["link"][0],
            elements_dict["link"][1],
        )
        if link not in dealers_data:
            coordinates = dealer.get_attribute("data-latlng")

            name = get_dealer_info(
                dealer,
                elements_dict["name"][0],
                elements_dict["name"][1],
            )
            address = get_dealer_info(
                dealer,
                elements_dict["address"][0],
                elements_dict["address"][1],
            )
            phone = get_dealer_info(
                dealer,
                elements_dict["phone"][0],
                elements_dict["phone"][1],
            )
            mail = get_dealer_info(
                dealer,
                elements_dict["name"][0],
                elements_dict["name"][1],
            )
            website = get_dealer_info(
                dealer,
                elements_dict["website"][0],
                elements_dict["website"][1],
            )
            hours_text = get_dealer_info(
                dealer,
                elements_dict["hours_text"][0],
                elements_dict["hours_text"][1],
            )
            dealers_data[link] = [
                country_name,
                name,
                address,
                phone,
                mail,
                website,
                coordinates,
            ] + opening_hours_list(hours_text)
            with open(filename, mode="a") as file:
                file.write(";".join(dealers_data[link]) + link + "\n")
    return dealers_data


def convert_coordinates(country, km_step):
    min_lat = country["min_lat"]
    max_lat = country["max_lat"]
    min_lon = country["min_lon"]
    max_lon = country["max_lon"]
    left_bottom = (min_lat, min_lon)
    right_bottom = (min_lat, max_lon)
    left_top = (max_lat, min_lon)
    lat_span = geopy.distance.distance(left_bottom, left_top).kilometers
    lon_span = geopy.distance.distance(left_bottom, right_bottom).kilometers
    lon_step = (max_lon - min_lon) * km_step / lon_span
    lat_step = (max_lat - min_lat) * km_step / lat_span
    return min_lat, max_lat, lat_step, min_lon, max_lon, lon_step



def get_dealers_info(country_name, country, filename, elements_dict):
    km_step = 100  # kilometers
    dealers_data = {}
    country_tag = country["country_tag"]
    min_lat, max_lat, lat_step, min_lon, max_lon, lon_step = convert_coordinates(
        country, 
        km_step,
    )
    for lat in arange(min_lat + lat_step / 2, max_lat, lat_step):
        for lon in arange(min_lon + lon_step / 2, max_lon, lon_step):
            for i in range(1, 200):
                # lat = 50.25052385714285
                # lon = 16.26666692857143
                if open_site(country_tag, latitude=lat, longtitude=lon, page_no=i):
                    dealers_data = get_dealers_info_from_page(elements_dict, 
                                                              filename,
                                                              dealers_data,
                                                             )
                else:
                    break
            break
        break



base_url = "https://www.goodyear.eu"
dealer_locator_url = "/consumer/dealers/results.html?latlng="
robots_url = "/robots.txt"

start = datetime.now()
filename = "dealers_goodyear.csv"
with open(filename, mode="w") as file:
    file.write(
        "Country;Dealer_Name;Dealer_Address;Dealer_Phone;"
        + "Dealer_Mail;Dealer_Website;Dealer_Coordinates;Monday;Tuesday"
        + ";Wednesday;Thursday;Friday;Saturday;Sunday;Manuf_link\n"
    )

driver = webdriver.Firefox()

countries = get_country_data.get_country_data()
with open('country_list.json') as fp:
    countries_gy = json.load(fp)

countries_gy_full = {
    country_name: {
        "country_tag": tag,
        "min_lon": countries[country_name]["min_lon"],
        "max_lon": countries[country_name]["max_lon"],
        "min_lat": countries[country_name]["min_lat"],
        "max_lat": countries[country_name]["max_lat"],
    }
    for country_name, tag in countries_gy.items()
}


for country_name, country in countries_gy_full.items():
    robots = Robots.fetch(base_url + robots_url)
    example_site = site(base_url,
                        dealer_locator_url,
                        0,
                        0,
                        country["country_tag"],
                        0,
                       )
    if not robots.allowed(example_site, "*"):
        print("Couldn't scrape {0} for {1}: disallowed by robots.txt".format(
            base_url, country_name))
        continue
    else:
        print("we're ok")
        get_dealers_info(country_name, country, filename, elements)
driver.close()
