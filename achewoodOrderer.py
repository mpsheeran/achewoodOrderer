from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import datetime
import heapq
import re
import ast

# define list of sites to scan
achewood_url = 'http://achewood.com/list.php'
blogspot_urls = ['raysmuckles.blogspot.com',
                 'rbeef.blogspot.com',
                 'journeyintoreason.blogspot.com',
                 'orezscu.blogspot.com',
                 'philippesblog.blogspot.com',
                 'corneliusbear.blogspot.com',
                 'lyle151.blogspot.com',
                 'mollysanders.blogspot.com',
                 'peterhcropes.blogspot.com',
                 'charleysmuckles.blogspot.com',
                 'emerillg.blogspot.com'
                 ]

post_urls = []

blogspot_post_regex_pattern = re.compile('/\d{4}/\d{2}/.*\.html')
blogger_api_key = 'AIzaSyCMrvRU7qnT1RqrfcAm65BbKxSrTQtrq8g'

def main():
    r = requests.get(achewood_url)
    if r.status_code == 200:
        html = r.text

    else:
        raise Exception(r.status_code)

    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            if 'index.php?' in href:
                post_urls.append('http://achewood.com/{}'.format(href))

    print("Added {} urls".format(len(post_urls)))

    for blog_url in blogspot_urls:
        response_dict = get_response_dict_from_url('https://www.googleapis.com/blogger/v3/blogs/byurl?url={}?key={}'.format(
            blog_url, blogger_api_key
        ))

        blog_id = response_dict['id']

        # now that we have the blog id, we can get the list of posts

        response_dict = get_response_dict_from_url('https://www.googleapis.com/blogger/v3/blogs/{}/posts?key={}'.format(
            blog_id, blogger_api_key
        ))
        for item in response_dict["items"]:
            print(item)  # we'll have to do some extra parsing here


"""
        r = requests.get("http://{}".format(blog_url))
        if r.status_code == 200:
            html = r.text
        else:
            raise Exception(r.status_code)

        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                match = blogspot_post_regex_pattern.search(href)
                if match:
                    post_urls.append(href)

        print("url list now {} entries long after scraping {}".format(len(post_urls), blog_url))
        print(post_urls)
"""




    # build data structure to store urls to sort - we'll use a heap

    # extract publication date for each entry on each site
    # return urls in usable sorted order
def get_publish_date(url):
    return None


def get_response_dict_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response_text = response.text
    else:
        raise Exception("GET failed with status code {} and text {}".format(response.status_code, response.text))

    response_dict = ast.literal_eval(response_text)
    return response_dict


if __name__ == "__main__":
    main()