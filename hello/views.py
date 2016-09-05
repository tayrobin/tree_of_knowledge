from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json, random, requests

from .models import Greeting

## homepage
def index(request):

	return render(request, 'base.html')

## show first version of tree
def showTree1(request):

	return render(request, 'tree_of_knowledge.html')

## show second version of tree
def showTree2(request):

	return render(request, 'tree_of_knowledge_v2.html')

## keeping so things don't break
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})
