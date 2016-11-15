# Cyber security use case for the ELK stack

This is a synchronized fork of [awesome-inc/docker-elk](https://github.com/awesome-inc/docker-elk).

This comprises Kibana UI and Graph Analysis (using [neo4j](https://neo4j.com/) and [apo](https://github.com/neo4j-contrib/neo4j-apoc-procedures)).

## Setup

1. Install [docker](http://docker.io).
2. Install [docker-compose](http://docs.docker.com/compose/install/).
3. Clone this repository recursively (i.e. including submodules)

## Usage

Start your stack using *docker-compose*:

    docker-compose up

Alternatively use [Vagrant](https://www.vagrantup.com/)

    vagrant up

And then access Kibana UI by hitting [http://localhost:5601](http://localhost:5601) with a web browser.
 
## Graph Analysis

In addition to the standard ELK stack we added a [neo4j](https://neo4j.com/) container including [apoc](https://github.com/neo4j-contrib/neo4j-apoc-procedures).
You can access the neo4j data browser on [http://localhost:7474/](http://localhost:7474/)

Custom actions on neo4j objects can be configured [HATEOAS style](https://en.wikipedia.org/wiki/HATEOAS) using the `decorator` which wraps the neo4j REST Api to provide custom data links. 
Browse the current configuration on [http://localhost:3000/api/ai/.config](http://localhost:3000/api/ai/.config).
