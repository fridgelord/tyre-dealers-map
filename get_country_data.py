import pandas as pd
import json
import requests
import os.path

default_data_file = "cow.txt"
default_url = "https://web.archive.org/web/20150319012353/http://opengeocode.org/cude/download.php?file=/home/fashions/public_html/opengeocode.org/download/cow.txt"


def download_country_data(
    url=default_url,
    filename=default_data_file,
    force=False
):
    """Download data from given URL and dump
    into text file
    """
    if not os.path.isfile(filename) or force:
        text = requests.get(url).text
        with open(filename, 'w') as fp:
            fp.write(text)


def read_country_csv(filename=default_data_file):
    return pd.read_csv(filename,
                       sep=";",
                       skiprows=28,
                       keep_default_na=True,
                       )


def convert_to_dict(df):
    """Select country name and abbrv, min & max latitude
    and longitude as well as total area of countries
    Return dictionary country_name:dict of values
    """
    df = df[['ISO3166A2',
             'ISOen_ro_name',
             'minlongitude',
             'maxlongitude',
             'minlatitude',
             'maxlatitude',
             'land_total',
             ]]
    df.ISOen_ro_name = df.ISOen_ro_name.str.strip()
    df.set_index('ISOen_ro_name', inplace=True)
    df.columns = ['country_tag',
                  'min_lon',
                  'max_lon',
                  'min_lat',
                  'max_lat',
                  'area',
                  ]
    df.loc[:, "country_tag"] = df.loc[:, "country_tag"].str.lower()
    return {i[0]: i[1].to_dict() for i in df.iterrows()}


def dump_json(countries, filename='countries.json'):
    with open(filename, "w") as file:
        json.dump(countries, file)


if __name__ == '__main__':
    download_country_data()
    df = read_country_csv()
    country_dict = convert_to_dict(df)
