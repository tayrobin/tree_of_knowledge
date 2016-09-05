from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json, random, requests, psycopg2, urlparse, os

from .models import Greeting

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cur = conn.cursor()

getTreeData = """WITH data AS(
						select array_to_json(array_agg(row_to_json(t))) as data
							from (
							 SELECT id, name, COALESCE(get_children(id), '[]') as children from tree_data_2
							) t
						) SELECT get_tree(data) from data;"""


## homepage
def index(request):

	return render(request, 'base.html')


## show first version of tree
def showTree1(request):

	return render(request, 'tree_of_knowledge.html')


## show second version of tree
def showTree2(request):

	return render(request, 'tree_of_knowledge_v2.html')

##### REAL ONE #####
## show my version of tree, with my data
def showTree3(request):

	return render(request, 'tree_of_knowledge_v3.html')

##### END REAL ONE #####


## display json data
def showData(request):

	return render(request, 'data.json')


## display live json tree data from database
def showDataLive(request):

	cur.execute(getTreeData,)
	treeData = cur.fetchone()[0]
	print "Here's my tree data:",treeData
	return JsonResponse(treeData)


## keeping so things don't break
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
