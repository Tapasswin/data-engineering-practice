# import boto3
# from botocore import UNSIGNED
# from botocore.config import Config
import requests
import gzip
from io import BytesIO
import os

def main():
    download_path = "./downloads"
    os.makedirs(download_path, exist_ok=True)
    # s3 = boto3.client("s3")
    # response = s3.get_object(Bucket = "commoncrawl", Key = "crawl-data/CC-MAIN-2022-05/wet.paths.gz")
    # data = response['Body'].read().decode('utf-8')
    # print(data)

    url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2022-05/wet.paths.gz"
    try:
        # Requirement: DO NOT download the initial gz file onto disk.
        # response.content is kept in RAM; BytesIO wraps it as a file-like object
        # so gzip can decompress it without ever writing to disk.
        response = requests.get(url)
        if response.status_code == 200:
            with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8', errors='ignore') as f:
                # encoding='utf-8' avoids relying on Windows' default cp1252 decoder,
                # which crashes on non-cp1252 bytes in crawled text.
                # errors='ignore' skips any stray undecodable bytes.
                data = f.read().strip().split('\n')  # list of WET file paths
                final_url = "https://data.commoncrawl.org/" + data[0]

                # stream=True: do NOT buffer the whole HTTP response body in memory
                # up front — response.raw becomes a live streaming socket instead.
                data_response = requests.get(final_url, stream=True)

                # Feed the raw streaming socket directly into gzip.open(), so
                # decompression happens on the fly, chunk by chunk, instead of
                # requiring the full compressed file to be downloaded first.
                with gzip.open(data_response.raw, 'rt', encoding='utf-8', errors='ignore') as file:
                    # Requirement: DO NOT load the entire final file into memory.
                    # Iterating over the file object streams it line-by-line —
                    # only one line is held in memory at a time.
                    # (file.read() would instead pull the entire decompressed
                    # content into one big string before printing anything.)
                    for f in file:
                        print(f, end='')

    except Exception as e:
        print(f"Failed to download {url}. Error: {e}")

if __name__ == "__main__":
    main()