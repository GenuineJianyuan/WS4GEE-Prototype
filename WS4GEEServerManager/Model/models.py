# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class ExecuteStatusRecord(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    execution_uuid = models.CharField(max_length=255, blank=True, null=True)
    process_uuid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'execute_status_record'

class DownloadingLog(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    image_uuid = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'downloading_log'


class DynamicWcs(models.Model):
    uuid = models.CharField(primary_key=True, max_length=256)
    req_uuid = models.CharField(max_length=64, blank=True, null=True)
    start = models.CharField(max_length=255, blank=True, null=True)
    end = models.CharField(max_length=255, blank=True, null=True)
    dataset_info = models.TextField(blank=True, null=True)
    image_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dynamic_wcs'


class ParamRecord(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    param_uuid = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=2048, blank=True, null=True)
    request_uuid = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'param_record'


class ParamRequest(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    process_uuid = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'param_request'


class Process(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    entrance_func = models.CharField(max_length=255, blank=True, null=True)
    entrance_name = models.CharField(max_length=255, blank=True, null=True)
    script_path = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=1024, blank=True, null=True)
    abstract = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process'


class ProcessParams(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    param_name = models.CharField(max_length=255, blank=True, null=True)
    data_type = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    param_type = models.CharField(max_length=255, blank=True, null=True)
    process_uuid = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    other_content = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'process_params'


class Record(models.Model):
    uuid = models.CharField(primary_key=True, max_length=255)
    doc_uuid = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'record'


class SearchRequest(models.Model):
    uuid = models.CharField(primary_key=True, max_length=64)
    dataset_name = models.CharField(max_length=255, blank=True, null=True)
    service_type = models.CharField(max_length=255, blank=True, null=True)
    stacking_method = models.CharField(max_length=255, blank=True, null=True)
    start = models.CharField(max_length=255, blank=True, null=True)
    end = models.CharField(max_length=255, blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    boundary_name = models.CharField(max_length=255, blank=True, null=True)
    bands = models.CharField(max_length=255, blank=True, null=True)
    no_cloud = models.IntegerField(blank=True, null=True)
    by_year = models.IntegerField(blank=True, null=True)
    by_month = models.IntegerField(blank=True, null=True)
    dataset_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'search_request'
