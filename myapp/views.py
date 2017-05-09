from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'myapp/index.html')

def items(request):
    return render(request, 'myapp/items.html')
