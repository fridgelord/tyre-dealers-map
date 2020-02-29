from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from numpy import arange
from time import sleep
from datetime import datetime
import pandas as pd
import get_country_data
import geopy.distance


countries_gy = {
    # "Austria": "de_at",
    # "Belgium": "fr_be",
    # "Denmark": "da_dk",
    # "Estonia": "et_ee",
    # "Finland": "fi_fi",
    # "France": "fr_fr",
    # "Greece": "el_gr",
    # "Spain": "es_es",
    # "Netherlands": "nl_nl",
    # "Ireland": "en_ie",
    # "Lithuania": "lt_lt",
    # "Latvia": "lv_lv",
    # "Germany": "de_de",
    # "Poland": "pl_pl",
    # "Portugal": "pt_pt",
    # "Czech Republic": "cs_cz",
    # "Romania": "ro_ro",
    # "Switzerland": "fr_ch",
    # "Sweden": "sv_se",
    # "Hungary": "hu_hu",
    # "Italy": "it_it",
    "United Kingdom": "en_gb",
    # "Bulgaria": "bg_bg",
    # "Croatia": "hr_hr",
    # "Norway": "no_no",
    # "Russian Federation": "ru_ru",
    # "Slovenia": "sl_si",
    # "Slovakia": "sk_sk",
    # "South Africa": "en_za",
    # "Serbia": "sr_rs",
    # "Turkey": "tr_tr",
    # "Ukraine": "uk_ua",
}


def site(country_tag, latitude, longtitude, page_no):
    return f"https://www.goodyear.eu/{country_tag}" +        f"/consumer/dealers/results.html?latlng={str(latitude)},{str(longtitude)}&page={str(page_no)}&r=0"

def open_site(country_tag, latitude, longtitude, page_no=1):
    sleep(1)
    global driver
    try:
        driver.maximize_window()
        driver.get(site(country_tag, latitude, longtitude, page_no))
        try:
            cookie_consent = driver.find_element_by_class_name("cmp-link__link")
            cookie_consent.click()
        except NoSuchElementException:
            pass
        except ElementNotInteractableException:
            pass
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "dealer-detail")
                )
            )
            #display all phones
            phone_wrappers = driver.find_elements_by_xpath(".//div[contains(@class, 'dealer-phone-wrapper')]")
            for element in phone_wrappers:
                element.click()
            hours_wrappers = driver.find_elements_by_xpath(".//div[contains(@class, 'dealer-hours-wrapper')]")
            for element in hours_wrappers:
                element.click()
            return True
        except TimeoutException:
            return False
    except WebDriverException:
        driver = webdriver.Firefox()
        open_site(country_tag, latitude, longtitude,  page_no)


def get_dealer_info(element, xpath_path, attribute):
    try:
        if attribute == "text":
            data = element.find_element_by_xpath(xpath_path).text
        else:
            data = element.find_element_by_xpath(xpath_path).get_attribute(attribute)
            if data == None: data = ""
        return data
    except NoSuchElementException:
        return ""

def opening_hours_list(html):
    if html == "":
        return ["" for i in range(0,7)]
    try:
        df = pd.read_html(html)[0]
        return [df.iloc[x,1]+"-"+df.iloc[x,2] for x in range(0,7)]
    except Exception as e:
        print(e.message, e.args)
        return ["" for i in range(0,7)]


def get_dealers_info(country_name, country,  filename):
    km_step = 100 # kilometers
    dealers_data = {}
    country_tag = country['country_tag']
    min_lat = country['min_lat']
    max_lat = country['max_lat']
    min_lon = country['min_lon']
    max_lon = country['max_lon']
    left_bottom = (min_lat, min_lon)
    right_bottom = (min_lat, max_lon)
    left_top = (max_lat, min_lon)
    lat_span = geopy.distance.distance(left_bottom, left_top).kilometers
    lon_span = geopy.distance.distance(left_bottom, right_bottom).kilometers
    lon_step = (max_lon - min_lon) * km_step/ lon_span
    lat_step = (max_lat - min_lat) * km_step / lat_span
    for lat in arange(min_lat + lat_step / 2, max_lat, lat_step):
        for lon in arange(min_lon + lon_step / 2, max_lon, lon_step):
            for i in range(1, 200):
#                 lat = 50.25052385714285
#                 lon = 16.26666692857143
                if open_site(country_tag, latitude=lat, longtitude=lon,  page_no=i):
                    dealers = driver.find_elements_by_xpath("//div[contains(@class, 'dealer-detail')]")
                    for dealer in dealers:
                        link = get_dealer_info(dealer, "./h2/a[contains(@class, 'cta-txt no-arrow')]", "href")
                        if link not in dealers_data:
                            coordinates = dealer.get_attribute("data-latlng")
                            name = get_dealer_info(dealer, "./h2/a[contains(@class, 'cta-txt no-arrow')]", "text")
                            address = get_dealer_info(dealer, "./p[contains(@class, 'dealer-location')]", "text")
                            phone = get_dealer_info(dealer, ".//div[contains(@class, 'dealer-phone-inner-wrapper')]/span", "text")
                            mail = get_dealer_info(dealer, ".//a[contains(@class, 'cta-icon icon-envelope')]/span", "text")
                            website = get_dealer_info(dealer, "./section[contains(@class, 'dealer-info')]//a[contains(@class, 'cta-txt')]", "href")
                            hours_text = get_dealer_info(dealer, ".//table[contains(@class, 'dealer-opening-hours')]", "outerHTML")
                            dealers_data[link] = [country_name,
                                                  name,
                                                  address,
                                                  phone,
                                                  mail,
                                                  website,
                                                  coordinates, ] + opening_hours_list(hours_text)
                            with open(filename, mode='a') as file:
                                file.write(";".join(dealers_data[link])+";"+link+";"+str(lat)+";"+str(lon)+"\n")
                else:
                    break




start = datetime.now()
filename = 'dealers_goodyear.csv'
with open(filename,mode='w') as file:
    file.write('Country;Dealer_Name;Dealer_Address;Dealer_Phone;'+\
        'Dealer_Mail;Dealer_Website;Dealer_Coordinates;Monday;Tuesday' +\
        ';Wednesday;Thursday;Friday;Saturday;Sunday;Manuf_link\n')

driver = webdriver.Firefox()

countries = get_country_data.get_country_data()

countries_gy_full = {
    country_name: {"country_tag": tag,
                   "min_lon": countries[country_name]["min_lon"],
                   "max_lon": countries[country_name]["max_lon"],
                   "min_lat": countries[country_name]["min_lat"],
                   "max_lat": countries[country_name]["max_lat"],
                   }
    for country_name, tag in countries_gy.items()
}



for country_name, country in countries_gy_full.items():
    get_dealers_info(country_name, country, filename)
    print(f"{datetime.now() - start} elapsed")
    # with open(filename,mode='a') as file:
    #     for link, data in dealers.items():
    #         file.write(";".join(data)+";"+link+'\n')
driver.close()

