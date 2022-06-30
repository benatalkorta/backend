from django.db import connection


def get_restricted_access(question_id):
    """GET  restricted fields from eccenca"""

    with connection.cursor() as cursor:

        query = """SELECT restricted_fields FROM  denyaccesstofields WHERE question_id=%s"""
        cursor.execute(query, (question_id,))

        result = cursor.fetchall()
        if result:
            if result[0][0]:

                result = set(result[0][0].split(","))
            else:
                result = None

    return result
