import sys
import getopt
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup

BASE_URL = 'https://www.olx.ua/list/q-'


def get_html(url=BASE_URL):
    req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = req.text
    return html


def link_generator(html):
    soup = BeautifulSoup(html, 'html.parser')
    cells = soup.find('table',
                      id='offers_table').find_all('td', class_='title-cell')
    for cell in cells:
        yield cell.find('a', class_='detailsLink')['href']


def crawl_controller(query):
    with Pool(4) as pool:
        for page in range(1, 3):
            try:
                html = get_html(f'{BASE_URL}{query}/?page={page}')
                pool.map(crawler, link_generator(html))
            except requests.exceptions.ConnectionError:
                print('OLX is unavailable')


def crawler(link):
    try:
        html = get_html(link)
    except requests.exceptions.ConnectionError:
        print('OLX is unavailable')
        return
    soup = BeautifulSoup(html, 'html.parser').find('div', id='offerdescription')
    title_box = soup.find('div', class_='offer-titlebox')
    title = title_box.h1.string.strip()
    id = title_box.find('div', class_='offer-titlebox__details'
                        ).em.small.string.strip()
    description = ''
    desc_gen = soup.find('div', id='textContent').strings
    for _ in range(10):
        try:
            description += next(desc_gen).string.strip()
        except StopIteration:
            break
    print(f'{title}\n{id}\n{description}\n\n')


def main(argv):
    query = ''
    try:
        opts, args = getopt.getopt(argv, "q:", ['query='])
        if not opts:
            raise getopt.GetoptError('crawler.py -query <search_query>')
    except getopt.GetoptError:
        print('crawler.py -q <search_query>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-q", "--query"):
            query = arg

    if not query:
        print('crawler.py -q <search_query>')
        sys.exit(1)

    crawl_controller(query)


if __name__ == "__main__":
    main(sys.argv[1:])
