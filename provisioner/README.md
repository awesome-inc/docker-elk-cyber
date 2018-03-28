# provisioner

Import & export Elasticsearch data, e.g. Kibana dashboards & configuration

## Export

Export documents of an Elasticsearch index

```bash
docker-compose run provisioner ruby export.rb [index=.kibana] [output=export]
```

This fetches the `.kibana` index and downloads documents into `export`.

## Porivion (Import)

Upload documents from `import` to Elasticsearch (`ES_BASE_URI`)

```bash
docker-compose run provisioner ruby 01_provision.rb [input=import]
```
