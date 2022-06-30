''' This module serves as a backend that connects to Eccenca '''
from unittest import result
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
import logging

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

        ''' Check the username for permissions and decide the access level granted for a user'''

        user_name = "admin" if not request.GET.get(
            "username") else request.GET.get("username")
        fields_set = None

        if user_name != "admin":
            fields_set = get_restricted_access(question_id, user_name)

        if not question_id:

            raise KeyError
        # Get Meta Data for a question this includes question id , the Query associated with a question and its variable fields

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
                    field_val = "" if not request.GET.get(
                        field) else request.GET.get(field)
                    final_field_val.append(field_val)
                # Execute the SparqlQuery with the variable fields
                results = json.loads(SparqlQuery(
                    results[0]["question_query"] % tuple(final_field_val)).get_results())
            else:
                results = json.loads(SparqlQuery(
                    results[0]["question_query"]).get_results())

            result_headers = results["head"]["vars"]

            final_result = []

            for i in results["results"]["bindings"]:
                triple_dict = {}
                for property_value in result_headers:
                    triple_dict[property_value] = i[property_value]["value"]

                final_result.append(triple_dict)

            if fields_set:
                # Filter properties from the restricted file list obtained earlier

                for i in final_result:
                    for key in fields_set:
                        if key in i:
                            del i[key]

            return Response(final_result, status=HTTP_200_OK)
        else:
            return Response({}, status=HTTP_404_NOT_FOUND)

class InsertStudentInDatabase(APIView):
    def get(self, request):

        print(request.GET)

        first_name = request.GET.get("first_name")
        last_name = request.GET.get("last_name")
        id = request.GET.get("id")

        print(first_name)
        print(last_name)
        print(id)


        query_string_insert = "PREFIX sn: <http://www.infineon.org/2020/11/Admindata#> INSERT DATA {GRAPH <http://www.infineon.org/2020/11/Admin_Graph_Benat>{sn:Admin_graph_ifx"+id+" sn:Firstname \"" +first_name+ "\" .sn:Admin_graph_ifx"+id+" sn:Lastname \"" +last_name+ "\" .}}"

        result_insert=json.loads(SparqlQuery(query_string_insert).get_results())

        return Response(result_insert, status=HTTP_200_OK)

class DeleteStudentInDatabase(APIView):
    def get(self, request):

        print(request.GET)

        first_name = request.GET.get("first_name")
        last_name = request.GET.get("last_name")
        id = request.GET.get("id")

        print(first_name)
        print(last_name)
        print(id)

        query_string_delete = "PREFIX sn: <http://www.infineon.org/2020/11/Admindata#> DELETE DATA {GRAPH <http://www.infineon.org/2020/11/Admin_Graph_Benat> {sn:Admin_graph_ifx"+id+" sn:Firstname \"" +first_name+ "\" . sn:Admin_graph_ifx"+id+" sn:Lastname \"" +last_name+ "\" .}}"

        result_delete=json.loads(SparqlQuery(query_string_delete).get_results())

        return Response(result_delete, status=HTTP_200_OK)