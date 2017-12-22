# Schema.org serialization

The EarthCube Project 418 is working towards directly inserting JSON-LD
annoations following schema.org and related vocabularies into dataset landing
pages.  A Google sitemap provides an index to the data URIs to be crawled
by Google.  Here's an example of the JSON-LD that is being embedded by BCO-DMO:

```json
{
    "@context": {
        "@vocab": "http:\/\/schema.org\/",
        "datacite": "http:\/\/purl.org\/spar\/datacite\/",
        "earthcollab": "https:\/\/library.ucar.edu\/earthcollab\/schema#",
        "geolink": "http:\/\/schema.geolink.org\/1.0\/base\/main#",
        "vivo": "http:\/\/vivoweb.org\/ontology\/core#"
    },
    "@id": "https:\/\/www.bco-dmo.org\/dataset\/3300",
    "identifier": ["http:\/\/lod.bco-dmo.org\/id\/dataset\/3300", {
        "@type": "PropertyValue",
        "additionalType": ["geolink:Identifier", "datacite:Identifier"],
        "@id": "https:\/\/doi.org\/10.1575\/1912\/bco-dmo.665253",
        "propertyID": "datacite:doi",
        "value": "10.1575\/1912\/bco-dmo.665253",
        "url": "https:\/\/doi.org\/10.1575\/1912\/bco-dmo.665253"
    }],
    "url": "https:\/\/www.bco-dmo.org\/dataset\/3300",
    "@type": "Dataset",
    "name": "Larval krill studies - fluorescence and clearance from ARSV Laurence M. Gould LMG0106, LMG0205 in the Southern Ocean from 2001-2002 (SOGLOBEC project)",
    "additionalType": ["geolink:Dataset", "vivo:Dataset"],
    "alternateName": "larval krill pigments",
    "description": "\u0026lt;p\u0026gt;\u0026quot;Winter ecology of larval krill: quatifying their interaction with the pack ice habitat\u0026quot;\u0026lt;\/p\u0026gt;\r\n\r\n\u0026lt;p\u0026gt;The goal of the larval krill studies was to investigate the physiology and ecology of krill larvae associated with the pack ice and the microbial community on which they feed.\u0026lt;\/p\u0026gt;\r\n\r\n\u0026lt;p\u0026gt;During LMG0106 we occupied two 4-5 day ice stations (Robert and Billy) and sampled several other ice floes opportunistically. We conducted 10 instantaneous growth rate experiments, and 4 whole body clearance time experiments to determine gut passage time (decline in pigment content over time). We also sampled larvae at two additional sites for initial body pigment content (whole body fluorescence), and at 4 sites for condition factor. The under-ice algal community was sampled at one site. Length and stage frequency determinations were also determined.\u0026lt;\/p\u0026gt;\r\n\r\n\u0026lt;p\u0026gt;We occupied three time-series stations of approximately 1 week each, and in addition opportunistically sampled at times when other activities had priority. Our primary goal during the cruise was to occupy three ice camps or process stations with the intent of thoroughly studying the under-ice environment by SCUBA in conjunction with other projects working topside. \u0026lt;a href=\u0026quot;http:\/\/www.ccpo.odu.edu\/Research\/globec\/main_cruises02\/lmg0205\/report_lmg0205.pdf\u0026quot; target=\u0026quot;_blank\u0026quot;\u0026gt;\u0026lt;em\u0026gt;(from cruise report LMG0205)\u0026lt;\/em\u0026gt;\u0026lt;\/a\u0026gt;\u0026lt;\/p\u0026gt;",
    "datePublished": "2010-02-03",
    "keywords": "oceans",
    "creator": [{
        "@type": "Person",
        "additionalType": "geolink:Person",
        "@id": "https:\/\/www.bco-dmo.org\/person\/51160",
        "name": "Dr Robin Ross",
        "url": "https:\/\/www.bco-dmo.org\/person\/51160"
    }, {
        "@type": "Person",
        "additionalType": "geolink:Person",
        "@id": "https:\/\/www.bco-dmo.org\/person\/51159",
        "name": "Dr Langdon Quetin",
        "url": "https:\/\/www.bco-dmo.org\/person\/51159"
    }],
    "version": "2010-02-03",
    "citation": "Ross, Robin and Quetin, Langdon (2010) Larval krill studies - fluorescence and clearance from ARSV Laurence M. Gould LMG0106, LMG0205 in the Southern Ocean from 2001-2002 (SOGLOBEC project). Biological and Chemical Oceanography Data Management Office (BCO-DMO). Dataset version 2010-02-03 [if applicable, indicate subset used]. http:\/\/lod.bco-dmo.org\/id\/dataset\/3300 [access date]",
    "license": "http:\/\/creativecommons.org\/licenses\/by\/4.0\/",
    "publishingPrinciples": {
        "@type": "DigitalDocument",
        "@id": "http:\/\/creativecommons.org\/licenses\/by\/4.0\/",
        "additionalType": "gdx:Protocol-License",
        "name": "Dataset Usage License",
        "url": "http:\/\/creativecommons.org\/licenses\/by\/4.0\/"
    },
    "publisher": {
        "@id": "https:\/\/www.bco-dmo.org\/affiliation\/191",
        "@type": "Organization",
        "additionalType": "geolink:Organization",
        "legalName": "Biological and Chemical Data Management Office",
        "name": "BCO-DMO",
        "identifier": "http:\/\/lod.bco-dmo.org\/id\/affiliation\/191",
        "url": "https:\/\/www.bco-dmo.org\/affiliation\/191",
        "sameAs": "http:\/\/www.re3data.org\/repository\/r3d100000012"
    },
    "provider": {
        "@id": "https:\/\/www.bco-dmo.org\/affiliation\/191"
    },
    "includedInDataCatalog": [{
        "@id": "http:\/\/www.bco-dmo.org\/datasets"
    }],
    "recordedAt": [{
        "@type": "Event",
        "additionalType": "geolink:Cruise",
        "@id": "https:\/\/www.bco-dmo.org\/deployment\/57639",
        "name": "LMG0106",
        "description": "",
        "location": {
            "@type": "Place",
            "name": "Southern Ocean",
            "address": "Southern Ocean"
        },
        "url": "https:\/\/www.bco-dmo.org\/deployment\/57639",
        "recordedIn": {
            "@type": "CreativeWork",
            "isBasedOn": {
                "@type": "Vehicle",
                "additionalType": "geolink:Platform",
                "@id": "https:\/\/www.bco-dmo.org\/platform\/54020",
                "name": "ARSV Laurence M. Gould",
                "url": "https:\/\/www.bco-dmo.org\/platform\/54020"
            }
        },
        "startDate": "2001-07-21",
        "endDate": "2001-09-01"
    }, {
        "@type": "Event",
        "additionalType": "geolink:Cruise",
        "@id": "https:\/\/www.bco-dmo.org\/deployment\/57644",
        "name": "LMG0205",
        "description": "",
        "location": {
            "@type": "Place",
            "name": "Southern Ocean",
            "address": "Southern Ocean"
        },
        "url": "https:\/\/www.bco-dmo.org\/deployment\/57644",
        "recordedIn": {
            "@type": "CreativeWork",
            "isBasedOn": {
                "@type": "Vehicle",
                "additionalType": "geolink:Platform",
                "@id": "https:\/\/www.bco-dmo.org\/platform\/54020",
                "name": "ARSV Laurence M. Gould",
                "url": "https:\/\/www.bco-dmo.org\/platform\/54020"
            }
        },
        "startDate": "2002-07-29",
        "endDate": "2002-09-18"
    }],
    "isPartOf": [{
        "@type": "CreativeWork",
        "additionalType": "earthcollab:Project",
        "@id": "https:\/\/www.bco-dmo.org\/project\/2039",
        "name": "U.S. GLOBEC Southern Ocean",
        "alternateName": "SOGLOBEC",
        "description": "The fundamental objectives of United States Global Ocean Ecosystems Dynamics (U.S. GLOBEC) Program are dependent upon the cooperation of scientists from several disciplines. Physicists, biologists, and chemists must make use of data collected during U.S. GLOBEC field programs to further our understanding of the interplay of physics, biology, and chemistry. Our objectives require quantitative analysis of interdisciplinary data sets and, therefore, data must be exchanged between researchers. To extract the full scientific value, data must be made available to the scientific community on a timely basis.\n",
        "url": "https:\/\/www.bco-dmo.org\/project\/2039"
    }],
    "distribution": [{
        "@type": "DataDownload",
        "contentUrl": "https:\/\/www.bco-dmo.org\/dataset\/3300\/data\/download",
        "encodingFormat": "text\/tab-separated-values",
        "datePublished": "2010-02-03",
        "inLanguage": "en-US"
    }],
    "measurementTechnique": ["Hand-held plankton net", "Manual Biota Sampler"],
    "variableMeasured": [{
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20860",
        "value": "cruiseid",
        "description": "cruise identification\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20860",
        "unitText": "text",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/789",
            "value": "cruise id ",
            "description": "cruise identifier, e.g. en9402 R\/V Endeavor cruise 9402\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/789"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20861",
        "value": "year",
        "description": "year of experiment\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20861",
        "unitText": "YYYY",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1062",
            "value": "year",
            "description": "year, reported as YYYY, e.g. 1995\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1062"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20862",
        "value": "sample_id",
        "description": "sample identification: WBC=whole body clearance expt.; WBF=whole body fluorescence on collection\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20862",
        "unitText": "alpha-numeric",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1073",
            "value": "no standard parameter",
            "description": "association with a community-wide standard parameter is not yet defined\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1073"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20863",
        "value": "time_sample",
        "description": "time of sampling for pigment content after collection; decline of pigment content with time was used to calculate time to clear the gut of pigment.\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20863",
        "unitText": "minutes",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1073",
            "value": "no standard parameter",
            "description": "association with a community-wide standard parameter is not yet defined\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1073"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20864",
        "value": "pigment_content",
        "description": "pigment content\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20864",
        "unitText": "micrograms total chl\/grams wet weight",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1073",
            "value": "no standard parameter",
            "description": "association with a community-wide standard parameter is not yet defined\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1073"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20865",
        "value": "stage_id",
        "description": "stage development index of larvae in sample (furcilia = F1-6 = 1-6,  juvenile = J=7)\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20865",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1073",
            "value": "no standard parameter",
            "description": "association with a community-wide standard parameter is not yet defined\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1073"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20866",
        "value": "wet_weight",
        "description": "average wet weight\/larvae in sample\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20866",
        "unitText": "mg",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1073",
            "value": "no standard parameter",
            "description": "association with a community-wide standard parameter is not yet defined\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1073"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20874",
        "value": "lat",
        "description": "latitude, in decimal degrees, North is positive, negative denotes South\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20874",
        "unitText": "decimal degrees",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/730",
            "value": "latitude",
            "description": "latitude, in decimal degrees, North is positive, negative denotes South; Reported in some datasets as degrees, minutes\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/730",
            "unitText": "decimal degrees"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20875",
        "value": "lon",
        "description": "longitude, in decimal degrees, East is positive, negative denotes West\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20875",
        "unitText": "decimal degrees",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/731",
            "value": "longitude",
            "description": "longitude, in decimal degrees, East is positive, negative denotes West; Reported in some datsets as degrees, minutes\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/731",
            "unitText": "decimal degrees"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20876",
        "value": "day_local",
        "description": "day of month, local time\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20876",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/803",
            "value": "day_local ",
            "description": "day, local time \n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/803"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20877",
        "value": "month_local",
        "description": "month, local time\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20877",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/895",
            "value": "month_local",
            "description": "month of year, local time\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/895"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20878",
        "value": "time_local",
        "description": "time of day, local time, using 2400 clock format\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20878",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1007",
            "value": "time_local",
            "description": "time of day, local time, using 2400 clock format\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1007"
        }
    }, {
        "@type": "PropertyValue",
        "additionalType": "earthcollab:Parameter",
        "@id": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20879",
        "value": "yrday_local",
        "description": "local day and decimal time, as 326.5 for the 326th day of the year, or November 22 at 1200 hours (noon)\n",
        "url": "https:\/\/www.bco-dmo.org\/dataset-parameter\/20879",
        "valueReference": {
            "@type": "PropertyValue",
            "@id": "https:\/\/www.bco-dmo.org\/parameter\/1069",
            "value": "yrday_local ",
            "description": "local day and decimal time, as 326.5 for the 326th day of the year, or November 22 at 1200 hours (noon)\n",
            "url": "https:\/\/www.bco-dmo.org\/parameter\/1069"
        }
    }]
}
```
