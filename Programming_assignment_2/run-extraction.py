import os
import sys
import time
import re
import json

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
    r'\input-extraction\rtvslo.si\Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
    r'\input-extraction\rtvslo.si\Volvo XC 40 D4 AWD momentum_ suvereno med najboljse v razredu - RTVSLO.si.html',
    r'\input-extraction\overstock.com\jewelry01.html',
    r'\input-extraction\overstock.com\jewelry02.html',
]

pages_url = [
    r'https://www.enaa.com/micro-sd-kartice/sandisk-ultra-microsdxc-128gb-100mb-s-class-10-uhs-i-sdsqunr-128g-gn3mn',
    r'https://www.enaa.com/micro-sd-kartice/spominska-kartica-samsung-evo-plus-micro-sdxc-256gb-u3-v30-a2-uhs-i-z-sd-adapterjem',
]

renderedPages = [
    r'\input-extraction\rtvslo.si\__Audi.html',
    r'\input-extraction\rtvslo.si\__Volvo.html',
    r'\input-extraction\overstock.com\__jewelry01.html',
    r'\input-extraction\overstock.com\__jewelry02.html',
    r'\input-extraction\_enaa.com\__sandisk-ultra-microsdxc-128gb-100mb-s-class-10-uhs-i-sdsqunr-128g-gn3mn.html',
    r'\input-extraction\_enaa.com\__spominska-kartica-samsung-evo-plus-micro-sdxc-256gb-u3-v30-a2-uhs-i-z-sd-adapterjem.html',
]


def regexRTV(s):
    author_pattern = r'<div class="author-name">(.*?)</div>'
    time_pattern = r'<div class="publish-meta">\s*(.*?)\s*<br>'
    title_pattern = r'<h1>(.*?)<\/h1>'
    subtitle_pattern = r'<div class="subtitle">(.*?)</div>'
    lead_pattern = r'<p class="lead">(.*?)</p>'

    author_match = re.search(author_pattern, s, re.DOTALL)
    time_match = re.search(time_pattern, s, re.DOTALL)
    title_match = re.search(title_pattern, s, re.DOTALL)
    subtitle_match = re.search(subtitle_pattern, s, re.DOTALL)
    lead_match = re.search(lead_pattern, s, re.DOTALL)

    json_rtv = {
        "author": "",
        "time": "",
        "title": "",
        "subTitle": "",
        "lead": "",
        "content": ""
    }

    if author_match:
        json_rtv["author"] = author_match.group(1)

    if time_match:
        json_rtv["time"] = time_match.group(1)

    if title_match:
        json_rtv["title"] = title_match.group(1)

    if subtitle_match:
        json_rtv["subTitle"] = subtitle_match.group(1)

    if lead_match:
        json_rtv["lead"] = lead_match.group(1)

    content_pattern = r'<article class="article">(.*?)<\/article>'
    p_pattern = r'<p.*?>(.*?)<\/p>'

    content_match = re.findall(content_pattern, s, re.DOTALL)
    if content_match:
        content_string = ""

        for content in content_match:
            p_matches = re.findall(p_pattern, content, re.DOTALL)
            for p in p_matches:
                clean_p = re.sub(r'<.*?>', '', p)
                if clean_p.strip() != '':
                    content_string += clean_p + '\n'

        json_rtv["content"] = content_string

    print(json.dumps(json_rtv))


def regexOverstock(s):
    item_pattern = r'(?<=<tbody>)(<tr\b[^>]*>[\s\S]*?<\/tr>)(?=<\/tbody>)'
    item_match = re.findall(item_pattern, s, re.DOTALL)

    title_pattern = r'<td valign="top">\s*<a\s[^>]*><b>(.*?)<\/b><\/a>'
    list_price_pattern = r'<b>List Price:</b></td><td align="left" nowrap="nowrap"><s>(.*?)</s>'
    price_pattern = r'<b>Price:</b></td><td align="left" nowrap="nowrap"><span class="bigred"><b>(.*?)</b></span>'
    saving_pattern = r'<b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">(.*?) \(.*?\)</span>'
    saving_percentage_pattern = r'<b>You Save:</b></td><td align="left" nowrap="nowrap"><span class="littleorange">.*? \((.*?)\)</span>'
    content_pattern = r'<span class="normal">(.*?)<br>'

    json_overstock = {"products": []}

    if item_pattern:
        for item in item_match:

            title_match = re.search(title_pattern, item, re.DOTALL)

            if title_match:
                #print("==================================================================")
                #print(title_match.group(1))

                list_price_match = re.search(list_price_pattern, item, re.DOTALL)
                price_match = re.search(price_pattern, item, re.DOTALL)
                saving_match = re.search(saving_pattern, item, re.DOTALL)
                saving_percentage_match = re.search(saving_percentage_pattern, item, re.DOTALL)
                content_match = re.search(content_pattern, item, re.DOTALL)

                if list_price_match:
                    list_price = list_price_match.group(1)
                    #print("LIST PRICE:", list_price_match.group(1))
                else:
                    list_price = None
                    print("Missing list price")

                if price_match:
                    price = price_match.group(1)
                    #print("PRICE:", price_match.group(1))
                else:
                    price = None
                    print("Missing price")

                if saving_match:
                    saving = saving_match.group(1)
                    #print("SAVING:", saving_match.group(1))
                else:
                    saving = None
                    print("Missing saving")

                if saving_percentage_match:
                    saving_percentage = saving_percentage_match.group(1)
                    #print("SAVING PERCENTAGE:", saving_percentage_match.group(1))
                else:
                    saving_percentage = None
                    print("Missing saving percentage")

                if content_match:
                    content = content_match.group(1)
                    #print("CONTENT:", content_match.group(1))
                else:
                    content = None
                    print("Missing content")

                json_overstock["products"].append({
                    "title": title_match.group(1),
                    "listPrice": list_price,
                    "price": price,
                    "saving": saving,
                    "saving_percentage": saving_percentage,
                    "content": content
                })

        return json.dumps(json_overstock)


def regexEnaa(s):


def runRegEx():
    print('RegEx Extraction started')

    for pagePath in renderedPages:
        print("__________________________________________________"+pagePath+"_______________________________________________________________")
        with codecs.open(ROOT_DIR + pagePath, "r", "utf-8") as f:
            s = f.read()

            print(pagePath[18:27])

            if pagePath[18:27] == "rtvslo.si":
                print(regexRTV(s))

            if pagePath[18:27] == "overstock":
                print(regexOverstock(s))

            if pagePath[18:27] == "_enaa.com":
                print(regexEnaa(s))


def runXPath():
    print('XPath Extraction started')


def runRoadRunner():
    print('RoadRunner started')


def getRenderHthmls():
    service = FirefoxService(executable_path=WEB_DRIVER_LOCATION)

    for url in pages_url:
        print(url)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.get(url)

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
