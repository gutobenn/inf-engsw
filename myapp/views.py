from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from myapp.forms import SignUpForm, ItemForm
from myapp.models import Item


def index(request):
    items = Item.objects.filter(published_date__lte=timezone.now()).order_by('published_date') # TODO limitar numero de itens que aparece na pagina inicial
    return render(request, 'myapp/index.html', {'items': items})

@login_required(login_url='login')
def items(request):
    #items = Item.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    items = Item.objects.filter(owner=request.user).order_by('published_date')
    return render(request, 'myapp/items.html', {'items': items})

@login_required(login_url='login')
def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.published_date = timezone.now()
            item.save()
            return redirect('items') #'post_detail', pk=post.pk)
    else:
        form = ItemForm()
    return render(request, 'myapp/item_new.html', {'form': form})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'myapp/item_detail.html', {'item': item})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'myapp/signup.html', {'form': form})
