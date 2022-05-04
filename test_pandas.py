import requests
import pandas

url = "https://baseball.fantasysports.yahoo.com/b1/buzzindex"
source = requests.get(url).text
table = pandas.read_html(source)[0]
print(table)
