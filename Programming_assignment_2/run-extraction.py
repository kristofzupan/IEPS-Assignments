import os
import sys
import time
import re
import json
from lxml import html
from bs4 import BeautifulSoup
from bs4.element import Comment
from difflib import SequenceMatcher

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

    return json.dumps(json_rtv)


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
                list_price_match = re.search(list_price_pattern, item, re.DOTALL)
                price_match = re.search(price_pattern, item, re.DOTALL)
                saving_match = re.search(saving_pattern, item, re.DOTALL)
                saving_percentage_match = re.search(saving_percentage_pattern, item, re.DOTALL)
                content_match = re.search(content_pattern, item, re.DOTALL)

                if list_price_match:
                    list_price = list_price_match.group(1)
                else:
                    list_price = None
                    print("Missing list price")

                if price_match:
                    price = price_match.group(1)
                else:
                    price = None
                    print("Missing price")

                if saving_match:
                    saving = saving_match.group(1)
                else:
                    saving = None
                    print("Missing saving")

                if saving_percentage_match:
                    saving_percentage = saving_percentage_match.group(1)
                else:
                    saving_percentage = None
                    print("Missing saving percentage")

                if content_match:
                    content = content_match.group(1)
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
    title_pattern = r'<h1 itemprop="name" class="text-break">(.*?)</h1>'
    price_pattern = r'<div class="single-product-price">(.*?)<div'
    rating_pattern = r'<span itemprop="ratingValue">(.*?)</span>'
    review_count_pattern = r'<span itemprop="reviewCount">(.*?)</span>'
    brand_pattern = r'<div class="product-brand">\s*Znamka / dobavitelj: <a.*?>(.*?)</a>\s*</div>'
    description_pattern = r'<div class="single-product-description">.*?<p>(.*?)</p>\s*<br><a href="#opis">Celoten opis'

    title_match = re.search(title_pattern, s, re.DOTALL)
    price_match = re.search(price_pattern, s, re.DOTALL)
    rating_match = re.search(rating_pattern, s, re.DOTALL)
    review_count_match = re.search(review_count_pattern, s, re.DOTALL)
    brand_match = re.search(brand_pattern, s, re.DOTALL)
    description_match = re.search(description_pattern, s, re.DOTALL)

    json_enaa = {
        "title": "",
        "price": "",
        "rating": "",
        "reviewCount": "",
        "brand": "",
        "description": ""
    }

    if title_match:
        json_enaa["title"] = title_match.group(1).strip()

    if price_match:
        json_enaa["price"] = price_match.group(1).strip()

    if rating_match:
        json_enaa["rating"] = rating_match.group(1).strip()

    if review_count_match:
        json_enaa["reviewCount"] = review_count_match.group(1).strip()

    if brand_match:
        json_enaa["brand"] = brand_match.group(1).strip()

    if description_match:
        clean_desc = re.sub(r'<.*?>', '', description_match.group(1))
        json_enaa["description"] = clean_desc

    return json.dumps(json_enaa)

def runRegEx():
    print('RegEx Extraction started')

    for pagePath in renderedPages:
        print('\n')
        print("__________________________________________________________________________________________"+pagePath+"__________________________________________________________________________________________")
        print('\n')
        with codecs.open(ROOT_DIR + pagePath, "r", "utf-8") as f:
            s = f.read()

            if pagePath[18:27] == "rtvslo.si":
                print(regexRTV(s))

            if pagePath[18:27] == "overstock":
                print(regexOverstock(s))

            if pagePath[18:27] == "_enaa.com":
                print(regexEnaa(s))


def xPathRTV(s):
    author_pattern = "//div[@class='author-timestamp']/strong/text()"
    time_pattern = '//div[@class="author-timestamp"]/text()'
    title_pattern = '//h1/text()'
    subTitle_pattern = "//div[@class='subtitle']/text()"
    lead_pattern = "//p[@class='lead']/text()"
    content_pattern = "//article[@class='article']//p/text()"

    json_rtv = {
        "author": "",
        "time": "",
        "title": "",
        "subTitle": "",
        "lead": "",
        "content": ""
    }

    tree = html.fromstring(s)
    author = tree.xpath(author_pattern)
    timestamp = tree.xpath(time_pattern)
    title = tree.xpath(title_pattern)
    subTitle = tree.xpath(subTitle_pattern)
    lead = tree.xpath(lead_pattern)
    content = tree.xpath(content_pattern)

    if author:
        json_rtv["author"] = author[0]

    if time:
        json_rtv["time"] = timestamp[1].split("|")[1].strip()

    if title:
        json_rtv["title"] = title[0]

    if subTitle:
        json_rtv["subTitle"] = subTitle[0]

    if lead:
        json_rtv["lead"] = lead[0]

    if content:
        merged_content = " ".join(content)
        json_rtv["content"] = merged_content

    return json.dumps(json_rtv)


def xPathOverstock(s):
    title_pattern = "//tbody//tr[@bgcolor]//td[@valign]//a/b/text()"
    list_price_pattern = "//tbody//tr[@bgcolor]//td//table//tbody//tr//td//table//tbody//tr//td//s/text()"
    price_pattern = "//tbody//tr[@bgcolor]//td//table//tbody//tr//td//table//tbody//tr//td//span/b/text()"
    saving_pattern = "//tbody//tr[@bgcolor]//td//table//tbody//tr//td//table//tbody//tr//td//span[@class='littleorange']/text()"
    content_pattern = "//tbody//tr[@bgcolor]//td//table//tbody//tr//td/span[@class='normal']/text()"

    tree = html.fromstring(s)

    titles = tree.xpath(title_pattern)
    list_price = tree.xpath(list_price_pattern)
    price = tree.xpath(price_pattern)
    savings = tree.xpath(saving_pattern)
    content = tree.xpath(content_pattern)

    json_overstock = {"products": []}

    for i in range(0, len(titles)):
        pattern_saving = r'\$[\d,.]+|\d+%'
        saving_matches = re.findall(pattern_saving, savings[i])

        json_overstock["products"].append({
            "title": titles[i],
            "listPrice": list_price[i],
            "price": price[i],
            "saving": saving_matches[0],
            "saving_percentage": saving_matches[1],
            "content": content[i]
        })

    return json.dumps(json_overstock)


def xPathEnaa(s):
    title_pattern = "//div[@class='section-title']/h1[@itemprop='name']/text()"
    price_pattern = "//div[@class='single-product-price']/text()"
    rating_pattern = "//span[@itemprop='ratingValue']/text()"
    review_count_pattern = "//span[@itemprop='reviewCount']/text()"
    brand_pattern = "//div[@class='product-brand']/a/text()"
    description_pattern = "//div[@class='single-product-description']//text()[not(parent::a)]"

    json_enaa = {
        "title": "",
        "price": "",
        "rating": "",
        "reviewCount": "",
        "brand": "",
        "description": ""
    }

    tree = html.fromstring(s)

    title = tree.xpath(title_pattern)
    price = tree.xpath(price_pattern)
    rating = tree.xpath(rating_pattern)
    review_count = tree.xpath(review_count_pattern)
    brand = tree.xpath(brand_pattern)
    description = tree.xpath(description_pattern)

    merged_description = ""
    for item in description:
        if item.strip() != '':
            merged_description += " " + item.strip()

    json_enaa["title"] = title[0].strip()
    json_enaa["price"] = price[0].strip()
    json_enaa["rating"] = rating[0].strip()
    json_enaa["reviewCount"] = review_count[0].strip()
    json_enaa["brand"] = brand[0].strip()
    json_enaa["description"] = merged_description.strip()

    return json.dumps(json_enaa)


def runXPath():
    print('XPath Extraction started')

    for pagePath in renderedPages:
        print('\n')
        print("__________________________________________________________________________________________"+pagePath+"__________________________________________________________________________________________")
        print('\n')
        with codecs.open(ROOT_DIR + pagePath, "r", "utf-8") as f:
            s = f.read()

            if pagePath[18:27] == "rtvslo.si":
                print(xPathRTV(s))

            if pagePath[18:27] == "overstock":
                print(xPathOverstock(s))

            if pagePath[18:27] == "_enaa.com":
                print(xPathEnaa(s))

def preprocess_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
        
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()
    
    for element in soup.find_all(['head', 'noscript', 'option', 'select', 'footer', 'header']):
        element.extract()
        
    for element in soup.find_all(string=lambda text: not isinstance(text, Comment)):
        element.replace_with(re.sub(r'\s+', ' ', element))
    
    for element in soup.find_all():
        if element.name not in ['br', 'hr'] and (not element.text or not element.text.strip()):
            element.extract()
    
    cleaned_html = str(soup)
    return cleaned_html


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def generate_wrapper(segment):
    wrapper = ""
    patterns = {
        'title': r'<title>(.*?)</title>',
        'heading': r'<h\d>(.*?)</h\d>',
        'paragraph': r'<p>(.*?)</p>',
        'unordered_list': r'<ul>(.*?)</ul>',
        'ordered_list': r'<ol>(.*?)</ol>',
        'table': r'<table>(.*?)</table>',
        'table_row': r'<tr>(.*?)</tr>',
        'table_data': r'<td>(.*?)</td>',
        'link': r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"',
        'image': r'<img\s+(?:[^>]*?\s+)?src="([^"]*)"'
    }

    for element, pattern in patterns.items():
        matches = re.findall(pattern, segment, re.DOTALL)
        if matches:
            wrapper += f"{element}: {pattern}\n"
    
    return wrapper.strip()


def roadRunner(page1, page2, text_threshold=0.8):
    clean_page1 = preprocess_html(page1)
    clean_page2 = preprocess_html(page2)

    soup1 = BeautifulSoup(clean_page1, 'html.parser')
    soup2 = BeautifulSoup(clean_page2, 'html.parser')

    sturctures1 = soup1.find_all(['table', 'ul', 'ol', 'div'])
    sturctures2 = soup2.find_all(['table', 'ul', 'ol', 'div'])

    common_segments = []
    unique_segments1 = []
    unique_segments2 = []

    for structure1 in sturctures1:
        found = False
        for structure2 in sturctures2:
            if str(structure1) == str(structure2):
                common_segments.append(str(structure1))
                found = True
                break
            elif structure1.name == structure2.name and similar(structure1.get_text(), structure2.get_text()) >= text_threshold:
                tag_similarity = similar(str(structure1), str(structure2))
                if tag_similarity >= text_threshold:
                    common_segments.append(str(structure1))
                    found = True
                    break
        if not found:
            unique_segments1.append(str(structure1))

    for structure2 in sturctures2:
        found = False
        for structure1 in sturctures1:
            if str(structure1) == str(structure2):
                found = True
                break
            elif structure1.name == structure2.name and similar(structure1.get_text(), structure2.get_text()) >= text_threshold:
                tag_similarity = similar(str(structure1), str(structure2))
                if tag_similarity >= text_threshold:
                    found = True
                    break
        if not found:
            unique_segments2.append(str(structure2))

    unique_common_segments = list(set(common_segments))

    if unique_common_segments:
        print("Wrapper:")
        combined_wrapper = ""
        included_elements = set()
        for segment in unique_common_segments:
            wrapper = generate_wrapper(segment)
            if wrapper.strip() not in included_elements: 
                combined_wrapper += wrapper + "\n"
                included_elements.add(wrapper.strip())
        print(combined_wrapper.strip())
    return unique_common_segments


"""
def roadRunnerEnaa(s):
    result = {}
    soup = BeautifulSoup(s, 'html.parser')

    title_element = soup.select_one("h1[itemprop='name']")
    result['title'] = title_element.get_text(
        strip=True) if title_element else "Title not found"

    price_element = soup.select_one(".single-product-price")
    result['price'] = price_element.get_text(strip=True).split()[
        0] if price_element else "Price not found"

    rating_element = soup.select_one("span[itemprop='ratingValue']")
    result['rating'] = rating_element.get_text(
        strip=True) if rating_element else "Rating not found"

    review_count_element = soup.select_one("span[itemprop='reviewCount']")
    result['reviewCount'] = review_count_element.get_text(
        strip=True) if review_count_element else "Review count not found"

    brand_element = soup.select_one(".product-brand a")
    result['brand'] = brand_element.get_text(
        strip=True) if brand_element else "Brand not found"

    short_desc_element = soup.select(".single-product-description p")
    result['short_description'] = " ".join([desc.get_text(
        strip=True) for desc in short_desc_element]) if short_desc_element else "Short description not found"

    availability_elements = soup.select(
        ".single-product-side-info-items .single-product-side-info-item")
    shipping_date = None
    pickup_date = None
    for element in availability_elements:
        text = element.get_text(strip=True)
        date_text = element.select_one(".green.text-nowrap")
        if 'poslali' in text and date_text:
            shipping_date = date_text.get_text(strip=True)
        elif 'prevzem' in text and date_text:
            pickup_date = date_text.get_text(strip=True)
    result['shipping_date'] = shipping_date if shipping_date else "Shipping date not found"
    result['pickup_date'] = pickup_date if pickup_date else "Pickup date not found"

    product_code_element = soup.select_one(
        ".single-product-side-bottom > p:contains('Šifra izdelka')")
    if product_code_element:
        product_code = product_code_element.get_text(
            strip=True).replace('Šifra izdelka:', '').strip()
    else:
        product_code = "Product code not found"
    result['product_code'] = product_code

    loyalty_points_element = soup.select_one(
        ".single-product-side-bottom > p:contains('S točkami zvestobe do popustov')")
    if loyalty_points_element:
        loyalty_points = loyalty_points_element.get_text(strip=True).replace(
            'S točkami zvestobe do popustov:', '').strip()
    else:
        loyalty_points = "Loyalty points info not found"
    result['loyalty_points'] = loyalty_points

    basic_features_section = soup.select_one(
        '.single-product-bottom-col .single-product-bottom-content-properties')
    basic_features = {}
    if basic_features_section:
        features_list = basic_features_section.find_all('li')
        for feature in features_list:
            key = feature.find('b').get_text(strip=True).rstrip(':')
            value = feature.get_text(strip=True).replace(key, '').strip()
            basic_features[key] = value

    result['basic_features'] = basic_features

    comparison_section = soup.select_one('div.compare-items')
    comparison_results = []

    if comparison_section:
        product_items = comparison_section.select('div.grid-item')
        for item in product_items[1:]:
            product_info = {
                'title': item.select_one('.grid-item-title').get_text(strip=True) if item.select_one('.grid-item-title') else "No title",
                'price': item.select_one('.grid-item-price').get_text(strip=True) if item.select_one('.grid-item-price') else "No price",
                'rating': item.select_one('.product-rating-number').get_text(strip=True) if item.select_one('.product-rating-number') else "No rating",
                'details': {}
            }

            properties = item.select('.compare-item-properties > div')
            for prop in properties:
                if prop.get_text(strip=True):
                    detail_text = prop.get_text(strip=True)
                    split_details = detail_text.split(':', 1)
                    if len(split_details) > 1:
                        product_info['details'][split_details[0].strip(
                        )] = split_details[1].strip()
                    else:
                        product_info['details'][split_details[0].strip()
                                                ] = None

            comparison_results.append(product_info)

    result['product_comparison'] = comparison_results

    full_desc_section = soup.select_one(".single-product-bottom-section")
    full_description = ''
    if full_desc_section:
        paragraphs = full_desc_section.select(
            "p[property='v:description'], .single-product-bottom-content p")
        for p in paragraphs:
            full_description += p.get_text(' ', strip=True) + ' '
        result['full_description'] = full_description.strip()
    else:
        result['full_description'] = "Full description not found"

    return json.dumps(result, ensure_ascii=False, indent=4)


def roadRunnerOverstock(s):
    result = {"products": []}
    soup = BeautifulSoup(s, 'html.parser')

    titles = soup.select('tbody tr[bgcolor] td[valign] a b')
    list_prices = soup.select('tbody tr[bgcolor] td table tr td table tr td s')
    prices = soup.select(
        'tbody tr[bgcolor] td table tr td table tr td span.bigred b')
    savings = soup.select(
        'tbody tr[bgcolor] td table tr td table tr td span.littleorange')
    contents = soup.select('tbody tr[bgcolor] td table tr td span.normal')

    # 2 je ker nevem kk odstranit da ignorira "Click here to purchase."
    for i in range(0, len(titles), 2):
        saving_matches = re.findall(
            r'\$[\d,.]+|\d+%', savings[i//2].get_text(strip=True))

        extraction_result = {
            "title": titles[i].get_text(strip=True),
            "listPrice": list_prices[i//2].get_text(strip=True),
            "price": prices[i//2].get_text(strip=True),
            "saving": saving_matches[0],
            "saving_percentage": saving_matches[1] if len(saving_matches) > 1 else None,
            "content": contents[i//2].get_text(strip=True) if i//2 < len(contents) else None
        }
        result["products"].append(extraction_result)

    return result
"""

def runRoadRunner():
    print('RoadRunner started')

    for i in range(0, len(renderedPages)-1, 2):
        with codecs.open(ROOT_DIR + renderedPages[i], "r", "utf-8") as f:
            s1 = f.read()
        with codecs.open(ROOT_DIR + renderedPages[i+1], "r", "utf-8") as f:
            s2 = f.read()
        print('\n')
        print("__________________________________________________________________________________________"+renderedPages[i][18:27]+"__________________________________________________________________________________________")
        print('\n')

        roadRunner(s1, s2)


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
