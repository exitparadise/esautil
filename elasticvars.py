import os

global API_KEY, ELASTIC_HOST, KIBANA_HOST, SSL_VERIFY, SPACES

API_KEY=os.getenv('ELASTIC_API_KEY')
ELASTIC_HOST="elastic-api:9200"
KIBANA_HOST="kibana-api:5601"
SSL_VERIFY=False
SPACES = ('prod','devqa','default')
