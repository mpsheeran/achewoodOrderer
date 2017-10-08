from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import json


def main():
    config = load_config('config.json')

    blogger_api_key = config['blogger_api_key']

    post_urls = []
    post_urls.extend(get_all_achewoods())

    for blog_url in config['blogger_urls']:
        post_urls.extend(get_all_blogger_posts_from_url(blog_url, blogger_api_key))

    sorted_url_list = [entry['url'] for entry in sorted(post_urls, key=lambda k: k['published'])]

    for url in sorted_url_list:
        print(url)


def get_response_dict_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()
    else:
        raise Exception("GET against {} failed with status code {} and text {}".format(
            url, response.status_code, response.text
        ))

    return response_json


def get_iso_datetime_from_achewood_url(url):
    date = str(url).split('=')[1]
    year = str(date)[4:9]
    day = str(date)[2:4]
    month = str(date)[0:2]
    return '{}-{}-{} 00:00:00'.format(year, month, day)


def load_config(config_file_path):
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    return config


def get_all_blogger_posts_from_url(blog_url, api_key):
    request_url = 'https://www.googleapis.com/blogger/v3/blogs/byurl?url={}&key={}&fields=id'.format(
        blog_url, api_key
    )
    response_dict = get_response_dict_from_url(request_url)

    blog_id = response_dict['id']

    # now that we have the blog id, we can start paging through the list of posts
    request_url = \
        'https://www.googleapis.com/blogger/v3/blogs/{}/posts?key={}&fields=nextPageToken,items(url,published)' \
        .format(blog_id, api_key)

    response_dict = get_response_dict_from_url(request_url)

    if response_dict['nextPageToken']:
        return paginated_blogger_recurse(request_url, response_dict['items'], response_dict['nextPageToken'])
    elif response_dict['items']:
        return response_dict['items']
    else:
        return None


def get_all_achewoods():
    r = requests.get('http://achewood.com/list.php')
    if r.status_code == 200:
        html = r.text

    else:
        raise Exception(r.status_code)

    soup = BeautifulSoup(html, 'html.parser')
    achewood_posts = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and 'index.php?' in href:
            url = 'http://achewood.com/{}'.format(href)
            achewood_posts.append({'url': url, 'published': get_iso_datetime_from_achewood_url(url)})

    return achewood_posts


def paginated_blogger_recurse(url, response, next_page_token):

    if not next_page_token:
        return response

    else:
        request_url = '{}&pageToken={}'.format(url, next_page_token)

        current_response = get_response_dict_from_url(request_url)

        try:
            current_response['items'].extend(response)
        except KeyError:
            return response

        try:
            npt = current_response['nextPageToken']
        except KeyError:
            npt = None

        return paginated_blogger_recurse(url, current_response['items'], npt)

if __name__ == "__main__":
    main()
