# examples/hydrocarbon

https://search.dataone.org/view/urn%3Auuid%3A3249ada0-afe3-4dd6-875e-0f7928a4c171

Why it's a good test:

- Has PROVONE prov

## Abridged Output

Issues:

- [ ] Where's the PROV?

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix d1d: <https://dataone.org/datasets/> .
@prefix d1o: <https://dataone.org/organizations/> .
@prefix d1p: <https://dataone.org/people/> .
@prefix dataone: <https://dataone.org/> .
@prefix so: <http://schema.org/> .
@prefix spd: <http://spdx.org/rdf/terms#> .

d1d:urn%3Auuid%3A3249ada0-afe3-4dd6-875e-0f7928a4c171 a so:Dataset ;
  so:name "Analysis of hydrocarbons following the Exxon Valdez oil spill, Gulf of Alaska, 1989 - 2014" ;
  so:description """This hydrocarbon database was initiated after the Exxon Valdez oil spill in 1989. The first version was as an RBase database, PWSOIL(Short, Heintz et al. 1996). It migrated to a proprietary structure in 1997, EVTHD (Exxon Valdez Oil Spill
              Trustee Council Hydrocarbon Database) and contained the collection and hydrocarbon analysis information for environmental samples obtained for the Exxon Valdez National Resource Damage Assessment and Restoration efforts. The data were organized into
              three matrix types, tissues, sediment, and seawater. The analytical results included concentrations of 63 hydrocarbons, summary statistics for the evaluation of the hydrocarbon sources and laboratory quality control data. Features of the database
              included identification of replicate samples, presentation of results in dry or wet weight, optional correction for method detection limits (MDL) of the analytes, and easy identification of samples contaminated with Exxon Valdez crude oil. This
              structure, written in Visual Basic, ceased to function well when Windows operating systems were upgraded to XP and the data were moved to a Microsoft Access format. The 2014 version continues in Access and is described in the included lexicon
              document. The 2014 version also includes a data analysis tool (Excel Office 2007 or greater) that flags recovery problems, provides method detection limit filtration (MDL), and source oil modeling. The data should not be used without understanding
              these details. Further instructions are in the lexicon document. These data are included here as exported csv files of the individual tables from the original MS Access database file available at
              http://portal.aoos.org/gulf-of-alaska.php#metadata/91b73240-b68d-43d8-bd64-aea4ea14e976/project/files. The DataDownload.R script used to download these csv files is also included here. The data have been manipulated and combined using the R script
              below (Total_PAH_and_Alkanes_GoA_Hydrocarbons_Clean.R), and output into the Total_Aromatic_Alkanes_PWS.csv file.""" ;
  so:identifier "urn:uuid:3249ada0-afe3-4dd6-875e-0f7928a4c171" ;

  so:creator d1p:urn%3Auuid%3A3c7e78d5-4dd0-4fc8-bd26-7cd75031858f ;

  so:dateModified "2017-05-05T15:14:00.201000Z" ;
  so:datePublished "2017-05-05T15:14:00.201000Z" ;

  so:distribution d1d:urn%3Auuid%3A44108e76-405d-4d58-b1b3-fb4b55e3fff9 ;
  so:distribution d1d:urn%3Auuid%3A5cde46ff-2e8e-4f40-97a1-eb4c4851f22f ;
  so:distribution d1d:urn%3Auuid%3A5f57c5d3-65f2-4d46-83f5-67f8104c62dd ;
  so:distribution d1d:urn%3Auuid%3A66c416af-84e6-4c7e-92a9-4413cf8acd7b ;
  so:distribution d1d:urn%3Auuid%3A780a5cff-6071-47d1-a52f-8f7a60c24625 ;
  so:distribution d1d:urn%3Auuid%3A9490ce50-b7bc-4fe8-89d1-5b00736df835 ;
  so:distribution d1d:urn%3Auuid%3Aa8ed4776-1e17-426f-9f54-98073ae35b5f ;
  so:distribution d1d:urn%3Auuid%3Ab4b3cc45-4953-43d3-910a-847528577531 ;
  so:distribution d1d:urn%3Auuid%3Ac2f47e88-cc2b-47db-a105-101b80e80334 ;

  so:isAccessibleForFree true ;

  so:keyword "Alaska" ;
  so:keyword "EVOS" ;
  so:keyword "Exxon Valdez" ;
  so:keyword "alkane" ;
  so:keyword "hydrocarbon" ;
  so:keyword "oil" ;
  so:keyword "oil spill" ;
  so:keyword "pah" ;

  so:spatialCoverage [
    a so:Place ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Spatial Reference System" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "http://www.opengis.net/def/crs/OGC/1.3/CRS84" ;
    ] ;
    so:additionalProperty [
      a so:PropertyValue ;
      so:name "Well-Known Text (WKT) representation of geometry" ;
      so:propertyID <http://www.wikidata.org/entity/Q4018860> ;
      so:value "POLYGON ((-159.8752 61.77312, -121.65 61.77312, -121.65 43.83333, -159.8752 43.83333, -159.8752 61.77312))" ;
    ] ;
    so:description "Gulf of Alaska, Alaksa" ;
    so:geo [
      a so:GeoShape ;
      so:box "61.77312,-121.65 43.83333,-159.8752" ;
    ] ;
  ] ;
  so:temporalCoverage "1989/2014" ;

  so:url "https://dataone.org/datasets/urn%3Auuid%3A3249ada0-afe3-4dd6-875e-0f7928a4c171" ;

  so:variableMeasured [
    a so:PropertyValue ;
    so:description "The amount of C2-chrysene in the sample" ;
    so:name "C2CHRYS" ;
  ] ;

  so:schemaVersion "eml://ecoinformatics.org/eml-2.1.1" ;
  so:byteSize 10283064 ;

  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "acd7e08524fff623123c879427c69ee025ef050e" ;
  ] .

d1d:urn%3Auuid%3A44108e76-405d-4d58-b1b3-fb4b55e3fff9 a so:DataDownload ;
  so:byteSize 2801033 ;
  so:contentUrl "https://search.dataone.org/cn/v2/resolve/urn%3Auuid%3A44108e76-405d-4d58-b1b3-fb4b55e3fff9" ;
  so:dateModified "2017-05-05T15:14:08.302000Z" ;
  so:datePublished "2017-05-05T15:14:08.302000Z" ;
  so:encodingFormat "text/csv" ;
  so:identifier "https://dataone.org/datasets/urn%3Auuid%3A44108e76-405d-4d58-b1b3-fb4b55e3fff9" ;
  so:name "Total_Aromatic_Alkanes_PWS.csv" ;
  spd:checksum [
    a spd:Checksum ;
    spd:checksumValue "53473dd8b5ab7aee559915d55d6ec8ba112c4917" ;
  ] .

d1o:urn%3Auuid%3Aa41dda7b-907d-4f90-9955-e46638b71b2b a so:Organization ;
  so:name "National Oceanic and Atmospheric Administration (NOAA) Alaska Fisheries Science Center (AFSC) Auke Bay Laboratories (ABL)" .

d1p:urn%3Auuid%3A3c7e78d5-4dd0-4fc8-bd26-7cd75031858f a so:Person ;
  so:affiliation d1o:urn%3Auuid%3Aa41dda7b-907d-4f90-9955-e46638b71b2b ;
  so:email "mark.carls@noaa.gov" ;
  so:name "Mark Carls" .
```
