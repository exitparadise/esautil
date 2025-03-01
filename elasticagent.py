#!/usr/bin/env python
#
# https://github.com/exitparadise/esactl.git
# tim talpas github.festive812@passfwd.com
# 

class dict_append:
    def __init__(self, target):
        self.target = target
    def __getitem__(self, key):
        return dict_append(self.target.setdefault(key, {}))
    def __setitem__(self, key, value):
        self.target[key] = value

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
       print(f"  - priority: {self.template['priority']}")
       try:
         print(f"  - ilm_policy: {self.template['template']['settings']['index']['lifecycle']['name']}")
       except KeyError:
         print(f"  - ilm_policy: None")

       try:
         print(f"  - lifecycle_data_retention: {self.template['template']['lifecycle']['data_retention']}")
       except KeyError:
         print(f"  - lifecycle data retention: None")

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
  
    def update_component(self,c):
        count = 0
        if c[0] in ('a','add'):
            if c[1] in self.template['composed_of']:
                print(f"component template: {c[1]} is already in index template: {self.name}")
            else: 
                self.template['composed_of'].append(c[1])
                count += 1
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
        self.template['priority'] = p[0]
        return 1
   
    def unmanage(self,m):
        self.template['_meta']['managed_by'] = m
        self.template['_meta']['managed'] = False
        return 1


class agentPolicy():
    def __init__(self, name, data={}):
        self.name = name
        self.packages = []
        try:
            for p in data['package_policies']:
                self.packages.append(p)

            del data['package_policies']
        except KeyError:
            pass

        self.policy = data

    def add_policy(self,policy):
        print(json.dumps(policy,indent=1))
        resp = api_request('POST',KIBANA_HOST,f"api/fleet/agent_policies",policy)
        self.policy = resp['item']

    def add_package(self,package):
        print(json.dumps(package,indent=1))
        p = api_request('POST',KIBANA_HOST,f"api/fleet/package_policies",package)
        self.packages.append(p['item'])

    def copy_policy(self,newname,newspace='default'):
        self.name = newname
        for d in ('id','version','revision','updated_at','updated_by','agents',
                  'unprivileged_agents','status','is_managed','is_protected','schema_version','inactivity_timeout'):
            del self.policy[d]
        self.policy['name'] = newname
        self.policy['namespace'] = newspace

        return self.policy

    def copy_packages(self,newname,newspace='default'):
        for p in self.packages:
            new_name = re.sub("^[^-]+",newspace,p['name'])
            p['name'] = new_name
            for d in ('id','version','updated_at','updated_by','revision','created_at',
                      'created_by','policy_id','policy_ids'):
                 del p[d]
            new_inputs = []
            for i in p['inputs']:
                new_streams = []
                for s in i['streams']:
                    del s['id']
                    new_streams.append(s)
                del i['streams']
                i['streams'] = new_streams
                new_inputs.append(i)
            del p['inputs']
            p['inputs'] = new_inputs

        return self.packages

    def print_json(self):
        print(self.name)
        print(json.dumps(self.policy,indent=1))
        print(json.dumps(self.packages,indent=1))

    def print_summary(self):
        print(f"name: {self.policy['name']}")
        print(f"namespace: {self.policy['namespace']}")
        for pkg in self.packages:
            print(f" - {pkg['name']}")
