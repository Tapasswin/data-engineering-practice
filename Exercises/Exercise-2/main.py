import requests
import pandas
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import os
import pandas as pd

def data_read(download_path,filename):
    df = pd.read_csv(f"{download_path}/{filename}", low_memory=False)
    df["HourlyDryBulbTemperature"] = pd.to_numeric(df["HourlyDryBulbTemperature"], errors='coerce')
    df["HourlyDryBulbTemperature"] = df["HourlyDryBulbTemperature"].fillna(0)
    highest_temp = df["HourlyDryBulbTemperature"].max()
    print(f"Highest Temperature in {filename} is {highest_temp}")

def downloaded_files(url, download_path):
    filename = url.split("/")[-1]

    try:
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            print(f"Failed to download {filename}. status code: {response.status_code}")
            return
        with open(f"{download_path}/{filename}", "wb") as f:
            f.write(response.content)
        data_read(download_path,filename)
    except requests.RequestException as e:
        print(f"Failed to download {filename}. Error: {e}")
        return

def main():
    download_uri=[]
    url = "https://www.ncei.noaa.gov/data/local-climatological-data/access/2021/"
    download_path = "./downloads"
    os.makedirs(download_path, exist_ok=True)
   
    html = requests.get(url)
    parsed_html = BeautifulSoup(html.text,"html.parser")
    row = parsed_html.find_all("tr")

    for r in row:
        data = r.find_all("td")
        if data and "2024-01-19 15:27" in data[1].text:
            download_uri.append(os.path.join(url, data[0].text.strip()))
    
    for url in download_uri:
        downloaded_files(url, download_path)
if __name__ == "__main__":
    main()
