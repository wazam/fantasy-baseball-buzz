import requests
import pandas as pd

url = "https://baseball.fantasysports.yahoo.com/b1/buzzindex"
source = requests.get(url).text
table = pd.read_html(source)[0]
print(table)
