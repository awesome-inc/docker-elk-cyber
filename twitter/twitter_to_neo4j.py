#!/usr/bin/python
# sudo apt install python-pip python-yaml
# pip install --upgrade pip
# pip install tweepy py2neo retrying

# check tweepy api: 
# - http://docs.tweepy.org/en/v3.5.0/api.html
# - https://github.com/tweepy/tweepy/

# code adapted from
# - https://github.com/neo4j-contrib/twitter-neo4j/blob/master/docker/import_user.py

# API rate limits (most are 15x / 15min)
# - https://dev.twitter.com/rest/public/rate-limits

import os, sys
import getopt 
import logging, logging.config 
import yaml
import tweepy
from py2neo import Graph

import concurrent.futures
from retrying import retry
import time
from datetime import timedelta

# change to script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

screen_name = None
delete_all=False
keywords=[]

config = None
api = None
g = None

SLEEP_TIME = timedelta(minutes=1)

NEO4J_HOST = (os.environ.get('HOSTNAME', 'localhost'))
NEO4J_PORT = 7474
NEO4J_URL = "http://%s:%s/db/data/" % (NEO4J_HOST,NEO4J_PORT)

# Number of times to retry connecting to Neo4j upon failure
CONNECT_NEO4J_RETRIES = 15
CONNECT_NEO4J_WAIT_SECS = 2

# Number of times to retry executing Neo4j queries
EXEC_NEO4J_RETRIES = 2
EXEC_NEO4J_WAIT_SECS = 1

merge_users_query = """
UNWIND {users} AS u
WITH u
MERGE (user:User {screen_name:u.screen_name})
SET user.name = u.name,
    user.location = u.location,
    user.followers = u.followers_count,
    user.following = u.friends_count,
    user.statuses = u.statusus_count,
    user.url = u.url,
    user.profile_image_url = u.profile_image_url
MERGE (mainUser:User {screen_name:{screen_name}})
MERGE (user)-[:FOLLOWS]->(mainUser)
"""

merge_tweets_query = """
UNWIND {tweets} AS t
WITH t
ORDER BY t.id
WITH t,
     t.entities AS e,
     t.user AS u,
     t.retweeted_status AS retweet
MERGE (tweet:Tweet {id:t.id})
SET tweet.id_str = t.id_str, 
    tweet.text = t.text,
    tweet.created_at = t.created_at,
    tweet.favorites = t.favorite_count
MERGE (user:User {screen_name:u.screen_name})
SET user.name = u.name,
    user.location = u.location,
    user.followers = u.followers_count,
    user.following = u.friends_count,
    user.statuses = u.statusus_count,
    user.profile_image_url = u.profile_image_url
MERGE (user)-[:POSTS]->(tweet)
MERGE (source:Source {name:t.source})
MERGE (tweet)-[:USING]->(source)
FOREACH (h IN e.hashtags |
  MERGE (tag:Hashtag {name:LOWER(h.text)})
  MERGE (tag)<-[:TAGS]-(tweet)
)
FOREACH (u IN e.urls |
  MERGE (url:Link {url:u.expanded_url})
  MERGE (tweet)-[:CONTAINS]->(url)
)
FOREACH (m IN e.user_mentions |
  MERGE (mentioned:User {screen_name:m.screen_name})
  ON CREATE SET mentioned.name = m.name
  MERGE (tweet)-[:MENTIONS]->(mentioned)
)
FOREACH (r IN [r IN [t.in_reply_to_status_id] WHERE r IS NOT NULL] |
  MERGE (reply_tweet:Tweet {id:r})
  MERGE (tweet)-[:REPLY_TO]->(reply_tweet)
)
FOREACH (retweet_id IN [x IN [retweet.id] WHERE x IS NOT NULL] |
    MERGE (retweet_tweet:Tweet {id:retweet_id})
    MERGE (tweet)-[:RETWEETS]->(retweet_tweet)
)
"""

def usage():
  print ('Usage: {0} --name [twitter_name] --keyword [keyword] [--delete_all] [--help]'.format(sys.argv[0]))

def parse_args():
  global screen_name
  global keywords
  global delete_all
  try:
    opts, args = getopt.getopt(sys.argv[1:],'n:k:dh', ['name=', 'keyword=', 'delete_all', 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit(2)
    elif opt in ("-n", "--name"):
      screen_name = arg
    elif opt in ("-k", "--keyword"):
      keywords.append(arg)
    elif opt in ("-d", "--delete_all"):
       delete_all = True
  # check required
  if (not screen_name) and (not keywords):
    print ('At least one of "name" or "keywords" should be specified.')
    usage()
    sys.exit(2)
       
def load_config(default_path='twitter.private.yml', env_key='CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
      path = value
    if os.path.exists(path):
      with open(path, 'rt') as f:
        return yaml.safe_load(f.read())
    raise ValueError('Could not open configuration file "{0}"'.format(path))

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
    for l in ['tweepy.binder', 'neo4j.bolt', 'requests.packages.urllib3.connectionpool', 'httpstream']:
      logging.getLogger(l).setLevel(logging.ERROR)
 
def get_api():
  global api
  if api is None:
    logging.info('Connecting to Twitter ...')
    global config
    if config is None:
      config = load_config()
    auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['oauth_token'], config['oauth_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    logging.info('Connected to Twitter.')
  return api

@retry(stop_max_attempt_number=CONNECT_NEO4J_RETRIES, wait_fixed=(CONNECT_NEO4J_WAIT_SECS * 1000))
def get_graph():
  global g
  if g is None:
    logging.info('Connecting to Neo4j ...')
    g = Graph(NEO4J_URL)
    g.run('match (t:Tweet) return COUNT(t)')
    logging.info('Connected to Neo4j.')
  return g
  
@retry(stop_max_attempt_number=EXEC_NEO4J_RETRIES, wait_fixed=(EXEC_NEO4J_WAIT_SECS * 1000))
def execute_query(query, **kwargs):
  graph = get_graph()
  graph.run(query, **kwargs)
  
def setup_neo4j():
  g = get_graph()
  if delete_all:
    logging.info('Deleting all Neo4j content...')
    g.delete_all()
  logging.info('Verifying Neo4j schema...')
  # Add uniqueness constraints.
  g.run("CREATE CONSTRAINT ON (t:Tweet) ASSERT t.id IS UNIQUE;")
  g.run("CREATE CONSTRAINT ON (u:User) ASSERT u.screen_name IS UNIQUE;")
  g.run("CREATE CONSTRAINT ON (h:Hashtag) ASSERT h.name IS UNIQUE;")
  g.run("CREATE CONSTRAINT ON (l:Link) ASSERT l.url IS UNIQUE;")
  g.run("CREATE CONSTRAINT ON (s:Source) ASSERT s.name IS UNIQUE;")
  return g
  
def import_followers():
  global screen_name
  if not screen_name:
    return
  api = get_api()
  logging.info('Scrolling followers of "@{0}" ...'.format(screen_name))
  # 20 users per page, 15 api calls in 15 minutes --> 3 pages
  # newest followers are paged first
  for followers in tweepy.Cursor(api.followers, screen_name=screen_name).pages(3):
    users = list(map(lambda f:f._json, followers))
    execute_query(merge_users_query, users=users, screen_name=screen_name)
    logging.info('Imported {0} followers of "@{1}".'.format(len(users), screen_name)) 

def import_tweets():
  global screen_name
  if not screen_name:
    return
  api = get_api()
  logging.info('Scrolling tweets of "@{0}" ...'.format(screen_name)) 
  # 20 tweets per page, 15 api calls in 15 minutes --> 3 pages
  # newest tweets are paged first
  for statuses in tweepy.Cursor(api.user_timeline, screen_name=screen_name).pages(3):
    tweets = list(map(lambda s:s._json, statuses))
    execute_query(merge_tweets_query, tweets=tweets)
    logging.info('Imported {0} tweets for "screen_name={1}".'.format(len(tweets), screen_name)) 

def import_tweets_tagged():
  global screen_name
  if not screen_name:
    return
  api = get_api()
  logging.info('Traversing hashtags from "@{0}" tweets...'.format(screen_name)) 
  tagged_query = 'MATCH (h:Hashtag)<-[:TAGS]-(t:Tweet)<-[:POSTS]-(u:User {screen_name:{screen_name}}) WITH h, COUNT(h) AS Hashtags ORDER BY Hashtags DESC LIMIT 5 RETURN h.name AS tag_name, Hashtags'
  g = get_graph()
  res = g.run(tagged_query, screen_name=screen_name)
  #res.dump()
  if not res:
    logging.info('No hashtags found in graph.')
    return
  hashtags = list(map(lambda r:'#'+r['tag_name'], res))  
  logging.info('Found hashtags "{0}". Triggering search ...'.format(hashtags))
  import_tweets_search(hashtags)

def import_tweets_search(keywords):
  if not keywords:
    return
  api = get_api()
  search_term = ' OR '.join(keywords)
  logging.info('Searching for tweets "{0}" ...'.format(search_term)) 
  # 15 tweets per page, 15 api calls in 15 minutes --> 3 pages
  # newest tweets are paged first
  for statuses in tweepy.Cursor(api.search, q=search_term).pages(3):
    tweets = list(map(lambda s:s._json, statuses))
    execute_query(merge_tweets_query, tweets=tweets)
    logging.info('Imported {0} tweets for "q={1}".'.format(len(tweets), search_term))

    
def main():  
  parse_args()
  setup_logging()
  setup_neo4j()

  followers_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  tweets_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  
  exec_times = 0
  global keywords

  while True:
    tweets_executor.submit(import_tweets)
    tweets_executor.submit(import_tweets_search, keywords)

    if (exec_times % 3) == 0:
      followers_executor.submit(import_followers)
      tweets_executor.submit(import_tweets_tagged)

    logging.info('Sleeping "{0}" ...'.format(SLEEP_TIME))
    time.sleep(SLEEP_TIME.total_seconds())
    logging.info('Done sleeping - maybe import more')
    exec_times = exec_times + 1
        
if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    logging.exception("Uncaught exception: {0}".format(str(e)), exc_info=True)
    raise  
   