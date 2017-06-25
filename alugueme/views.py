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
from django.views.generic import DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from templated_email import send_templated_mail

def index(request):
    items = Item.objects.filter(published_date__lte=timezone.now(), status=Item.AVAILABLE_STATUS).order_by('-published_date')[:12]
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

    if item.status == Item.UNAVAILABLE_STATUS: # Item alugado
        messages.error(request, 'Não é possível editar um item enquanto ele está com outra pessoa!')
        return redirect('item_detail', pk=item.pk)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.published_date = timezone.now()
            item.save()
            # Cancel rent requests for item
            other_rent_requests = Rent.objects.filter(item=item, status=Rent.PENDING_STATUS)
            for rent_request in other_rent_requests:
                rent_request.status = Rent.CANCELLED_STATUS
                rent_request.save()
                send_templated_mail(
                    template_name='rent_canceled_item_edited',
                    from_email='alugueme@florescer.xyz',
                    recipient_list=[rent_request.user.email],
                    context={
                        'item':rent_request.item,
                        'first_name':rent_request.user.first_name,
                })
            messages.success(request, 'Item alterado com sucesso!')
            return redirect('item_detail', pk=item.pk)
    else:
        item_rent_requests = Rent.objects.filter(item=item, status=Rent.PENDING_STATUS)
        form = ItemForm(instance=item)
        return render(request, 'alugueme/item_edit.html', {'form': form, 'title': 'Editar Item', 'item_rent_requests': item_rent_requests})
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
            send_templated_mail(
                template_name='rent',
                from_email='alugueme@florescer.xyz',
                recipient_list=[item.owner.email],
                context={
                    'item':item,
                    'first_name':item.owner.first_name,
                    'rent_user':request.user.first_name
            })
            messages.success(request, 'Pedido realizado com sucesso! Assim que o dono do item avaliá-lo, te enviaremos um e-mail.')
            return redirect('item_detail', pk=item.pk )
    else:
        if request.user.is_authenticated:
            if Rent.objects.filter(user=request.user, item=item, status=Rent.PENDING_STATUS).exists():
                return render(request, 'alugueme/item_detail.html', {'item': item, 'alreadyrequested': True})
            elif item.status == item.AVAILABLE_STATUS and item.owner != request.user :
                form = RentForm()
                return render(request, 'alugueme/item_detail.html', {'item': item, 'form': form})
    return render(request, 'alugueme/item_detail.html', {'item': item})

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
    my_rents = Rent.objects.filter(user=request.user, status=Rent.PENDING_STATUS)
    my_current_rents = Rent.objects.filter(user=request.user, status=Rent.CONFIRMED_STATUS)
    rents_my_items = Rent.objects.filter(item__owner=request.user, status=Rent.PENDING_STATUS)

    for rent in my_current_rents:
        rent.return_date = rent.confirmation_date
        # TODO set correct return date
        # TODO fazer assim ou criar um campo para data de devolucao no model?
        # Além disso, o relative delta leva em conta a quantida de dias do mes para calcular. É assim mesmo que queremos?

    return render(request, 'alugueme/rents.html', {'my_rents': my_rents, 'rents_my_items': rents_my_items, 'my_current_rents': my_current_rents, 'payment_choices': Rent.PAYMENT_CHOICES})

@login_required(login_url='login')
def rent_cancel(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and request.user == rent.user:
        rent.status = Rent.CANCELLED_STATUS
        rent.save()
        messages.success(request, 'Pedido cancelado')
        return redirect('rents')
    else:
        raise Http404

@login_required(login_url='login')
def rent_accept(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and request.user == rent.item.owner:
        rent.status = Rent.CONFIRMED_STATUS
        rent.confirmation_date = timezone.now() # TODO usar date.today() ? E se a troca não for feita no dia? a data de devolucao vai ficar errada
        rent.item.status = Item.UNAVAILABLE_STATUS
        rent.item.save()
        rent.save()

        # Cancel other rent requests for same item
        other_rent_requests = Rent.objects.filter(item=rent.item, status=Rent.PENDING_STATUS)
        for rent_request in other_rent_requests:
            rent_request.status = Rent.CANCELLED_STATUS
            rent_request.save()
            send_templated_mail(
                template_name='rent_canceled',
                from_email='alugueme@florescer.xyz',
                recipient_list=[rent_request.user.email],
                context={
                    'item':rent_request.item,
                    'first_name':rent_request.user.first_name,
            })

        send_templated_mail(
            template_name='rent_accepted',
            from_email='alugueme@florescer.xyz',
            recipient_list=[rent.user.email],
            context={
                'item':rent.item,
                'first_name':rent.user.first_name,
                'item_owner':request.user.first_name
        })
        messages.success(request, 'Pedido aceito')
        return redirect('rents')
    else:
        raise Http404

@login_required(login_url='login')
def rent_reject(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and request.user == rent.item.owner:
        rent.status = Rent.CANCELLED_STATUS
        rent.save()
        send_templated_mail(
            template_name='rent_rejected',
            from_email='alugueme@florescer.xyz',
            recipient_list=[rent.user.email],
            context={
                'item':rent.item,
                'first_name':rent.user.first_name,
                'item_owner':request.user.first_name
        })
        messages.success(request, 'Pedido rejeitado')
        return redirect('rents')
    else:
        raise Http404
