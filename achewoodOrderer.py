from __future__ import print_function
from bs4 import BeautifulSoup
import requests
#import datetime
#import heapq
import re
import ast

# define list of sites to scan
achewood_url = 'http://achewood.com/list.php'
blogspot_urls = ['https://raysmuckles.blogspot.com',
                 'https://rbeef.blogspot.com',
                 'https://journeyintoreason.blogspot.com',
                 'https://orezscu.blogspot.com',
                 'https://philippesblog.blogspot.com',
                 'https://corneliusbear.blogspot.com',
                 'https://lyle151.blogspot.com',
                 'https://mollysanders.blogspot.com',
                 'https://peterhcropes.blogspot.com',
                 'https://charleysmuckles.blogspot.com',
                 'https://emerillg.blogspot.com'
                 ]

post_urls = []

blogspot_post_regex_pattern = re.compile('/\d{4}/\d{2}/.*\.html')
blogger_api_root='https://www.googleapis.com/blogger/v3/blogs/'
blogger_api_key = 'AIzaSyCdEy333-Z3gfJcA7qVLaMc_Kz-DVMwdZM'

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
        request_url = '{}byurl?url={}&key={}&fields=id'.format(
            blogger_api_root, blog_url, blogger_api_key
        )
        print(request_url)
        response_dict = get_response_dict_from_url(request_url)

        blog_id = response_dict['id']

        # now that we have the blog id, we can start paging through the list of posts

        request_url = \
            '{}{}/posts?key={}&fields=nextPageToken,items(url,published)'\
                .format(
                blogger_api_root, blog_id, blogger_api_key
        )
        response_dict = get_response_dict_from_url(request_url)

        if response_dict['nextPageToken']:
            print('entering recursion with page token: {}'.format(response_dict['nextPageToken']))
            full_response = paginated_recurse(request_url, response_dict)

        print(full_response)


    # build data structure to store urls to sort - we'll use a heap

    # extract publication date for each entry on each site
    # return urls in usable sorted order
def get_publish_date(url):
    return None

# assumes response['nextPageToken'] returns a valid page token
def paginated_recurse(url, response):

    request_url = '{}&PageToken={}'.format(url, response['nextPageToken'])
    print(request_url)

    current_response = get_response_dict_from_url(request_url)

    try:
        print(current_response['nextPageToken'])  # hacky
        current_response['items'] += response['items']

    except KeyError:
        return current_response

    paginated_recurse(url, current_response)


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