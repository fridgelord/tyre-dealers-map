import pandas as pd


gy = pd.read_csv("dealers_goodyear.csv",
                dtype="str",
                 sep=";",
                keep_default_na=False,
                usecols=range(0,15),
                )
gy.rename(columns={"Dealer_Address": "Dealer_Address_Full"}, inplace=True)

gy.drop_duplicates(inplace=True)
gy.reset_index(inplace=True, drop=True)
gy.replace("Zamknięte-Zamknięte","Closed", inplace=True)

regex = r'(.*?)\s*,\s*(\w*\d+-*\d*(\s?\d\w+|)) \s*(.*)'
tmp = gy.Dealer_Address_Full.str.extract(regex, )
gy = pd.merge(gy, tmp, left_index=True, right_index=True )
gy.rename(columns={0: "Address",
                   1: "Post_Code",
                   3: "City"},
          inplace=True,
          )
gy.drop(2, axis=1, inplace=True)

gy.to_excel("dealers_goodyear.xlsx",
           index=False,
           )
