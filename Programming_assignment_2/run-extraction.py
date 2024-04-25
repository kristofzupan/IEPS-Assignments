import os
import sys
import time
import re

import codecs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WEB_DRIVER_LOCATION = "geckodriver.exe"
# WEB_DRIVER_LOCATION = "./Programming_assignment_1/geckodriver.exe"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Firefox setup
firefox_options = FirefoxOptions()
# Uncomment the following line if you want to run headless
# firefox_options.add_argument("--headless")
firefox_options.add_argument("user-agent=fri-wier-Skupina_G")
# Update the binary location based on your Firefox installation path
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
firefox_options.accept_insecure_certs = True

pages = [
    r'\rtvslo.si\Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
    r'\rtvslo.si\Volvo XC 40 D4 AWD momentum_ suvereno med najboljse v razredu - RTVSLO.si.html',
    r'\overstock.com\jewelry01.html',
    r'\overstock.com\jewelry02.html',
]

renderedPages = [
    r'\rtvslo.si\__Audi.html',
    r'\rtvslo.si\__Volvo.html',
    r'\overstock.com\__jewelry01.html',
    r'\overstock.com\__jewelry02.html',
]


def runRegEx():
    print('RegEx Extraction started')

    for pagePath in renderedPages:
        print("__________________________________________________"+pagePath+"_______________________________________________________________")
        with codecs.open(ROOT_DIR + pagePath, "r", "utf-8") as f:
            s = f.read()

            author_pattern = r'<div class="author-name">(.*?)</div>'
            time_pattern = r'<div class="publish-meta">\s*(.*?)\s*<br>'
            title_pattern = r'<h1>(.*?)<\/h1>'
            subtitle_pattern = r'<div class="subtitle">(.*?)</div>'
            lead_pattern = r'<p class="lead">(.*?)</p>'
            content_pattern = r'(?<=<article class="article">)[\s\S]*?(?=<p class="Body">)([\s\S]*?)(<\/article>)'

            author_match = re.search(author_pattern, s, re.DOTALL)
            time_match = re.search(time_pattern, s, re.DOTALL)
            title_match = re.search(title_pattern, s, re.DOTALL)
            subtitle_match = re.search(subtitle_pattern, s, re.DOTALL)
            lead_match = re.search(lead_pattern, s, re.DOTALL)
            content_match = re.search(content_pattern, s, re.DOTALL)

            if author_match:
                print("AUTHOR:", author_match.group(1))

            if time_match:
                print("TIME:", time_match.group(1))

            if title_match:
                print("TITLE:", title_match.group(1))

            if subtitle_match:
                print("SUB TITLE:", subtitle_match.group(1))

            if lead_match:
                print("LEAD:", lead_match.group(1))

            if content_match:
                print("CONTENT:", content_match.group(1))


def runXPath():
    print('XPath Extraction started')


def runRoadRunner():
    print('RoadRunner started')


def getRenderHthmls():
    service = FirefoxService(executable_path=WEB_DRIVER_LOCATION)

    for url in pages:
        print(url)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.get(ROOT_DIR + url)

        filename = os.path.basename(url)

        # Remove the file extension
        filename_without_extension = os.path.splitext(filename)[0]

        # Get the first word
        first_word = filename_without_extension.split()[0]

        time.sleep(10)
        f = codecs.open("__"+first_word+".html", "w", "utf-8")
        f.write(driver.page_source)
        f.close()
        driver.quit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python run-extraction.py <parameter>")
        return

    parameter = sys.argv[1]

    if parameter != 'A' and parameter != 'B' and parameter != 'C':
        print("Parameter should be either A, B or C")
        return

    # getRenderHthmls() # Use this to get one html file that has the whole page rendered. Files are returned to the root folder, and should be placed in to the correct folder

    if parameter == 'A':
        runRegEx()

    if parameter == 'B':
        runXPath()

    if parameter == 'C':
        runRoadRunner()


if __name__ == "__main__":
    main()
