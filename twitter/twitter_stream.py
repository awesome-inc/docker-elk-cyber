#!/usr/bin/python

# sudo apt install python-pip python-yaml
# pip install --upgrade pip
# pip install tweepy
# PYTHONENCODING=UTF-8
# chcp 65001
# CFG=my_twitter.yml 
# python twitter_stream.py 

# cf.: http://tweepy.readthedocs.io/en/v3.5.0/streaming_how_to.html?highlight=streaming
import sys, os, getopt, json, yaml
import logging, logging.config
import tweepy, socket

# change to script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

api = None
host = 'localhost'
port = 9563
keywords = []
toptrends = 0
output = 'stdout' #'tcp', ... 'elasticsearch', 'neo4j' (TODO)
woeid = 23424829 # Germany

def usage():
  print ('Usage: {0} [--output {3}] [--host {1}] [--port {2}] [--keyword keyword] [--trends max) [--woeid {4}]] --help'.format(sys.argv[0], host, port, output, woeid))
  
def parse_args():
  global output
  global host
  global port
  global keywords
  global toptrends
  global woeid
  try:
    opts, args = getopt.getopt(sys.argv[1:],'o:h:p:k:t:i', ['output=', 'host=','port=','keyword=', 'trends=','woeid=' 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ('--help'):
      usage()
      sys.exit(2)
    elif opt in ("-o", "--output"):
       output = arg
    elif opt in ("-h", "--host"):
       host = arg
    elif opt in ("-p", "--port"):
       port = int(arg)
    elif opt in ("-k", "--keyword"):
       keywords.append(arg)
    elif opt in ("-t", "--trends"):
       toptrends = int(arg)
    elif opt in ("-i", "--woeid"):
       woeid = int(arg)

def load_config(default_path='twitter.private.yml', env_key='CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
      path = value
    if os.path.exists(path):
      with open(path, 'rt') as f:
        return yaml.safe_load(f.read())
    raise ValueError('Could not open configuration file "{0}"'.format(path))

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
    
# override tweepy.StreamListener to add logic
class StdOutStreamListener(tweepy.StreamListener):

  #def on_data(self, data):
  #  print( json.dumps(data) )
  #  return True

  def on_status(self, status):
    logging.info('Tweet {0} at {1} from {2} ({3}): {4}'.format(status.id, status.created_at, status.user.screen_name, status.user.id, status.text))
    #logging.info(status._json)

  def on_error(self, status_code):
    if status_code == 420:
      #returning False in on_data disconnects the stream
      return False    
      
# override tweepy.StreamListener to add logic
class TcpStreamListener(tweepy.StreamListener):
  
  def __init__(self, api, host, port):
    super().__init__(api)
    
    # https://gist.github.com/jgoodall/6323951
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((host, port))
    logging.info ('Connected to "tcp://{0}:{1}."'.format(host, port))
    
  def __del__(self):
    self.sock.shutdown(socket.SHUT_WR)
    self.sock.close()
    logging.info('Closed.')
      
  #def on_data(self, raw_data):
  #  data = json.loads(raw_data)
  #  msg = { '@message' : data['text'], '@fields' : data }
  #  msg_dump = json.dumps(msg, ensure_ascii=False)
  #  self.socket.send(msg_dump.encode('utf-8'))
  #  return True

  def on_status(self, status):
    logging.info('Tweet {0} at {1} from {2} ({3}): {4}'.format(status.id, status.created_at, status.user.screen_name, status.user.id, status.text))
    status_json = { '@message' : status._json, '@timestamp':status.created_at.isoformat() }
    json_msg = json.dumps(status_json, ensure_ascii=False)
    msg = json_msg.encode('utf-8')
    self.mysend(msg)
    return True

  def on_error(self, status_code):
    if status_code == 420:
      #returning False in on_data disconnects the stream
      return False 

  def mysend(self, msg):
    msglen = len(msg)
    totalsent = 0
    while totalsent < msglen:
      sent = self.sock.send(msg[totalsent:])
      if sent == 0:
        raise RuntimeError("socket connection broken")
      totalsent = totalsent + sent      

def get_keywords(keywords, toptrends):
  if toptrends > 0:
    return get_toptrends(toptrends)
  
  if len(keywords) == 0:
    return ['*']
    
  return keywords

def get_toptrends(max):    
  # Twitter Trends API, cf.: https://dev.twitter.com/rest/public
  # Here, we use 'trends/place' which requires a woeid, cf.: http://woeid.rosselliot.co.nz
  trends = api.trends_place(woeid)
  all_trends = set([trend['name'] for trend in trends[0]['trends']])
  keywords = list(all_trends)[1:toptrends]
  logging.info ('Top {0} trends for (woeid={1}): {2}'.format(toptrends, woeid, keywords))
  return keywords

def main():
  parse_args()
  setup_logging()

  config = load_config()
  auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
  auth.set_access_token(config['oauth_token'], config['oauth_token_secret'])
  
  global api
  api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

  global keywords
  keywords = get_keywords(keywords, toptrends)
  
  listener = StdOutStreamListener() if output=='stdout' else TcpStreamListener(api, host, port)
  stream = tweepy.Stream(auth=api.auth, listener=listener)

  logging.info('Streaming twitter on {0}...'.format(keywords))
  stream.filter(track=keywords) # async=True, locations=[-6.38,49.87,1.77,55.81]

if __name__ == '__main__':
  main()
