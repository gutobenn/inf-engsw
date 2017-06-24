# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from alugueme.forms import SignUpForm, ItemForm, SearchItemForm, RentForm
from alugueme.models import Item, Rent
from search_views.views import SearchListView
from search_views.filters import BaseFilter

def index(request):
    items = Item.objects.filter(published_date__lte=timezone.now(), status=Item.AVAILABLE_STATUS).order_by('published_date')[:12]
    return render(request, 'alugueme/index.html', {'items': items})

@login_required(login_url='login')
def items_my(request):
    items = Item.objects.filter(owner=request.user).order_by('published_date')
    return render(request, 'alugueme/items_my.html', {'items': items})

@login_required(login_url='login')
def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.published_date = timezone.now()
            item.save()
            messages.success(request, 'Item cadastrado com sucesso!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'alugueme/item_edit.html', {'form': form, 'title': 'Cadastrar Item'})

@login_required(login_url='login')
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.user != item.owner:
        return redirect('index')

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.published_date = timezone.now()
            item.save()
            messages.success(request, 'Item alterado com sucesso!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'alugueme/item_edit.html', {'form': form, 'title': 'Editar Item'})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = RentForm(request.POST)
        if form.is_valid():
            rent = form.save(commit=False)
            rent.user = request.user
            rent.item = item
            rent.status = rent.PENDING_STATUS
            rent.request_date = timezone.now()
            rent.save()
            messages.success(request, 'Pedido realizado com sucesso! Assim que o dono do item avaliá-lo, te enviaremos um e-mail.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = RentForm()
    return render(request, 'alugueme/item_detail.html', {'item': item, 'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Olá, {0}!'.format(user))
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'alugueme/signup.html', {'form': form})

class ItemFilter(BaseFilter):
    def only_available_status_query_method(model_field, request_field_value, params_dict):
        return Q(status__lte=Item.AVAILABLE_STATUS)

    search_fields = {
        "search_text" : ["title", "description"],
        "search_price_min" : { "operator" : "__gte", "fields" : ["price"] },
        "search_price_max" : { "operator" : "__lte", "fields" : ["price"] },
        "search_onlyavailable" : { "fields" : ["status"], "custom_query": only_available_status_query_method },
    }

class ItemView(SearchListView):
    model = Item
    template_name = "alugueme/search.html"

    form_class = SearchItemForm
    filter_class = ItemFilter

@login_required(login_url='login')
def rents(request):
    rents = Rent.objects.filter(user=request.user)
    return render(request, 'alugueme/rents.html', {'rents': rents})
