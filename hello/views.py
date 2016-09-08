from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
import json, random, requests, psycopg2, urlparse, os

from .models import Greeting

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])
inputPassword = os.environ["INPUT_PASSWORD"]

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

## add new data into the tree_data_2 table
insertNewKnowledge = "INSERT INTO tree_data_2 (name, link, parent_id) VALUES (%(name)s, %(link)s, %(parent_id)s) RETURNING *"

## get a parent ID given a name
selectParentId = "SELECT id FROM tree_data_2 WHERE LOWER(name) LIKE LOWER(%(parent_name)s) LIMIT 1"


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


## experimenting with different styles of data trees
def showTree4(request):
    return render(request, 'tree_of_knowledge_v4.html')


## experimenting with pannable data tree
def showTree5(request):
    return render(request, 'tree_of_knowledge_v5.html')


## add new data to the database
@csrf_exempt
def inputData(request):

    if request.method == 'POST':
        print "POST order up!"
        print request.POST
        inputs = dict(request.POST)

        ## check for valid password, for now to prevent spam
        if 'password' in inputs and inputs['password'] is not None:

            password = inputs['password']

            if password != inputPassword:
                ## permission denied
                #return HttpResponse(status=403)
                print "Password Incorrect. Given:%s"%password
                raise PermissionDenied

            elif password == inputPassword:

                ## process inputs
                if 'name' in inputs and inputs['name'] is not None and inputs['name'] != '':
                    name = inputs['name'].capitalize()
                else:
                    ## don't accept null names, return 400 error
                    print "invalid name provided: %s"%inputs['name']
                    return HttpResponse('You gave me an invalid Name.', status=400)

                if 'link' in inputs and inputs['link'] is not None:
                    link = inputs['link']
                else:
                    link = None

                if 'parent' in inputs and inputs['parent'] is not None and inputs['parent'] != '':
                    parent_name = inputs['parent']
                else:
                    ## don't accept null parent names, return 400 error
                    print "invalid parent name provided: %s"%inputs['parent']
                    return HttpResponse('You have me an invalid Parent Name.', status=400)

                ## figure out which parent_id to use...
                cur.execute(selectParentId, {'parent_name':parent_name})
                parent_id = cur.fetchone()[0]

                if parent_id is None or parent_id == '':
                    print "couldn't match a parent name to the one provided: %s"%parent_name
                    return HttpResponse('I was unable to find a Parent ID to match the Parent you provided: (%(parent_name)s)'%{'parent_name':parent_name}, status=400)

                cur.execute(insertNewKnowledge, {'name':name, 'link':link, 'parent_id':parent_id})
                conn.commit()
                dataInserted = cur.fetchone()

                print "New Knowledge added to the database! (%(child)s is a child of %(parent)s)"%{'name':name, 'parent':parent_name}

                return JsonResponse(dataInserted, status=200)


## display json data
def showData(request):
	return render(request, 'data.json')


## display miserables.json data
def showMiserablesData(request):
	return render(request, 'miserables.json')


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

	return JsonResponse({'id':0, 'name':'root', 'link':'', 'children':topLevelItems})


## keeping so things don't break
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
