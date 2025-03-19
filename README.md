# esautil

Elastic Agent Control Utility

Manipulate Index Templates, Data Streams, Agent Policies & ILM Policies


### setenvs.sh
script to set your secrets in env vars

```
tee setenvs.sh <<EOF
export ELASTIC_API_KEY="<your elastic api key>"
EOF

. setenvs.sh
```

### elastic api key permissions

API Permissions for Elastic Agent/Fleet Managment

```
{
  "fleet-mgmt-api": {
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
          "*"
        ],
        "privileges": [
          "manage",
          "manage_ilm",
          "manage_data_stream_lifecycle"
        ],
        "field_security": {
          "grant": [
            ".ds-*",
            "logs*",
            "metrics*",
            "traces*"
          ],
          "except": [
            ".ds-merged-*"
          ]
        },
        "allow_restricted_indices": true
      },
      {
        "names": [
          ".ds-merged-*",
          "partial-*"
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
