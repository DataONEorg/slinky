# How DataOne Concepts Map to Knowledge Graph Concepts and Patterns

The DataOne Linked Open Data graph (D1LOD) is essentially a translation of DataOne's holdings into [RDF](http://www.w3.org/RDF/) using a variety of standard vocabularies, including [schema.org](http://schema.org) as described in [Science on schema.org](https://science-on-schema.org), OBOE, ENVO, ECSO, and other vocuabularies. i.e., there is no DataONE ontology. Originally it was mapped against the [GeoLink Ontology](http://schema.geolink.org/), but this document has moved away from using GeoLink as the base.

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

| DataONE Concept  | Type     | OWL Class                                                     |
| ---------------- | -------- | ------------------------------------------------------------- |
| Object: Metadata | `1:1`    | `schema:Dataset`                                              |
| Object: Data     | `1:1`    | `schema:DataDownload`                                         |
| Object: Portal   | n/a      | Not mapped                                                    |
| System Metadata  | n/a      | Mapped directly to `schema:Dataset` or `schema:DataDownload`  |
| Package          | n/a      | Mapped directly to `schema:Dataset` via `schema:distribution` |
| Accounts         | `1:many` | `schema:Person` or `schema:Organization`                      |

Packages won't be directly mapped to a first-class type but the triples contained within them will be reflected using the following linkages:

| DataONE            | RDF                                                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `ore:aggregates`   | `schema:Dataset` <-> `schema:distribution` <-> `schema:DataDownload`                                                       |
| Provenance         | Following [SOSO](https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/Dataset.md#provenance-relationships). |
| `prov:hasLocation` | TBD. Maybe just as `prov:hasLocation`                                                                                      |
| Other triples      | Not mapped                                                                                                                 |

### Dataset

Note: This list is possibly not comprehensive at this point.
Note: These are loose mappings because the mappings are not as simple as XPath expressions. Also because the XPath expressions for ISO metadata are a nightmare.

| Property              | Mapped From (these aren't all real XPaths for brevity)                                                                                                                                                               |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@id`                 | `https://dataone.org/datasets/${PID}`                                                                                                                                                                                |
| `@type`               | `schema:Dataset`                                                                                                                                                                                                     |
| `identifier`          | System Metadata `identifier` (PID), `seriesId` (SID), EML `/eml/dataset/alternateIdentifier`                                                                                                                         |
| `isAccessibleForFree` | System Metadata `accessPolicy`                                                                                                                                                                                       |
| `url`                 | `https://dataone.org/datasets/${PID}`                                                                                                                                                                                |
| `name`                | EML: `/eml/dataset/title` <br> ISO: `//gmd:citation/gmd:title`<br>FGDC:`//idinfo/citation/citeinfo/title/` <br> Dryad: `//dcterms:title`                                                                             |
| `description`         | EML: `/eml/dataset/abstract` <br> ISO: `//gmd:identificationInfo/gmd:abstract` <br>FGDC: `//idinfo/descript/abstract` <br> Dryad: `//dcterms:description`                                                            |
| `datePublished`       | EML: `/eml/dataset/pubDate` <br> ISO: `//gmd:identificationInfo/gmd:citation/gmd:date` <br>FGDC: `//idinfo/citation/citeinfo/pubdate` <br> Dryad: n/a                                                                |
| `dateModified`        | System Metadata `dateSysMetadataUpdated`                                                                                                                                                                             |
| `keywords`            | EML: `/eml/dataset/keywordSet/keyword` <br> ISO: `//gmd:identificationInfo/gmd:descriptiveKeywords/` <br>FGDC: `//idinfo/keywords/theme/themekey`, `/idinfo/keywords/place/placekey` <br> Dryad: `//dcterms:subject` |
| `creator`             | EML: `/eml/dataset/creator` <br> ISO: `/gmd:identificationInfo/gmd:citation/gmd:CI_ResponsibleParty/` <br>FGDC: `//idinfo/citation/citeinfo/origin` <br> Dryad: `//dcterms:creator`                                  |
| `version`             | System Metadata `identifier`                                                                                                                                                                                         |
| `license`             | EML: `/eml/dataset/{licensed,intellectualRights}` <br> ISO: `//gmd:metadataConstraints/gmd:useConstraints/` <br>FGDC: n/a <br> Dryad `//dcterms:license`                                                             |
| `temporalCoverage`    | EML: `/eml/dataset/coverage/temporalCoverage` <br> ISO: `//gmd:identificationInfo/gmd:extent` <br>FGDC: `//idinfo/timeperd/timeinfo` <br> Drayd: n/a                                                                 |
| `spatialCoverage`     | EML: `/eml/dataset/coverage/spatialCoverage` <br> ISO: `//gmd:identificationInfo/gmd:extent` <br>FGDC: `//idinfo/spdom/bounding` <br> Drayd: n/a                                                                     |
| `publisher`           | EML: `/eml/dataset/publisher` <br> ISO: TBD <br>FGDC: n/a? <br> Drayd: `//dcterms:publisher` <br> Falls back to System Metadata `originMemberNode` otherwise                                                         |
| `distribution`        | Resource Map `ore:aggregates`                                                                                                                                                                                        |
| `variableMeasured`    | EML: `/eml/dataset/{entity}/attribute` <br> ISO: TODO <br>FGDC: `//attr` <br> Dryad n/a                                                                                                                              |
| `MonetaryGrant`       | EML: `/eml/dataset/project/{funding,award}/` <br> ISO: n/a <br>FGDC: n/a? <br> Dryad n/a                                                                                                                             |
| `prov:wasRevisionOf`  | System Metadata `obsoletes`                                                                                                                                                                                          |
| `schemaVersion`       | System Metadata `formatId`                                                                                                                                                                                           |
| `size`                | System Metadata `size` (summed over all members)                                                                                                                                                                     |
| `sameAs`              | The DOI if the DataONE identifier is a DOI                                                                                                                                                                           |

Extra triples:

- EML `annotation` elements will go in as-is with the subject as `https://dataone.org/datasets/${PID}[#id]` (fragment URI depending on context)

## Parties

Parties in DataONE are referenced either in system metadata or science metadata and are referenced either explicitly in the metadata or referenced by identifier in the DataONE Accounts service.

Parties exist in the graph as top-level instances so that references to them can be resolved independently and re-used across `schema:Dataset` instances.
Because parties rarely have identifiers of their own in the metadata they're referenced in, we mint identifiers as needed.
When references to parties in the metadata have identifier metadata (i.e., ORCIDs), we use that instead of minting an identifier.
When references to parties _do not_ have an existing identifier but have enough information to reasonably uniquely identify them, we mint a content-based identifier based upon the uniquely identifying information.
For all other cases, we generate a UUIDv4 identifier.

The motivation to use content-based identifiers where possible is rather than UUIDv4-based identifiers is two-fold:

1. Create stable URIs for parties. Where random identifiers are used, the URI for a person may change if the graph is ever re-generated. This was a limitation of the original plan.
2. You don't have to query the graph to look for a URI for an existing user before inserting triples about thems

### Examples

- If the metadata provides an ORCID, the ORCID is the identifier we use instead of generating/minting one
- If the metadata provides a last name _and_ and email address, which is reasonably uniquely identifying, we generate a content-based identifier. e.g., with last name "Scientist" and email "Scientist@Example.com", we hash `scientist scientist@scientist.com` and generate the URI `hash://sha256/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Data Repositories

Data repositories in DataONE are listed in the [Node list](https://cn.dataone.org/cn/v2/node) and referenced in System Metadata (`authoritativeMemberNode`, etc).
DataONE nodes (CN/MN) will are mapped to schema:ResearchProject + schema:Service following [SOSO](https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/DataRepository.md).

## Alignments

A set of alignments is automatically provisioned in the graph to provide `owl:equivalentClass` and `owl:equivalentProperty` triples where appropriate.

- `schema:DataDownload owl:equivalentClass dcat:Distribution`
- `schema:distribution owl:equivalentProperty dcat:Distribution`
- `schema:Person owl:equivalentClass foaf:Person`
- `schema:Organization owl:equivalentClass foaf:Organization`

Note: We can push as little or as hard on this idea, really.
The above are just some mappings that looked easy to me.

## Example

TODO: Note, can we solve some problems with a content based ID for people/orgs? I think so

Examples yet to produce:

- Multiple identifiers (pid, sid, alternateIdentifier)
- DataONE identifiers
- A basic prov example (script uses data and generates output)
- EML w/ semantic annotations

### Full Dataset

The following triples would be added to the graph for [https://dataone.org/datasets/doi%3A10.5063%2FF1891459](https://dataone.org/datasets/doi%3A10.5063%2FF1891459):

```{ttl}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix schema: <http://schema.org/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix spdx: <http://spdx.org/rdf/terms#> .
@prefix d1datasets: <https://dataone.org/datasets/> .
@prefix d1people: <https://dataone.org/people/> .
@prefix d1orgs: <https://dataone.org/organizations/> .
@prefix d1nodes: <https://dataone.org/nodes/> .

d1datasets:doi%3A10.5063%2FF1891459
    a schema:Dataset ;
    schema:name "Sockeye salmon brood tables, northeastern Pacific, 1922-2016" ;
    schema:description "Brood tables, also called run reconstructions, utilize annual estimates of the total run (commercial catch plus escapement), ..." ; # Rest of abstract elided for space
    schema:url "https://dataone.org/datasets/doi%3A10.5063%2FF1891459", "https://search.dataone.org/view/doi%3A10.5063%2FF1891459" ;
    schema:identifier [
        a schema:PropertyValue ;
        schema:propertyID "https://registry.identifiers.org/registry/doi" ;
        schema:value "doi:10.5063/F1891459" ;
        schema:url "https://doi.org/10.5063/F1891459" ;
    ] ;
    schema:sameAs <https://doi.org/doi%3A10.5063%2FF1891459> ;
    schema:schemaVersion <https://eml.ecoinformatics.org/eml-2.2.0> ;
    prov:wasRevisionOf <https://doi.org/doi%3A10.5063%2FF987123> ;
    schema:isAccessibleForFree "true" ; # When sysmeta AccessPolicy has public-read
    schema:datePublished "2017-11-20" ;
    schema:dateModified "2017-11-20" ;
    schema:keywords "brood table", "featured", "ocean climate" ;
    schema:creator d1people:Furn%3Auuid%3A81895d19-f8e8-4934-9e96-ee85d12bad10,
        d1people:Furn%3Auuid%3A21dc4382-8b79-4c88-96e3-a733fafd8790,
        d1people:Furn%3Auuid%3A75c4a6a8-4957-4fc5-b740-29e132537e54,
        d1people:Furn%3Auuid%3Ac2bc78b6-486b-402c-acf4-c3d15ceecbe2,
        d1people:Furn%3Auuid%3Abefdc7be-598a-4800-b8b4-283c204d22d5 ;
    schema:temporalCoverage "1922/2016" ;
    schema:spatialCoverage [
        a schema:Place ;
        schema:geo [
            a schema:GeoCoordinates ;
            schema:latitude "49.12" ;
            schema:longitude "-123.06"
        ] ;
        schema:additionalProperty [
            a schema:PropertyValue ;
            schema:propertyID <http://www.wikidata.org/entity/Q4018860> ;
            schema:name "Well-Known Text (WKT) representation of geometry" ;
            schema:value "POINT (-123.06 49.12)"
        ],
        [
            a schema:PropertyValue ;
            schema:propertyID "http://www.wikidata.org/entity/Q161779" ;
            schema:name "Spatial Reference System" ;
            schema:value "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
        ] ;
    ] ;
    schema:publisher d1nodes:urn%3Anode%3AKNB ;
    schema:variableMeasured "Stock.ID", "Species", "Stock", "Ocean.Region" ;
    schema:byteSize "986123981623"^^xsd:decimal ; # Sum across package

    # Note: Both awards are (1) using the free-text schema:award property and (2)
    # smushed together because the metadata doesn't use the new EML structured
    # funding and because multiple EML projects should have been used but were
    # smushed together in this record. This isn't a perfect example of funding.
    schema:award "State of Alaska's Salmon and People (Gordon and Betty Moore Foundation Award 5124) Data Task Forces for Better Synthesis Studies (Gordon and Betty Moore Foundation Award 5451)" ;

    # Note: This metadata record doesn't link to a specific license so this
    # triple is absent but will be included when available
    # schema:license

    schema:distribution d1datasets:urn%3Auuid%3A2e1f4408-6cbc-4acd-97b2-a0635a316952,
        d1datasets:urn%3Auuid%3Ac1ef6abb-f0e1-49f6-9705-171bb765366d,
        d1datasets:urn%3Auuid%3A47fa131f-f5be-409d-b13b-8d9756a6239e,
        d1datasets:urn%3Auuid%3A178c61cc-6119-42c2-9387-5b0b602324d4,
        d1datasets:urn%3Auuid%3A8371e85b-b693-4f22-9454-714ee17056f7,
        d1datasets:urn%3Auuid%3A78cd5968-8707-4f96-95ea-3d56383cb1bb,
        d1datasets:urn%3Auuid%3A62731e0f-023c-4d93-b16c-1ce17c2d2a2e .

d1nodes:urn%3Anode%3AKNB
    a schema:Service, schema:ResearchProject ;
    schema:name "KNB Data Repository" ;
    schema:description "The Knowledge Network for Biocomplexity (KNB) is a national network intended to facilitate ecological and environmental research on biocomplexity." .

d1datasets:urn%3Auuid%3A2e1f4408-6cbc-4acd-97b2-a0635a316952
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A2e1f4408-6cbc-4acd-97b2-a0635a316952" ;
    schema:encodingFormat "application/R" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "a87eef65e120b0c4bbf640d7095afc6bda931031" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    spdx:schema:name "broodTableProcessing.Rmd" .

d1datasets:urn%3Auuid%3Ac1ef6abb-f0e1-49f6-9705-171bb765366d
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3Ac1ef6abb-f0e1-49f6-9705-171bb765366d" ;
    schema:encodingFormat "text/html" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum"dbfcffc75d3036ce302068e8e9bb544aec03cd08" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "broodTableProcessing.html" .

d1datasets:urn%3Auuid%3A47fa131f-f5be-409d-b13b-8d9756a6239e
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A47fa131f-f5be-409d-b13b-8d9756a6239e" ;
    schema:encodingFormat "text/csv" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "56092cdb6040e95fb48979adc1ed7bcdcd8af0a4" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "SourceInfo.csv" .

d1datasets:urn%3Auuid%3A178c61cc-6119-42c2-9387-5b0b602324d4
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A178c61cc-6119-42c2-9387-5b0b602324d4" ;
    schema:encodingFormat "text/csv" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "62e39364c79028d6071c94cfff146ac662e698b9" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "StockInfo.csv" .

d1datasets:urn%3Auuid%3A8371e85b-b693-4f22-9454-714ee17056f7
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A8371e85b-b693-4f22-9454-714ee17056f7" ;
    schema:encodingFormat "text/csv" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "5979ec24f82bfd0a08c9503fe1d6a0619c57fe33" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "raw_brood_table_2019_07_16.csv" .

d1datasets:urn%3Auuid%3A78cd5968-8707-4f96-95ea-3d56383cb1bb
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A78cd5968-8707-4f96-95ea-3d56383cb1bb" ;
    schema:encodingFormat "image/png" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "88526341ead34b737b4c1fcf07bbe17a3fb82412" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "temporal_coverage.png" .

d1datasets:urn%3Auuid%3A62731e0f-023c-4d93-b16c-1ce17c2d2a2e
    a schema:DataDownload ;
    schema:contentUrl "https://cn.dataone.org/cn/v2/resolve/urn%3Auuid%3A62731e0f-023c-4d93-b16c-1ce17c2d2a2e" ;
    schema:encodingFormat "image/png" ;
    schema:datePublished "2020-04-20" ;
    schema:byteSize "123456789"^^xsd:decimal ;
    spdx:Checksum "fe5648e21a068409c1bf10ceae29ee2aacf0fdf9" ;
    spdx:ChecksumAlgorithm spdx:checksumAlgorithm_sha1 ;
    schema:name "stocks_per_region.png" .

d1people:Furn%3Auuid%3A81895d19-f8e8-4934-9e96-ee85d12bad10
    a schema:Person ;
    schema:name "Rich Brenner" ;
    schema:affiliation d1orgs:urn%3Auuid%3Adf20c53b-9ece-4f05-a0c9-18364adcb46a ;
    schema:email "richard.brenner@alaska.gov" .

d1people:Furn%3Auuid%3A21dc4382-8b79-4c88-96e3-a733fafd8790
    a schema:Person ;
    schema:name "Greg Ruggerone" ;
    schema:email "gruggerone@nrccorp.com" .

d1people:Furn%3Auuid%3A75c4a6a8-4957-4fc5-b740-29e132537e54
    a schema:Person ;
    schema:name "Brendan Connors" ;
    schema:affliation d1orgs:urn%3Auuid%3A78c098f6-5333-4d35-8eb4-616b3111f87c ;
    schema:email "Brendan.Connors@dfo-mpo.gc.ca" .

d1people:Furn%3Auuid%3Ac2bc78b6-486b-402c-acf4-c3d15ceecbe2
    a schema:Person ;
    schema:name "Jeanette Clark" ;
    schema:identifier [
        a schema:PropertyValue ;
        schema:propertyID "https://orcid.org" ;
        schema:value "0000-0003-4703-1974" ;
        schema:url "https://orcid.org/0000-0003-4703-1974"
    ] ;
    schema:affiliation d1orgs:urn%3Auuid%3Aab515281-3e44-4ea1-ba7a-1749fe3849f8 ;
    schema:email "jclark@nceas.ucsb.edu" .

d1people:Furn%3Auuid%3Abefdc7be-598a-4800-b8b4-283c204d22d5
    a schema:Person ;
    schema:name "Stephanie Freund" ;
    schema:affiliation d1orgs:urn%3Auuid%3Aab515281-3e44-4ea1-ba7a-1749fe3849f8 .

d1orgs:urn%3Auuid%3Aab515281-3e44-4ea1-ba7a-1749fe3849f8
    a schema:Organization ;
    schema:name "National Center for Ecological Analysis and Synthesis" .

d1orgs:urn%3Auuid%3Adf20c53b-9ece-4f05-a0c9-18364adcb46a
    a schema:Organization ;
    schema:name "Alaska Department of FIsh & Game, Division of Commercial Fisheries" .

d1orgs:urn%3Auuid%3A78c098f6-5333-4d35-8eb4-616b3111f87c
    a schema:Organization ;
    schema:name "Fisheries and Oceans Canada" .
```
