#!/usr/bin/python
# sudo apt install python-pip python-yaml
# pip install --upgrade pip
# pip install pyprind elasticsearch py2neo
# LOG_CFG=my_logging.yml python my_server.py
import os, sys
import getopt
import logging, logging.config
import yaml
import pyprind
from elasticsearch import Elasticsearch
from py2neo import Graph, Node, Relationship

# change to script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

index='logstash-*'
#doc_type='rss'
size=500
scroll='2m'
timeout=60
delete_all=False
quiet=False

query = """
WITH {hits} as hits
UNWIND hits as h

MERGE (e:Event {id:h._source.id} ) 
  ON CREATE SET 
    e.timestamp = h._source.`@timestamp`,
    e.ingest_time = h._source.ingest_time,
    e.title = h._source.title,
    e.content = h._source.summary

MERGE (post:Link {href:h._source.url, title:h._source.title, label:"View Post"})
MERGE (e)-[:LINKS_TO{type:"Post"}]->(post)

FOREACH (enclosureUrl IN (CASE WHEN h._source.enclosure_url <> "" THEN [h._source.enclosure_url] ELSE [] END) |
  MERGE (media:Link {href:enclosureUrl, title:enclosureUrl, label:"View Media"})
  MERGE (e)-[:LINKS_TO{type:"Media"}]->(media)
)

FOREACH (c IN h._source.categories | MERGE (category:Category {name:c}) MERGE (e)-[:TAGGED{type:"Keyword"}]->(category))

FOREACH (ent IN h._source.entities |
  FOREACH (loc in ent.locations | MERGE (location:Location {name:loc}) MERGE (e)-[:TAGGED{type:"Location"}]->(location) )
  FOREACH (dat in ent.dates | MERGE (thedate:Date {name:dat}) MERGE (e)-[:TAGGED{type:"Date"}]->(thedate) )
  FOREACH (nam in ent.names | MERGE (name:Name{name:nam}) MERGE (e)-[:TAGGED{type:"Name"}]->(name))
)
"""

def usage():
  print ('Usage: {0} -b [1000] -s [1m] -t [30] -d -q -h'.format(sys.argv[0]))

# cf.: http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
def setup_logging(
    default_path='logging.yml', 
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
      path = value
    if os.path.exists(path):
      with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
      logging.config.dictConfig(config)
    else:
      logging.basicConfig(level=default_level)

    # disable other loggers
    for l in ['neo4j.bolt', 'urllib3.connectionpool', 'httpstream', 'elasticsearch']:
      logging.getLogger(l).setLevel(logging.CRITICAL)
      
    # TODO: disable logging to console if quiet
    #if quiet is True:
    #  logging.getLogger().disabled = True

def setup_neo4j():
  g = Graph()
  if delete_all:
    logging.info('Deleting all Neo4j content...')
    g.delete_all()
  logging.debug('Verifying Neo4j schema...')
  g.run('CREATE CONSTRAINT ON (n:Event) ASSERT n.id IS UNIQUE')
  g.run('CREATE INDEX ON :Event(timestamp)')
  g.run('CREATE INDEX ON :Event(ingest_time)')
  return g

def import_neo4j(g, maxTime=''):
  body = '{"query":{"range":{ "ingest_time":{ "gt":"'+maxTime+'"}}}}' if maxTime else ''
  es = Elasticsearch(timeout=timeout)

  total = int(es.count(index=index, body=body)['count'])
  if total == 0:
    logging.info('No events newer than "{0}". Terminating.'.format(maxTime))
    
  logging.info('Scrolling {0} documents since "{1}" from Elasticsearch (bulk={2}, scroll={3})...'.format(total,maxTime,size,scroll))
  sid = ''
  maxTime=''
  n = int(max(total / size, 1))
  bar = pyprind.ProgBar(n, title='Import {0} documents'.format(total)) if quiet is False else None
  while True:
    rs = es.scroll(scroll_id=sid, scroll=scroll) if sid else es.search(index=index, scroll=scroll, size=size, body=body)
    sid = rs['_scroll_id']
    hits = rs['hits']['hits']
    if not hits:
      break
    g.run(query, hits=hits)
    pivot = max(map(lambda h: h['_source'].get('ingest_time', ''), hits))
    maxTime = max(maxTime, pivot)   
    if maxTime:
      writeMaxTime(maxTime)
    if bar:
      bar.update()
  if bar:
    logging.info(bar)

def parse_args():
  global size
  global scroll
  global delete_all
  try:
    opts, args = getopt.getopt(sys.argv[1:],'b:s:t:d:q:h', ['bulk=','scroll=','timeout=', 'delete_all','quiet', 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit(2)
    elif opt in ("-b", "--bulk"):
       size = int(arg)
    elif opt in ("-s", "--scroll"):
       scroll = arg
    elif opt in ("-t", "--timeout"):
       timeout = int(arg)
    elif opt in ("-d", "--delete_all"):
       delete_all = True
    elif opt in ("-q", "--quiet"):
       quiet = True

def parseMaxTime():
  maxTime=''
  if os.path.isfile('maxTime.stamp'):
    with open('maxTime.stamp', 'r') as f:
      maxTime=f.readline()
  return maxTime
  
def writeMaxTime(maxTime):
  logging.debug('max(@timestamp)=%s', maxTime)
  with open('maxTime.stamp', 'w') as f:
      f.write(maxTime)  

def main():
  parse_args()
  setup_logging()
  maxTime = parseMaxTime()
  g = setup_neo4j()
  import_neo4j(g, maxTime)

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    logging.exception("Uncaught exception: {0}".format(str(e)), exc_info=True)
    raise  
   