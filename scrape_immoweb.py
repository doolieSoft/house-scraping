import argparse
import csv
import datetime
import json
import logging
import re
import shutil
import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_json", help="Config path to load", required=True)
    args = parser.parse_args()

    with open(args.config_json) as config_file:
        config = json.load(config_file)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(filename=config['log_full_path'],
                        level=logging.DEBUG,
                        format='%(asctime)s[ %(levelname)s ][ %(pathname)s:%(lineno)d ] %(message)s')

    ua = UserAgent()
    # chrome_options = Options()
    # chrome_options.add_argument('headless')
    # chrome_options.add_argument('disable-extensions')
    # chrome_options.add_argument('no-proxy-server')
    # chrome_options.add_argument("--proxy-server='direct://'");
    # chrome_options.add_argument("--proxy-bypass-list=*");
    # driver = webdriver.Chrome(executable_path="C:\\Users\\c158492\\chromedriver_win32\\chromedriver.exe",
    #                          chrome_options=chrome_options)
    driver = webdriver.Chrome(executable_path="C:\\Users\\c158492\\chromedriver_win32\\chromedriver.exe")

    time.sleep(2)
    driver.maximize_window()

    page = "&page=1"
    url = config['url'] + page
    logging.debug("Url scrapped : {}".format(url))
    try:
        time.sleep(2)
        driver.get(url)

        driver.get_screenshot_as_file('screen1.png')
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        last_page = None
        for el in soup.find_all('div', attrs={'id': 'bottomGalNav'}):
            last_page = el.find_all('li', attrs={'id': re.compile('page-\d')})[-1]
        logging.debug("Last page of results : {}".format(last_page.text))

        dict_house = {}
        iscrape = 0
        for ipage in range(1, int(last_page.text) + 1):
            # for ipage in range(3, 4):
            old_page = page
            page = "&page=" + str(ipage)
            url = url.replace(old_page, page)

            driver.get(url)
            iscrape += 1
            if iscrape > 30:
                logging.debug("Too much try on {} : Nb try = {}".format(url, iscrape))
            logging.debug("Scrapping page {}".format(ipage))
            logging.debug("Waiting 5 seconds")
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            addresses = soup.find_all('span', attrs={'class': 'result-adress'})
            logging.debug("Nb span addresses found : {}".format(len(addresses)))

            descriptions = soup.find_all('div', attrs={'class': 'xl-desc'})
            descriptions.extend(soup.find_all('div', attrs={'class': 'l-desc'}))
            descriptions.extend(soup.find_all('div', attrs={'class': 'm-desc'}))
            logging.debug("Nb div xl-desc, l-desc, m-desc found (descriptions): {}".format(len(descriptions)))

            houses = soup.find_all('div', attrs={'class': 'result-xl-title-bar'})
            houses.extend(soup.find_all('div', attrs={'class': 'result-l-title-bar'}))
            houses.extend(soup.find_all('div', attrs={'class': 'result-m-title-bar'}))
            logging.debug(
                "Nb div result-xl-title-bar, result-l-title-bar, result-m-title-bar  (houses): {}".format(len(houses)))

            prices = []
            all_donnees_bien = soup.find_all('div', attrs={'class': 'xl-donnees-bien'})
            all_donnees_bien.extend(soup.find_all('div', attrs={'class': 'l-donnees-bien'}))
            all_donnees_bien.extend(soup.find_all('div', attrs={'class': 'm-donnees-bien'}))
            logging.debug(
                "Nb div xl-donnees-bien, l-donnees-bien, m-donnees-bien  (price): {}".format(len(all_donnees_bien)))
            for el in all_donnees_bien:
                price = el.find('div', attrs={'class': 'rangePrice'})
                if price is None:
                    prices.append("")
                else:
                    prices.append(price)

            surfaces = soup.find_all('div', attrs={'class': 'xl-surface-ch'})
            surfaces.extend(soup.find_all('div', attrs={'class': 'l-surface-ch'}))
            surfaces.extend(soup.find_all('div', attrs={'class': 'm-surface-ch'}))
            logging.debug(
                "Nb div xl-surface-ch, l-surface-ch, m-surface-ch (surfaces): {}".format(len(surfaces)))

            type_houses = soup.find_all('div', attrs={'class': 'title-bar-left'})
            logging.debug("Nb div title-bar-left (type_houses): {}".format(len(type_houses)))

            for house in houses:
                id_house = house.parent.parent.attrs['id']
                logging.debug("id_house = {}".format(id_house))

                dict_house[id_house] = {}

            for description in descriptions:
                if description.attrs['class'][0] == 'l-desc' or description.attrs['class'][0] == 'm-desc':
                    if description.parent['class'][0] == 'l-desc-wrapper':
                        id_house = description.parent.parent.parent.parent.parent.parent.parent.attrs['id']
                        dict_house[id_house]['description'] = description.get_text().replace("\t", "").replace("\n",
                                                                                                               "").strip()
                    else:
                        id_house = description.parent.parent.parent.parent.parent.parent.attrs['id']
                        dict_house[id_house]['description'] = description.get_text().replace("\t", "").replace("\n",
                                                                                                               "").strip()
                else:
                    id_house = description.parent.parent.parent.parent.parent.attrs['id']
                    dict_house[id_house]['description'] = description.get_text().replace("\t", "").replace("\n",
                                                                                                           "").strip()

            for surface in surfaces:
                if surface.attrs['class'][0] == 'l-surface-ch' or surface.attrs['class'][0] == 'm-surface-ch':
                    id_house = surface.parent.parent.parent.parent.parent.parent.attrs['id']
                    dict_house[id_house]['surface'] = surface.contents[0].replace("\t", "").replace("\n", "").strip()
                else:
                    id_house = surface.parent.parent.parent.parent.parent.attrs['id']
                    dict_house[id_house]['surface'] = surface.contents[0].replace("\t", "").replace("\n", "").strip()

            for i in range(len(addresses)):
                id_house = addresses[i].parent.parent.parent.parent.attrs['id']
                dict_house[id_house]['address'] = addresses[i].get_text().replace("\t", "").replace("\n", "").strip()
                id_house = type_houses[i].parent.parent.parent.attrs['id']
                dict_house[id_house]['type_house'] = type_houses[i].get_text().replace("\t", "").replace("\n",
                                                                                                         "").strip()

                if prices[i] is not None:
                    if type(prices[i]) is not str:
                        if prices[i].attrs['class'][0] == 'l-price' or prices[i].attrs['class'][0] == 'm-price' or \
                                prices[i].attrs['class'][0] == 'm-price-promotion' or prices[i].attrs['class'][
                            0] == 'l-price-promotion':
                            id_house = prices[i].parent.parent.parent.parent.parent.parent.attrs['id']
                            dict_house[id_house]['price'] = prices[i].contents[0].replace("\t", "").replace("\n",
                                                                                                            "").replace(
                                " ", "")
                        else:
                            id_house = prices[i].parent.parent.parent.parent.parent.attrs['id']
                            dict_house[id_house]['price'] = prices[i].contents[0].replace("\t", "").replace("\n",
                                                                                                            "").replace(
                                " ", "")
                        old_price = prices[i].find('span', {'class': 'old-price'})
                        if old_price is not None:
                            dict_house[id_house]['old_price'] = old_price.get_text().replace("\t", "").replace("\n",
                                                                                                               "").replace(
                                " ", "")
                        else:
                            dict_house[id_house]['old_price'] = ""

                link = houses[i].parent
                id_house = houses[i].parent.parent.attrs['id']
                if link.name == 'a':
                    dict_house[id_house]['link'] = link.attrs['href']

                dict_house[id_house]['url_image'] = ""

    except TimeoutException as e:
        logging.critical("Exception : {}".format(e.msg))
    finally:
        driver.quit()

    now = datetime.datetime.now()
    annonces_root_path = config['annonces_root_path']
    annonce_file_name_working = 'annonces-' + now.strftime("%Y-%m-%d_%H%M") + '.csv.working'

    with open(annonces_root_path + annonce_file_name_working, mode='w', newline='', encoding="UTF-8") as annonce_file:
        employee_writer = csv.writer(annonce_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for id_house, values in dict_house.items():
            employee_writer.writerow(
                [values['address'], values['type_house'],
                 values['price'], values['surface'],
                 values['description'], values['link'], id_house, values['url_image'],
                 values['old_price']])

    annonce_file_name = annonce_file_name_working.replace('.working', '')
    shutil.move(annonces_root_path + annonce_file_name_working, annonces_root_path + annonce_file_name)
    logging.debug("File {} has been created".format(str(annonces_root_path) + str(annonce_file_name)))
    logging.debug("End of scrapping")


if __name__ == "__main__":
    main()
