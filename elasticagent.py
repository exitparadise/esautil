#!/usr/bin/env python
#
# https://github.com/exitparadise/esautil.git
# code@mailshaft.com
# 

import json, re, requests, sys
from datetime import datetime
requests.packages.urllib3.disable_warnings()

class apiClient:
    def __init__(self,key,elastic_host,kibana_host,ssl_verify):
        self.apiKey = key
        self.elasticHost = elastic_host
        self.kibanaHost = kibana_host
        self.sslVerify = ssl_verify

    def _request(self,type,method,url,payload=None):
        _headers = {
            'kbn-xsrf': 'reporting',
            'Content-Type': 'application/json',
            'Authorization': f'ApiKey {self.apiKey}',
            'Elastic-Api-Version': '2023-10-31'
        }
        if method == 'GET':
            response = requests.get(url, headers=_headers, verify=self.sslVerify)
        elif method == 'POST':
            response = requests.post(url, headers=_headers, json=payload, verify=self.sslVerify)
        elif method == 'PUT':
            response = requests.put(url, headers=_headers, json=payload, verify=self.sslVerify)
        else:
           sys.exit(f"method {method} not recognized")
        if type == 'data': 
            if response.status_code == 200:
                content = response.json()
                return content
            else:
                e = response.json()
                try:
                    print(f"ERROR: {e['error']['reason']}")
                except:
                    print(f"ERROR: {e['message']}")
                sys.exit()

        elif type == 'exists':
            if response.status_code == 200:
                return True
            else:
                return False
    
    def elasticRequest(self,method,loc,payload=None):
        _url = f'https://{self.elasticHost}/{loc}'
        return self._request('data',method,_url,payload)

    def elasticExists(self,type,item):
        if type == 'template':
            _url = f'https://{self.elasticHost}/_index_template/{item}'
            return self._request('exists','GET',_url)
        elif type == 'component':
            _url = f'https://{self.elasticHost}/_component_template/{item}'
            return self._request('exists','GET',_url)

    def kibanaRequest(self,method,loc,payload=None):
        _url = f'https://{self.kibanaHost}/{loc}'
        return self._request('data',method,_url,payload)

class ilmDetails:
    def __init__(self,data):
        self.details = data
    
    def print_details(self,w):
        m = datetime.now() - datetime.fromtimestamp(self.details['phase_time_millis']/1000)
        print(f"    {self.details['index']}", end='')
        print(f" ilm:{self.details['policy']}", end='')
        print(f" phase:{self.details['phase']}", end='')
        print(f" created:{self.details['time_since_index_creation']}", end='')
        print(f" rolledover:{self.details['age']}", end='')
        print(f" in_phase:{str(round(m.total_seconds() / 86400,2)) + 'd'} {w}")

class indexTemplate():
    def __init__(self,data):
        try:
            self.template = data['index_templates'][0]['index_template']
            self.name = data['index_templates'][0]['name']
        except KeyError:
            self.template = data['index_template']
            self.name = data['name']

    def __str__(self):
        return(json.dumps(self.template,indent=1))

    def print_json(self):
        print(self.name)
        print(json.dumps(self.template,indent=1))

    def print_details(self):
       try:
         print(f"  - priority: {self.template['priority']}")
       except:
         print(f"  - priority: 0")
       try:
         print(f"  - ilm_policy: {self.template['template']['settings']['index']['lifecycle']['name']}")
       except KeyError:
         print(f"  - ilm_policy: None")

       try:
         print(f"  - lifecycle_data_retention: {self.template['template']['lifecycle']['data_retention']}")
       except KeyError:
         print(f"  - lifecycle_data_retention: None")

       print("  - patterns:")
       for pat in self.template['index_patterns']:
         print(f"    {pat}")
       print("  - components:")
       for comp in self.template['composed_of']:
         print(f"    {comp}")

    def get_patterns(self):
        return self.template['index_patterns']

    def update_name(self,name):
        self.name = name
        return 1

    def update_ilm_policy(self,p):
        count = 0
        if p == None:
            try:
                del self.template['template']['settings']['index']['lifecycle']
                count += 1
            except KeyError:
                pass
        else:
            dict_append(self.template)['template']['settings']['index']['lifecycle']['name'] = p
            count += 1
        return count

    def update_ralias(self,ra):
        dict_append(self.template)['template']['settings']['index']['lifecycle']['rollover_alias'] = ra
        return 1

    def update_retention(self,r):
        count = 0
        if r == 0:
            dict_append(self.template)['template']['lifecycle']['enabled'] = False
            dict_append(self.template)['template']['lifecycle']['data_retention'] = None
            count += 1
        elif r:
            dict_append(self.template)['template']['lifecycle']['enabled'] = True
            dict_append(self.template)['template']['lifecycle']['data_retention'] = f"{r}d"
            count += 1
        return count
  
    def update_component(self,a,c):
        count = 0
        if c[0] in ('a','add'):
            if c[1] in self.template['composed_of']:
                print(f"component template: {c[1]} is already in index template: {self.name}")
            else: 
                if a.elasticExists('component',c[1]):
                    self.template['composed_of'].append(c[1])
                    count += 1
                else:
                    sys.exit(f"component: {c[1]} does not exist")
        elif c[0] in ('r','rm','remove'):
            if c[1] in self.template['composed_of']:
                self.template['composed_of'].remove(c[1])
                count += 1
            else: 
                print(f"component template: {c[1]} is not in index template: {self.name}")
        else:
           sys.exit(f"unrecognized subcommand: {c[0]}") 
        return count

    def update_patterns(self,p):
        if type(p) is list:
            self.template['index_patterns'] = p
            return 1
        else: 
            print("not a list, skipping")
            return 0
        
    def update_prio(self,p):
        if type(p) is list:
            self.template['priority'] = p[0]
        else:
            self.template['priority'] = p
        return 1
   
    def unmanage(self,m):
        if m != "":
            dict_append(self.template)['_meta']['managed_by'] = m
            dict_append(self.template)['_meta']['managed'] = False
            return 1
        else:
            return 0

class agentPolicy():
    def __init__(self, name, data={}):
        self.name = name
        self.packages = []
        if not data:
            try:
                for p in data['package_policies']:
                    self.packages.append(p)

                del data['package_policies']
            except KeyError:
                pass

            self.policy = data

    def get(self,a):
        pid = a.kibanaRequest('GET',f"api/fleet/agent_policies?kuery=ingest-agent-policies.name:{self.name}")
        try:
            policy = a.kibanaRequest('GET',f"api/fleet/agent_policies/{pid['items'][0]['id']}")
        except:
            sys.exit(f"no such policy {self.name}")
        try:
            for p in policy['item']['package_policies']:
                self.packages.append(p)
            del policy['item']['package_policies']
        except KeyError:
            pass
        self.policy = policy['item']

    def commit_new_policy(self,a):
        resp = a.kibanaRequest('POST',f"api/fleet/agent_policies",self.policy)
        self.policy = resp['item']

    def commit_existing_policy(self,a):
        for d in ('version','revision','updated_at','updated_by','agents','unprivileged_agents',
                  'status','is_managed','is_protected','schema_version','inactivity_timeout'):
            del self.policy[d]
        resp = a.kibanaRequest('PUT',f"api/fleet/agent_policies/{self.policy['id']}",self.policy)
        self.policy = resp['item']
    
    def delete_packages(self):
        self.packages = []

    def add_package(self,a,package,num):
        package['policy_id'] = self.policy['id']
        if num > 1:
            package['name'] = self.policy['name'] + "-" + package['package']['name'] + str(num)
        else: 
            package['name'] = self.policy['name'] + "-" + package['package']['name']

        p = a.kibanaRequest('POST',f"api/fleet/package_policies",package)
        self.packages.append(p['item'])
        return (p['item'])

    def update_copy_policy(self,newname,newspace='default'):
        self.name = newname
        for d in ('id','version','revision','updated_at','updated_by','agents',
                  'unprivileged_agents','status','is_managed','is_protected','schema_version','inactivity_timeout'):
            del self.policy[d]
        self.policy['name'] = newname
        self.policy['namespace'] = newspace

    def update(self,n,v):
        self.policy[n] = v

    def print_json(self):
        print(self.name)
        print("policy:")
        print(json.dumps(self.policy,indent=1))
        print("integrations:")
        print(json.dumps(self.packages,indent=1))

    def print_details(self):
        print(f"{self.policy['name']}:")
        print(f"  - namespace: {self.policy['namespace']}")
        print("  - integrations:")
        for pkg in self.packages:
            print(f"    - {pkg['name']}: {pkg['package']['name']}/{pkg['package']['title']}")

class dict_append:
    def __init__(self, target):
        self.target = target
    def __getitem__(self, key):
        return dict_append(self.target.setdefault(key, {}))
    def __setitem__(self, key, value):
        self.target[key] = value
