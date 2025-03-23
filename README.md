# esautil

Elastic Agent Management Utility
 - Manage and configure datastreams
 - Manage and copy agent policies
 - Manage and copy/create index templates

## you need to know

### elastic agent
elastic agent is elastic's replacement for metricbeat and filebeat. it can be installed standalone, or as a "fleet" member, and configured wholly through fleet managment in kibana. elastic agent policies are composed of "integrations", such as "zookeeper", "hadoop", "system", etc. and can include logs or metrics

### datastreams
**datastreams** are elastic agent's method of storing information in elastic. a **datastream** is esentially an alias name for a group of indices. for the most part, you do not have control over the naming of the datastream and the indices that back it

the format for a datastream name is: **\<type\>-\<dataset\>-\<namespace\>**

**type** is either "logs" or "metrics"
**dataset** is the name of the data set that the integration sends to elastic servers for indexing. examples are 'zookeeper.server' or 'system.syslog'
**namespace** is a user-configurable text string 

### namespaces
**namespaces** are configured in **agent policies** (and/or in **integrations** for that agent) this is a free-form text field that allows you to maintain any separation if you want, for example you could use a * *prod* * and * *nonprod* * **namespace** to keep your prod and nonprod data in separate indices. if you do not specify one, it will be * *default* *

### index templates
**index templates** control how the data for any given **datastream* (and its component indices) is treated, this includes lifecycle policies applied to indices, data mapping, aliases, etc. 
**index templates** have an index pattern that matches the name of the **datastream(s)** you want it to apply to. 

if you do not create a specific template, a generic system template with a wildcard pattern will be used

# some caveats for this cli utility
## index template names

since **namespaces** play a significant part of elastic agent, the script assumes that your **index** template names include **'-\<namespace\>'** at the end of the name of the template. not following this convention will give unexpected results with some commands and is advised against.


## install
### python virtualenv
```
python -m venv ~/esautil 
source ~/esautil/bin/activate
pip -r requirements.txt
```

### setenvs.sh
use this to set your API key as an environment variable. esautil will use this key to connect.

```
tee setenvs.sh <<EOF
export ELASTIC_API_KEY="<your elastic apikey>"
EOF

. ./setenvs.sh
```
## options

```
esautil task <list|details|cancel|watch> [task_id] [-w <seconds>]


esautil index <details|create|rmalias|reindex|update> [index] 
        [-a <alias>] 
        [-l <lifecycle-policy>] 
        [-w <seconds>]

esautil template <list|json|init|details|update|createfromgeneric|copy> <namespace|template> [dest template]
        [-p <indexpattern1,indexpattern2,...>]
        [-o <priority>]
        [-c <add|rm> <component>]
        [-l <lifecycle-policy>]
        [-d <retention-days>]
        [-n <namespace>]
        [-r <rollover-alias>]

esautil agent <list|details|copy|json> <namespace|policy> [dest policy] [namespace]

esautil ds <list|details|applyilm|rmindex|addindex> <namespace|datastream> [namespace|datastream] [index]
        [-l] (show lifecycle)
        
esautil ilm <list|details|json> [policy]

esautil lc <details|move> [index] [phase]

```



## elastic API key privileges
```
{
  "esautil-api-privileges": {
    "cluster": [
      "manage_ilm",
      "write_fleet_secrets",
      "manage_index_templates",
      "manage_pipeline",
      "manage_logstash_pipelines",
      "manage_ingest_pipelines",
      "manage_data_stream_global_retention",
      "cancel_task",
      "monitor"
    ],
    "indices": [
      {
        "names": [
          ".ds-*",
          "logs*",
          "metrics*",
          "traces*"
        ],
        "privileges": [
          "manage",
          "manage_ilm",
          "manage_data_stream_lifecycle"
        ],
        "field_security": {
          "grant": [
            "*"
          ],
          "except": [
            ".ds-merged-*",
            "partial*"
          ]
        },
        "allow_restricted_indices": true
      },
      {
        "names": [
          ".ds-merged-*",
          "partial*"
        ],
        "privileges": [
          "write",
          "read",
          "manage",
          "manage_ilm",
          "manage_data_stream_lifecycle"
        ],
        "field_security": {
          "grant": [
            "*"
          ],
          "except": []
        },
        "allow_restricted_indices": true
      }
    ],
    "applications": [
      {
        "application": "kibana-.kibana",
        "privileges": [
          "feature_fleetv2.all",
          "feature_fleet.all"
        ],
        "resources": [
          "*"
        ]
      }
    ],
    "run_as": [],
    "metadata": {},
    "transient_metadata": {
      "enabled": true
    }
  }
}
```
