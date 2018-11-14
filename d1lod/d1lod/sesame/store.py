"""d1lod.virtuoso.store

This is a repository manager for the d1lod service to manage the Virtuoso repositories.
It contains the following functionality:

1. CREATE operation Creating a new repository in stores that support empty repositories.
2. DELETE operation Removing a repository and all of its contents.
3. COPY operation Modifying a repository to contain a copy of another.
4. MOVE  operation Moving all of the data from one repository into another.
5. ADD operation Reproducing all data from one repository into another.
6. Getting a list of all the repositories.

"""

import requests
import logging


class Store:
    def __init__(self, host, port, name, ns={}):
        self.name = name
        self.ns = ns
        self.host = host
        self.port = port
        self.endpoints = {
            'sparql': 'http://%s:%s/sparql' % (self.host, self.port),
        }

        # Set aside a Session object
        # We use this when making HTTP requests to reduce overhead when making
        # many requests during the lifetime of a Repository objects
        self.session = requests.Session()


    def __str__(self):
        return "Repository: '%s'" % self.name


    def exists(self, repository_name):
        """Execute a SPARQL QUERY against the Repository.

        Arguments:
        ----------

        repository_name: str
            the <URI> to of the repository to check its existence

        Returns: A boolean value representing the existence of the Repository."""
        query_string = "ASK WHERE { GRAPH <" + repository_name + "> { ?s ?p ?o } }"
        sparqlResponse = self.query(query_string=query_string, accept='text/plain')
        return sparqlResponse.content


    def create_repository(self, repository_name, silent=False):
        """This operation creates a repository in the Repository Store.

        Arguments:
        ----------

        repository_name: str
            the <URI> to be used to create the repository

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while creating the repository.
            By default it is set to False.


        Returns: None."""
        if self.exists(repository_name) == "false":
            print "Creating repository - " + repository_name
            if not silent:
                create_query = "CREATE GRAPH <" + repository_name + ">"
            else:
                create_query = "CREATE SILENT GRAPH <" + repository_name + ">"
            sparqlResponse = self.query(query_string=create_query, accept='text/plain')
            print sparqlResponse.content
        else:
            print "Repository already exists!"

        return


    def delete_repository(self, repository_name, silent=False):
        """This operation deletes a repository from the Repository Store.
        TODO: deletes only empty repositories

        Arguments:
        ----------

        repository_name: str
            the <URI> of the repository to be deleted

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while deleting the repository
            By default it is set to False.

        Returns: None."""
        if self.exists(repository_name) == "true":
            print "Deleting repository - " + repository_name
            if not silent:
                delete_query = "DROP GRAPH <" + repository_name + ">"
            else:
                delete_query = "DROP SILENT GRAPH <" + repository_name + ">"
            sparqlResponse = self.query(query_string=delete_query, accept='text/plain')
            print sparqlResponse.content
        else:
            print "Repository does not exists!"

        return


    def copy_repository(self, source_repository_name, target_repository_name, silent=False):
        """The COPY operation is a shortcut for inserting all data from an input repository into a destination repository.
        Data from the input repository is not affected, but data from the destination repository,
        if any, is removed before insertion.

        Arguments:
        ----------

        source_repository_name: str
            the <URI> of the source repository

        target_repository_name: str
            the <URI> of the destination repository

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while copying triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_repository_name) == "true":
            print "Copying source repository - " + source_repository_name + " to the destination repository - " + target_repository_name
            if not silent:
                copy_query = "COPY GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            else:
                copy_query = "COPY SILENT GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            sparqlResponse = self.query(query_string=copy_query, accept='text/plain')
            print sparqlResponse.content
        else:
            print "Source Repository does not exists!"

        return


    def move_repository(self, source_repository_name, target_repository_name, silent=False):
        """The MOVE operation is a shortcut for moving all data from an input repository into a destination repository.
        The input repository is removed after insertion and data from the destination repository,
        if any, is removed before insertion.

        Arguments:
        ----------

        source_repository_name: str
            the <URI> of the source repository

        target_repository_name: str
            the <URI> of the destination repository

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while moving from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_repository_name) == "true":
            print "Moving source repository - " + source_repository_name + " to the destination repository - " + target_repository_name
            if not silent:
                move_query = "MOVE GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            else:
                move_query = "MOVE SILENT GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            sparqlResponse = self.query(query_string=move_query, accept='text/plain')
            print sparqlResponse.content
        else:
            print "Source Repository does not exists!"

        return


    def add_repository(self, source_repository_name, target_repository_name, silent=False):
        """The ADD operation is a shortcut for inserting all data from an input repository into a destination repository.
         Data from the input repository is not affected, and initial data from the destination repository,
         if any, is kept intact.

        Arguments:
        ----------

        source_repository_name: str
            the <URI> of the source repository

        target_repository_name: str
            the <URI> of the destination repository

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while adding the triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_repository_name) == "true":
            print "Adding source repository - " + source_repository_name + " to the destination repository - " + target_repository_name
            if not silent:
                add_query = "ADD GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            else:
                add_query = "ADD SILENT GRAPH <" + source_repository_name + "> TO GRAPH <" + target_repository_name + ">"
            sparqlResponse = self.query(query_string=add_query, accept='text/plain')
            print sparqlResponse.content
        else:
            print "Source Repository does not exists!"

        return

    def query(self, query_string, accept='application/json'):
        """Execute a SPARQL QUERY against the Repository.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.

        accept : str
            An appropriate HTTP Accept header value. Defaults to JSON.

        formatResponse: boolean
            A boolean value indicating the formatting requirements of the results.


        Returns: A result dict containing the query response."""

        # getrting the namespaces before performing the query
        prefix = self.namespacePrefixString()

        results = {}
        endpoint = self.endpoints['sparql']
        params = {
            'query': prefix + "\n" + query_string
        }

        r = self.session.post(endpoint, params=params, auth=('dba', 'dev.nceas'))
        print r.headers

        logging.info(prefix + "\n" + query_string)

        if r.status_code != 200:
            print "SPARQL QUERY failed. Status was not 200 as expected."
            print r.status_code
            print r.text
            print query_string

        if r.headers['Content-Type'] == "application/sparql-results+xml; charset=UTF-8":
            response_type = "xml"
            response_var = r.content
            results = self.processResponse(response_var, response_type)

        elif r.headers['Content-Type'] == "application/json":
            try:
                response_type = "json"
                response_var = r.json()
                results = self.processResponse(response_var, response_type)
            except:
                print "Failed to convert response to JSON."
                print r.status_code
                print r.text
                results = []

        return results


    def processResponse(self, response_var, response_type):
        """Process a JSON response from the Repository and create a friendlier
        format. The format is a list of Dicts, where the names in each dict
        match the bindings of the query.
        """
        results = []

        if response_type == "xml":
            response_content = ET.fromstring(response_var)


            xml_result_element = []
            xml_results_element = None
            xml_result = []


            for child in response_content:
                if child.tag == '{http://www.w3.org/2005/sparql-results#}head':
                    xml_head_element = child
                elif child.tag == '{http://www.w3.org/2005/sparql-results#}results':
                    xml_results_element = child
                else:
                    pass

            for child in xml_results_element:
                if child.tag == '{http://www.w3.org/2005/sparql-results#}result':
                    xml_result_element.append(child)

            for result in xml_result_element:
                xml_result = []
                for binding in result:
                    xml_result_dict = {}
                    binding_key = binding.attrib["name"]
                    binding_val = None
                    for uri in binding:
                        binding_val = uri.text
                    xml_result_dict[binding_key] = binding_val
                    xml_result.append(xml_result_dict)

            results = xml_result

        else:
            response = response_var

            if 'head' not in response['sparql'] or 'results' not in response['sparql'] \
                    or 'result' not in response['sparql']['results'] \
                    or 'binding' not in response['sparql']['results']['result']:
                return results



            for binding in response['sparql']['results']['result']['binding']:
                row = {}

                row[binding["@name"]] = binding["uri"]

                results.append(row)

        return results

if __name__ == "__main__":
    repository1 = Store("localhost", "8890", "BookStore")
    repository1.add_repository("Bookstore", "Bookstore3")
