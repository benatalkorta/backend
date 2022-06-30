from django.db import models

# Create your models here.


class QuestionModel(models.Model):

    question_description = models.TextField(max_length=200)
    question_query = models.TextField(max_length=10000)
    variable_fields = models.CharField(max_length=100, blank=True, null=True)
    variable_types = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.question_description


class DenyAccessToFields(models.Model):

    question = models.ForeignKey(QuestionModel, on_delete=models.CASCADE)
    restricted_fields = models.TextField(max_length=10000)

    class Meta:
        db_table = "denyaccesstofields"

    def __str__(self):

        return self.restricted_fields
