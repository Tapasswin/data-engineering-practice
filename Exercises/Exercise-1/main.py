import requests
import os
import zipfile
import asyncio
import aiohttp

download_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

async def download_files(session, url, download_path):
    filename = url.split("/")[-1]
    zip_path = f"{download_path}/{filename}"
    # response = requests.get(url)

    # if response.status_code == 200:
    #     # Downloads the folder to downloads directory
    #     with open(zip_path,"wb") as f:
    #         f.write(response.content)
    #     # Extract the folder in download directory
    #     with zipfile.ZipFile(zip_path, 'r') as zf:
    #         all_files = zf.namelist()
    #         csv_files = [file for file in all_files if file.endswith('.csv')]
    #         for file in csv_files:
    #             zf.extract(file, download_path)
        
    #     os.remove(zip_path)
    # else:
    #     print(f"Failed to download {filename}. status code: {response.status_code}")
    try:
        async with session.get(url, timeout=45) as response:
            if response.status != 200:
                print(f"Failed to download {filename}. status code: {response.status}")
                return
            content = await response.read()
    except aiohttp.ClientError as e:
        print(f"Failed to download {filename}. Error: {e}")
        return
    
    with open(zip_path, "wb") as f:
        f.write(content)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as f:
            all_files = f.namelist()
            csv_files = [files for files in all_files if files.endswith('.csv')]
            for files in csv_files:
                f.extract(files, download_path)
    except zipfile.BadZipFile as e:
        print(f"Failed to extract {filename}. Error: {e}")
        return
    
    os.remove(zip_path)


async def main():
    download_path = "Exercises\Exercise-1/downloads"
    os.makedirs(download_path, exist_ok=True)
    
    # for url in download_uris:
    #     download_files(url, download_path)
    
    async with aiohttp.ClientSession() as session:
        task = [download_files(session, url, download_path) for url in download_uris]
        await asyncio.gather(*task)

if __name__ == "__main__":
    asyncio.run(main())  

# Key concepts to lock in:

# aiohttp.ClientSession() — like requests.Session(), but async. You create one session and reuse it across all requests (connection pooling) rather than opening a new connection per call.
# async with session.get(url) as response — the async equivalent of requests.get(url). The async with ensures the connection is properly released back to the pool when done.
# await response.read() — this is the async version of response.content. The await is what lets the event loop go do other work (like starting another download) while this one is waiting on bytes from the network.
# asyncio.gather(*tasks) — this is what actually runs all the downloads concurrently. You build a list of coroutine objects (tasks), then gather schedules and runs them all together, waiting for all to finish.
# Why disk write/zip extraction stays synchronous — open(), f.write(), and zipfile are blocking, CPU/disk-bound operations, not network I/O. asyncio only helps with I/O-bound waiting (like network calls); it doesn't make disk writes faster. Mixing them in is fine for this scale — if file sizes were huge, you'd look at aiofiles or push the write into a thread pool via loop.run_in_executor.