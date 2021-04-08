# How DataOne Concepts Map to Knowledge Graph Concepts and Patterns

The DataOne Linked Open Data graph (D1LOD) is essentially a translation of DataOne's holdings into [RDF](http://www.w3.org/RDF/) using a variety of standard vocabularies, including [schema.org](https://schema.org) as described in [Science on schema.org](https://science-on-schema.org), OBOE, ENVO, ECSO, and other vocuabularies. i.e., there is no DataONE ontology. Originally it was mapped against the [GeoLink Ontology](http://schema.geolink.org/), but this document has moved away from using GeoLink as the base.

- **STATUS: Work in Progress**
  - This document is in a partial state of incomplete editing as we transition concepts from Geolink to other vocabularies. Changes should be made on the `feature_14_graph_pattern` branch, and will show up in the associated pull rerquest.

## Concepts

DataONE has a number of formal types that need to be mapped:

- **Objects**: Everything stored/federated in DataONE (metadata, data, etc) is an Object and has (1) a serialization on disk ("object bytes") and (2) corresponding System Metadata
- **System Metadata**: Every Object has corresponding System Metadata containing operational metadata about the Object such as its size, checksum, etc
- **Packages:** A virtual concept formed by the closure asserted by triples in an Object conforming to a variant of the OAI/ORE Resource Map data model. For every Package there is one Object describing the Package. An Object may be a member of zero, one, or many Packages
- **Accounts**: All Objects are related to Subjects in the DataONE Accounts system and Subjects can be an individual or a group. These relations are stored in the System Metadata for the Object. e.g., all Objects have a `submitter` which is a string identifying the client or person that created the Object. This is often not the same client or person that created the content in the Object. e.g., a scientist might have created a file but their data manager may have uploaded the Object
- **Nodes**: Coordinating Nodes and Member Nodes make up the federation. See Data Repositories.

At a higher level, the most important/interesting information we have in DataONE is information about:

1. "Datasets" & Data (methods, variables, measurements, space & time, funding/funders, etc)
2. Parties (People, Organizations) + their relationships to data/datasets
3. Data Repositories

The job of the mappings is to provide the link between the concepts across the two above lists.

## Datasets & Data

| DataONE Concept  | Type     | OWL Class                                                        |
| ---------------- | -------- | ---------------------------------------------------------------- |
| Object: Metadata | `1:1`    | `schema:Dataset`                                                 |
| Object: Data     | `1:1`    | `schema:DataDownload`                                            |
| Object: Portal   | n/a      | Not mapped                                                       |
| System Metadata  | n/a      | Mapped directly on to `schema:Dataset` or `schema:DataDownload`  |
| Package          | n/a      | Mapped directly on to `schema:Dataset` via `schema:distribution` |
| Accounts         | `1:many` | `schema:Person` or `schema:Organization`                         |

Packages won't be directly mapped to a first-class type but the triples contained within them will be reflected using the following linkages:

| DataONE            | RDF                                                                  |
| ------------------ | -------------------------------------------------------------------- |
| `ore:aggregates`   | `schema:Dataset` <-> `schema:distribution` <-> `schema:DataDownload` |
| Provenance         | TBD. See Notes.                                                      |
| `prov:hasLocation` | TBD. Maybe just as `prov:hasLocation`                                |
| Other triples      | Not mapped                                                           |

Notes:

- For mapping in provenance metadata, I think we want to do something simpler than ProvONE and more like what Carl Boettiger shows in [prov](https://github.com/cboettig/prov). ie, we care about derivation and usage but not really ports and all that detailed stuff

### Dataset

| Property              | Mapped From                                                                     |
| --------------------- | ------------------------------------------------------------------------------- |
| `@id`                 | `https://dataone.org/datasets/${PID}`                                           |
| `@type`               | `schema:Dataset`                                                                |
| `identifier`          | System Metadata `identifier` (PID)                                              |
| `isAccessibleForFree` | System Metadata `accessPolicy`                                                  |
| `url`                 | `https://dataone.org/datasets/${PID}`                                           |
| `name`                | EML: `/eml/dataset/title` <br> ISO: `//` <br>FGDC: `//`                         |
| `description`         | EML: `/eml/dataset/abstract` <br> ISO: `//` <br>FGDC: `//`                      |
| `datePublished`       | EML: `/eml/dataset/pubDate` <br> ISO: `//` <br>FGDC: `//`                       |
| `keywords`            | EML: `/eml/dataset/keywordSet/keyword` <br> ISO: `//` <br>FGDC: `//`            |
| `creator`             | EML: `/eml/dataset/creator` <br> ISO: `//` <br>FGDC: `//`                       |
| `version`             | System Metadata `identifier`                                                    |
| `license`             | EML: `/eml/dataset/{licensed,intellectualRights}` <br> ISO: `//` <br>FGDC: `//` |
| `temporalCoverage`    | EML: `/eml/dataset/coverage/temporalCoverage` <br> ISO: `//` <br>FGDC: `//`     |
| `spatialCoverage`     | EML: `/eml/dataset/coverage/spatialCoverage` <br> ISO: `//` <br>FGDC: `//`      |
| `publisher`           | EML: `/eml/dataset/publisher` <br> ISO: `//` <br>FGDC: `//`                     |
| `distribution`        | Resource Map `ore:aggregates`                                                   |
| `variableMeasured`    | EML: `/eml/dataset/{entity}/attribute` <br> ISO: `//` <br>FGDC: `//`            |
| `funder`              | EML: `//` <br> ISO: `//` <br>FGDC: `//`                                         |

Extra triples:

- EML `annotation` elements will go in as-is with the subject as `https://dataone.org/datasets/${PID}[#id]` (fragment URI depending on context)

## People

Parties in DataONE are referenced either in science metadata or in the Accounts service.

| Property | Mapped From                           |
| -------- | ------------------------------------- |
| `@id`    | `https://dataone.org/datasets/${PID}` |
| `@type`  | `schema:Dataset`                      |

## Data Repositories

Data repositories in DataONE are referenced in the Nodes list and in System Metadata (`authoritativeMemberNode`, etc).

| Property | Mapped From                           |
| -------- | ------------------------------------- |
| `@id`    | `https://dataone.org/datasets/${PID}` |
| `@type`  | `schema:Dataset`                      |

## Archive

Content below is old and will either be migrated or removed.

## `gl:Dataset`

DataOne has the concept of a [Data Package](https://releases.dataone.org/online/api-documentation-v1.2.0/design/DataPackage.html) which is a set of digital objects and is composed of a Science Metadata object, at least one Data object, all of which are described by a Resource Map (another type of object). All three elements of the Data Package are Objects.

`gl:Dataset`s have take on the PID of the Science Metadata object and have properties that are drawn from the Solr index which is mainly fields that were extracted from the Science Metadata object during ingestion of the Data Package. For `gl:Dataset`s with a Resource Map, the `gl:Dataset` then contains a set of `gl:DigitalObject`s, which may be either Science Metadata (e.g., EML, FGDC) or Science Data (e.g., CSV, XLS, etc.).

Notes:

- Each `gl:Dataset` enters the graph as a resource with a URI of the form `<http://dataone.org/dataset/{PID}`.

## `gl:DigitalObject`

Science Metadata objects and Data objects are both mapped onto `gl:DigitalObject`. Each `gl:Dataset` will thus have at least one `gl:DigitalObject` which is a Science Metadata object. In the case of a Science Metadata object that is part of a Resource Map (part of a Data Package), a `gl:DigitalObject` will be created for the one Science Metadata object and for each object in the Resource Map that is the object (in the RDF sense) of a [`ore:aggregates`](http://www.openarchives.org/ore/1.0/vocabulary#ore-aggregates) statement. The latter set of described objects is not limited to the Data objects described by the Science Metadata and thus a `gl:Dataset` may include objects without a related Science Metadata object. Note: The relationship used to link `gl:Dataset` resources to `gl:DigitalObject` resources is `gl:isPartOf`.

Notes:

- Resource maps are not in the graph.
- Each `gl:DigitalObject` enters the graph as a blank node.

## `gl:Identifier`

Data objects, Science Metadata objects, and Resource Maps all have [Persistent Identifiers](http://jenkins-1.dataone.org/jenkins/job/API%20Documentation%20-%20trunk/ws/api-documentation/build/html/design/PIDs.html) (PIDs) within DataOne. For the D1 LOD graph, only Science Metadata and Data Objects get `gl:Identifier`s.

Notes:

- Each `gl:Identifier` enters the graph as a blank node.

## Example

An example will solidify what I've said above. Here's what would be added to the graph store if we just added the dataset with the PID 'doi:10.6073/AA/knb-lter-arc.376.1':

```{ttl}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix d1landing: <https://search.dataone.org/#view/> .
@prefix pext: <http://proton.semanticweb.org/protonext#> .
@prefix psys: <http://proton.semanticweb.org/protonsys#> .
@prefix datacite: <http://purl.org/spar/datacite/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix d1org: <http://dataone.org/organization/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix geolink: <http://schema.geolink.org/base/main#> .
@prefix d1person: <http://dataone.org/person/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix d1node: <https://cn.dataone.org/cn/v1/node/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix d1dataset: <http://dataone.org/dataset/> .

<http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1>
    geolink:description "phosphorus, nitrate, ammonia, and particulate phosphorus for lake N1 in 1991." ;
    geolink:hasEndDate "1991-01-01T00:00:00Z" ;
    geolink:hasGeometryAsWktLiteral "POLYGON ((-149.75 68.8, -149.0433 68.8, -149.0433 68.5, -149.75, 68.5))" ;
    geolink:hasIdentifier [
        geolink:hasIdentifierScheme datacite:doi ;
        geolink:hasIdentifierValue "doi:10.6073/AA/knb-lter-arc.376.1" ;
        a geolink:Identifier ;
        rdfs:label "doi:10.6073/AA/knb-lter-arc.376.1"
    ] ;
    geolink:hasLandingPage <https://search.dataone.org/#view/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
    geolink:hasPart [
        geolink:dateUploaded "2005-07-27T23:00:00.000+00:00" ;
        geolink:hasAuthoritativeDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:hasByteLength "7093" ;
        geolink:hasChecksum "22bd46629eaf8d71e686f63395a12a56" ;
        geolink:hasChecksumAlgorithm "MD5" ;
        geolink:hasFormat <http://schema.geolink.org/dev/voc/dataone/format#002> ;
        geolink:hasIdentifier [
            geolink:hasIdentifierScheme datacite:doi ;
            geolink:hasIdentifierValue "doi:10.6073/AA/knb-lter-arc.376.1" ;
            a geolink:Identifier ;
            rdfs:label "doi:10.6073/AA/knb-lter-arc.376.1"
        ] ;
        geolink:hasOriginDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:hasReplicaDigitalRepository <https://cn.dataone.org/cn/v1/node/urn:node:CN>, <https://cn.dataone.org/cn/v1/node/urn:node:LTER> ;
        geolink:isPartOf <http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
        a geolink:DigitalObject
    ] ;
    geolink:hasStartDate "1991-01-01T00:00:00Z" ;
    a geolink:Dataset ;
    rdfs:label "91n1nuts.txt" .

<http://dataone.org/person/urn:uuid:78d79a39-3aef-4bad-a011-e3fd2c5466f5>
    geolink:isCreatorOf <http://dataone.org/dataset/doi%3A10.6073%2FAA%2Fknb-lter-arc.376.1> ;
    geolink:nameFamily "Miller" ;
    geolink:nameFull "Mike Miller" ;
    geolink:nameGiven "Mike" ;
    a geolink:Person .
```
