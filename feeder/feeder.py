#!/usr/bin/python3
# -*- coding: utf-8 -*-

import feedparser
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import schedule
import time
import yaml


def render_template(data, template_name, filters=None):
    """Render data using a jinja2 template"""
    env = Environment(loader=FileSystemLoader(''))

    if filters is not None:
        for key, value in filters.iteritems():
            env.filters[key] = value

    template = env.get_template(template_name)
    return template.render(feed=data).encode('utf-8')


def load_feeds():
    with open("config.yml", 'r') as file:
        return yaml.load(file)['feeds']


def rss2json(url, name):
    feed = feedparser.parse(url)
    json = render_template(feed.entries, 'news.j2')
    file_name = f'{name}_{time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(file_name, 'wb') as output:
        output.write(json)


def main():
    for feed in load_feeds():
        interval = feed['interval']
        name = feed['name']
        url = feed['url']
        schedule.every(interval).seconds\
            .tag(name)\
            .do(rss2json, url, name)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
