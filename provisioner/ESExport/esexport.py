#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys

import elasticsearch


def parse_cmdline():
    parser = argparse.ArgumentParser(
        description='Exports indexes from ElasticSearch to a structure accepted by docker-elk provisioner'
    )

    parser.add_argument('--host', '-H',
                        action='store',
                        help='ElasticSearch node hostname',
                        type=str,
                        dest='host',
                        metavar='HOST',
                        default='localhost'
                        )
    parser.add_argument('--port', '-P',
                        action='store',
                        help='ElasticSearch node port',
                        type=int,
                        dest='port',
                        metavar='PORT',
                        default=9200
                        )
    parser.add_argument('--ssl', '-s',
                        action='store_true',
                        help='ElasticSearch SSL connection',
                        dest='ssl',
                        )
    parser.add_argument('--prefix', '-p',
                        action='store',
                        help='ElasticSearch URL prefix',
                        type=str,
                        dest='prefix',
                        metavar='URL',
                        default=''
                        )
    parser.add_argument('--output', '-o',
                        action='store',
                        help='Output path',
                        type=str,
                        dest='output',
                        metavar='DIRECTORY',
                        default='.'
                        )
    parser.add_argument('indices',
                        nargs='+',
                        metavar='INDEX',
                        type=str
                        )
    args = parser.parse_args()

    if os.path.isfile(args.output):
        raise ValueError('Output path is a file, cannot create parent directories')
    if not os.access(args.output, os.W_OK):
        raise ValueError('Non-writable output path')

    return args


def fetch_index(elastic: elasticsearch.Elasticsearch, index: str):
    doc_count = elastic.search(index=index, size=0)['hits']['total']
    print('------ Found {} documents'.format(doc_count))
    if doc_count >= 10000:
        raise OverflowError('Result window is probably too large ({} >= 10000) and scrolling api is not supported yet'
                            .format(doc_count))

    docs = elastic.search(index=index, size=doc_count)
    return docs['hits']['hits']


def sort_docs(docs):
    result = dict()
    for doc in docs:
        if '_source' in doc:
            if doc['_type'] not in result:
                print('------ Found new type: {}'.format(doc['_type']))
                result[doc['_type']] = list()
            result[doc['_type']].append(
                {
                    'id': doc['_id'],
                    'document': doc['_source']
                }
            )
    return result


def sanitize_path(path):
    dictionary = {
        '*': '_x_'
    }
    for replchar in dictionary.keys():
        path = path.replace(replchar, dictionary[replchar])
    return path


def yield_path_document(outdir, index, docs):
    for doctype in docs.keys():
        target_dir = os.path.join(outdir, sanitize_path(index), sanitize_path(doctype))
        os.makedirs(target_dir, exist_ok=True)
        print('------ Created directory structure up to {}'.format(target_dir))

        # Write structure to disk
        for docdict in docs[doctype]:
            target_file = os.path.join(target_dir, '{0}.json'.format(sanitize_path(docdict['id'])))
            if os.path.exists(target_file):
                raise FileExistsError('Target file path {} already exists'.format(target_file))
            yield target_file, docdict['document']


def write_document(target_file, document):
    print('------ Write {}'.format(target_file))
    with open(target_file, 'w') as fp:
        json.dump(document, fp, indent=1, sort_keys=True)


def main(args):
    print('--------------- ElasticSearch Export ---------------')
    print('-- Open connection')

    elastic = elasticsearch.Elasticsearch(
        [
            {
                'host': args.host,
                'port': args.port,
                'url_prefix': args.prefix,
                'use_ssl': args.ssl
            }
        ]
        )

    print('-- Connection established, fetching indices')

    for index in args.indices:
        print('---- Fetching index {}'.format(index))
        docs = fetch_index(elastic, index)
        print('---- Sort documents by type')
        docs = sort_docs(docs)
        print('---- Write documents to disk')
        for target, document in yield_path_document(args.output, index, docs):
            write_document(target, document)


if __name__ == '__main__':
    try:
        main(parse_cmdline())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print('************ ERROR: {} / {} ************'.format(type(e), e), file=sys.stdout)
        sys.exit(1)
