''' This module serves as a backend that connects to Eccenca '''
from django.shortcuts import render

# Create your views here.

from os import environ
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.db import connection
from cmem.cmempy.workspace.projects.project import get_projects
from cmem.cmempy.workflow import get_workflows
from cmem.cmempy.workspace.activities.taskactivity import get_activity_status
from cmem.cmempy.queries import SparqlQuery
from cmem.cmempy import queries as qlist
from django.core.cache import cache

from .utils import get_restricted_access

environ["CMEM_BASE_URI"] = "https://braine.eccenca.dev/"
environ["OAUTH_GRANT_TYPE"] = "password"
environ["OAUTH_CLIENT_ID"] = "cmemc"
environ["OAUTH_USER"] = "kwibmer"
environ["OAUTH_PASSWORD"] = "5hyZ5PNjF4b#"


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class GetQueryResults(APIView):

    ''' GET results for a query that is generated from
    the competency questions'''

    def get(self, request):
        ''' Return a list of all users '''

#        start_date = request.GET.get("start_date")
#        end_date = request.GET.get("end_date")

        QUERY_TEXT = '''PREFIX sn: <http://www.infineon.org/2020/11/Admindata#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT * 
            FROM <http://www.infineon.org/2020/11/Admin_Graph>  
            WHERE {
             ?Person sn:Firstname ?Firstname .
             ?Person sn:Working_Hours ?Working_Hours .
             ?Person sn:Work_Type ?Work_Type .
            ?Person sn:Contract_From ?Contract_From .
            ?Person sn:Contract_From "01.02.2020" .
            ?Person sn:Contract_Till ?Contract_Till .
            ?Person sn:Contract_Till "01.03.2020" .

            }
'''
        results = json.loads(SparqlQuery(QUERY_TEXT).get_results())
        if results:

            final_result = []

            for i in results["results"]["bindings"]:
                person_id = i["Person"]["value"]
                first_name = i["Firstname"]["value"]
                working_hours = i["Working_Hours"]["value"]
                work_type = i["Work_Type"]["value"]
                final_result.append({
                    "id": person_id,
                    "first_name": first_name,
                    "working_hours": working_hours,
                    "working_type": work_type
                })

            return Response(final_result, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_404_NOT_FOUND)


class ListQuestions(APIView):

    def get(self, request):
        ''' GET the list of questions from the database'''
        with connection.cursor() as cursor:

            query = '''SELECT id,question_description, variable_fields, variable_types FROM queryprocessor_questionmodel'''
            cursor.execute(query)
            result = dictfetchall(cursor)

        if result:

            return Response(result, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_404_NOT_FOUND)


class ExecuteQueryByID(APIView):

    def get(self, request, question_id):
        print(request.GET.get("username"))

        user_name = "admin" if not request.GET.get(
            "username") else request.GET.get("username")
        fields_set = None

        if user_name != "admin":
            fields_set = get_restricted_access(question_id)

        if not question_id:

            raise KeyError

        with connection.cursor() as cursor:

            query = '''SELECT question_query,variable_fields FROM queryprocessor_questionmodel 
            WHERE id=%s'''
            query_params = (question_id,)

            cursor.execute(query, query_params)
            results = dictfetchall(cursor)

        if results:
            if results[0]["variable_fields"]:
                variable_fields = results[0]["variable_fields"].split(",")
                final_field_val = []
                for field in variable_fields:
                    field_val = "" if not request.query_params.get(field) else request.query_params.get(field)
                    final_field_val.append(field_val)
                    print(request.GET.get(field))
                print(repr(results[0]["question_query"] %tuple(final_field_val)))

                results = json.loads(SparqlQuery(
                results[0]["question_query"] %tuple(final_field_val)).get_results())
            else:
                results = json.loads(SparqlQuery(results[0]["question_query"]).get_results())

            result_headers = results["head"]["vars"]

            final_result = []

            for i in results["results"]["bindings"]:
                triple_dict = {}
                for property_value in result_headers:
                    triple_dict[property_value] = i[property_value]["value"]

                final_result.append(triple_dict)

            if fields_set:

                for i in final_result:
                    for key in fields_set:
                        if key in i:
                            del i[key]

            return Response(final_result, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_404_NOT_FOUND)
