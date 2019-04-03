from locust import HttpLocust, TaskSet, task
import urllib
from faker import Faker

fake = Faker()

class SPARQLQueryTasks(TaskSet):
    @task
    def query_simple(self):
        self.client.get("/sparql/?query=select+%2A+where+%7B+%3Fs+%3Fp+%3Fo+%7D+limit+0")

    @task
    def query_realistic(self):
        self.client.get("/sparql/?query=select+%2A+where+%7B+%3Fs+%3Fp+%3Fo+%7D+limit+0")

class SPARQLInsertTasks(TaskSet):
    @task
    def insert_simple(self):
        self.client.get("/sparql/?query=INSERT+DATA+%7B+GRAPH+%3Chttps%3A%2F%2Fdataone.org%3E+%7B+%3Chttp%3A%2F%2Fexample.com%2FX%3E+%3Chttp%3A%2F%2Fexample.com%2FisA%3E+%3Chttp%3A%2F%2Fexample.com%2FY%3E+%7D%7D")

    @task
    def insert_realistic(self):
        self.client.get("/sparql/?query=INSERT+DATA+%7B+GRAPH+%3Chttps%3A%2F%2Fdataone.org%3E+%7B+%3Chttp%3A%2F%2Fexample.com%2FX%3E+%3Chttp%3A%2F%2Fexample.com%2FisA%3E+%22{}%22+%7D%7D".format(urllib.quote(fake.name())))

class QueryLocust(HttpLocust):
    weight = 5
    task_set = SPARQLQueryTasks

class InsertLocust(HttpLocust):
    weight = 3
    task_set = SPARQLInsertTasks