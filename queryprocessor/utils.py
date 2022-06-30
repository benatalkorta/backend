
from django.db import connection
from cmem.cmempy.queries import SparqlQuery
import json


def get_restricted_access(question_id, user_name):
    """GET  restricted fields from eccenca for a user"""
    if "admin" in user_name:

        return None

    query = """

    PREFIX sn: <http://www.infineon.org/2020/11/Access_%s>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT *

    FROM <http://www.infineon.org/2020/11/Access_%s>

    WHERE {
     
       ?s ?p ?o
    }
    ORDER BY ?p

    """ % (str(question_id), str(question_id))
    results = json.loads(SparqlQuery(query).get_results())

    iter_result = results["results"]["bindings"]
    fields = []

    for value in iter_result:

        if "Admin" in value["s"]["value"]:

            if "All_Properties" in value["p"]["value"]:
                break
        else:

            if "Deny" in value["p"]["value"]:

                fields.append(value["o"]["value"])

    return fields
