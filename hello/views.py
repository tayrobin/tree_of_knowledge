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

## new select with no pre-processing
getAllTreeObjects2 = """SELECT array_to_json(array_agg(row_to_json(t))) AS data
                        from (
                              SELECT id, name, link, parent_id as parent
                              FROM tree_data_2
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

	cur.execute(getAllTreeObjects2,)
	myJson = cur.fetchone()[0]
	print "Here's all my pre-sorted tree objects:",myJson

        for i in range(len(myJson)):
           if myJson[i]['parent'] is None:
              myJson[i].pop('parent', None)

        #this creates a dictionary that maps id names to JSON items.
        #ex. itemsKeyedById["9Xdd"] gives the jpg item with id "9Xdd"
        itemsKeyedById = {i["id"]: i for i in myJson}

        #iterate through each item in the `myJson` list.
        for item in myJson:
            #does the item have a parent?
            if "parent" in item:
                #get the parent item
                parent = itemsKeyedById[item["parent"]]
                #if the parent item doesn't have a "children" member, we must create one.
                if "children" not in parent:
                    parent["children"] = []
                #add the item to its parent's "children" list.
                parent["children"].append(item)

        #filter out any item that has a parent.
        #They don't need to appear at the top level, 
        #since they will appear underneath another item elsewhere.
        topLevelItems = [item for item in myJson if "parent" not in item]
        print topLevelItems

	return JsonResponse(topLevelItems)


## keeping so things don't break
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
