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

## built from: http://lakshminp.com/building-nested-hierarchy-json-relational-db
getTreeData = """WITH data AS(
						select array_to_json(array_agg(row_to_json(t))) as data
							from (
							 SELECT id, name, link, COALESCE(get_children(id), '[]') as children from tree_data_2
							) t
						) SELECT get_tree(data) from data;"""

## saving this for manual processing in python below
getAllTreeObjects = """SELECT array_to_json(array_agg(row_to_json(t))) AS data
						from (
						SELECT id, name, link, COALESCE(get_children(id), '[]') AS children FROM tree_data_2
						) t"""


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

	cur.execute(getAllTreeObjects,)
	treeObjects = cur.fetchone()[0]
	print "Here's all my pre-sorted tree objects:",treeObjects

	def findRoot(treeObjects):

		for obj in treeObjects:

			root = True
			objId = obj['id']

			for obj2 in treeObjects:

				if obj2['id'] == objId:
					continue

				if obj2['children'] != []:

					for child in obj2['children']:

						if child['id'] == objId:
							root = False

			if root:
				return obj

	treeRoot = findRoot(treeObjects)

	## from online javascript get_tree function
	def get_tree(data):

		root = []

		def getObject(theObject, id):

			result = None

			if type(theObject) == list:

				for i in range(len(theObject)):
					result = getObject(theObject[i], id)
					if result is not None:
						break

			else:

				for prop in theObject:
					if prop == 'id':
						if theObject[prop] == id:
							return theObject

					if type(theObject[prop]) == dict or type(theObject[prop]) == list:
						result = getObject(theObject[prop], id):
						if result is not None:
							break

			return result

		def build_tree(id, name, link, children):
			exists = getObject(root, id)
			if exists is not None:
				exists['children'] = children
			else:
				root.append({'id':id, 'name':name, 'link':link, 'children':children})

		for i in range(len(data)):
			build_tree(data[i]['id'], data[i]['name'], data[i]['link'], data[i]['children'])


	return JsonResponse(dict(response=root))


## keeping so things don't break
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
