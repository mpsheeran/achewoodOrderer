from __future__ import print_function
from bs4 import BeautifulSoup
import requests
#import datetime
#import heapq
import re
import ast
from time import sleep

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
                url = 'http://achewood.com/{}'.format(href)
                post_urls.append({'url': url, 'published':get_iso_datetime_from_achewood_url(url)})

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
            # print('entering recursion with page token: {}'.format(response_dict['nextPageToken']))
            full_response = paginated_recurse(request_url, response_dict['items'], response_dict['nextPageToken'])

        post_urls.extend(full_response)
        print('Finished collecting posts from {}. Sleeping 10s'.format(blog_url))

    sorted_url_list = [entry['url'] for entry in sorted(post_urls, key=lambda k: k['published'])]

    print(sorted_url_list)


def paginated_recurse(url, response, nextPageToken):

    if not nextPageToken:
        return response

    else:
        request_url = '{}&pageToken={}'.format(url, nextPageToken)

        current_response = get_response_dict_from_url(request_url)

        try:
            current_response['items'].extend(response)
        except KeyError:
            return response

        try:
            npt = current_response['nextPageToken']
        except KeyError:
            npt = None

        return paginated_recurse(url, current_response['items'], npt)


def get_response_dict_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response_text = response.text
    else:
        raise Exception("GET failed with status code {} and text {}".format(response.status_code, response.text))

    response_dict = ast.literal_eval(response_text)
    return response_dict

def get_iso_datetime_from_achewood_url(url):
    date = str(url).split('=')[1]
    year = str(date)[4:9]
    day = str(date)[2:4]
    month = str(date)[0:2]
    return '{}-{}-{} 00:00:00'.format(year, month, day)

if __name__ == "__main__":
    main()