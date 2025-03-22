# esautil

Elastic Agent Management Utility
 - Manage and configure datastreams
 - Manage and copy agent policies
 - Manage and copy/create index templates

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
