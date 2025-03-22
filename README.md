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
