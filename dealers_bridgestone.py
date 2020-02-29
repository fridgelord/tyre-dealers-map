from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

filename = "dealers_bridgestone.csv"
countries = {
    "Austria": "at",
    "Belgium": "be/fr",
    "Denmark": "dk",
    "Estonia": "ee",
    "Finland": "fi",
    "France": "fr",
    "Greece": "gr",
    "Spain": "es",
    "The Netherlands": "nl",
    "Ireland": "ie",
    "Lithuania": "lt",
    "Latvia": "lv",
    "Germany": "de",
    "Poland": "pl",
    "Portugal": "pt",
    "Czech Republic": "cz",
    "Romania": "ro",
    "Switzerland": "ch/fr",
    "Sweden": "se",
    "Hungary": "hu",
    "Italy": "it",
    "UK": "gb",
}


def get_cities_links(country_tag, driver):
    cities_links = []
    driver.get(f"https://www.bridgestone.pl/gdzie-kupić/{country_tag}")
    try:
        a = driver.find_element_by_class_name("cookie-accept-block-button").click()
    except NoSuchElementException:
        pass
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located(
            (By.ID, "phmain_0_rptAlphabet_rptCities_0_hlCity_0")
        )
    )
    for i in range(0, 1000):
        for j in range(0, 1000):
            try:
                city_link = driver.find_element_by_id(
                    f"phmain_0_rptAlphabet_rptCities_{i}_hlCity_{j}"
                )
            except NoSuchElementException:
                break
            cities_links.append([city_link.get_attribute("href"), city_link.text])
    return cities_links


def get_dealers_info(cities_links, driver, country_name):
    dealers = []
    for city_link in cities_links:
        driver.get(city_link[0])
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.ID, "phmain_0_rptDealers_hplDealerName_0")
                )
            )
        except TimeoutException:
            continue
        for i in range(0, 1000):
            dealer = [country_name, city_link[1]]
            try:
                a = driver.find_element_by_id(f"phmain_0_rptDealers_liDealer_{i}")
                dealer.append(
                    a.find_element_by_id(f"phmain_0_rptDealers_hplDealerName_{i}").text
                )
                try:
                    info = a.find_element_by_class_name("info").text
                    info = re.sub(
                        city_link[1].replace("(", "\\(").replace(")", "\\)"),
                        "",
                        info,
                        flags=re.IGNORECASE,
                    ).strip()
                    info = info.split(" | ")[0]
                    info = info.split(" - ", 1)
                    info = info[1].rsplit(" - ", 1)
                    dealer += info
                except NoSuchElementException:
                    dealer += ["", ""]
                try:
                    dealer.append(
                        a.find_element_by_id(
                            f"phmain_0_rptDealers_hplPhone_{i}"
                        ).get_property("text")
                    )
                except NoSuchElementException:
                    dealer.append("")
            except NoSuchElementException:
                break
            dealers.append(dealer)
    return dealers


driver = webdriver.Firefox(firefox_binary="/usr/bin/firefox")

with open(filename, mode="w") as file:
    file.write(
        "Country;Dealer_City;Dealer_Name;Dealer_Street;Dealer_Post_Code;Dealer_Phone\n"
    )

for country_name, country_tag in countries.items():
    cities_links = get_cities_links(country_tag, driver)
    dealers = get_dealers_info(cities_links, driver, country_name)
    with open(filename, mode="a") as file:
        for line in dealers:
            file.write(";".join(line) + "\n")
driver.close()
