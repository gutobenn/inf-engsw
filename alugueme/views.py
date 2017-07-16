# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import DeleteView, UpdateView
from search_views.filters import BaseFilter
from search_views.views import SearchListView
from templated_email import send_templated_mail

from alugueme.forms import ItemForm, RentForm, SearchItemForm, SignUpForm, AvaliationForm
from alugueme.models import Item, Rent, Profile, Avaliation


def index(request):
    items = Item.objects.filter(
        published_date__lte=timezone.now(),
        status=Item.AVAILABLE_STATUS).order_by('-published_date')[:12]
    return render(request, 'alugueme/index.html', {'items': items})

def check_due_date():
    rents = Rent.objects.filter(
        due_date__lte=timezone.now(),
        status=Rent.CONFIRMED_STATUS)
    for rent in rents:
        rent.status = Rent.DELAYED_STATUS
        user_profile = Profile.objects.get(user=rent.user)
        user_profile.can_rent = False # block user from renting more items
        rent.save()
        user_profile.save()
        send_templated_mail(
            template_name='rent_due',
            from_email='alugueme@florescer.xyz',
            recipient_list=[rent.user.email],
            context={
                'item': rent.item,
                'first_name': rent.user.first_name,
            })


@login_required(login_url='login')
def items_my(request):
    items = Item.objects.filter(owner=get_user(request)).order_by('published_date')
    user_profile = Profile.objects.get(user=get_user(request))
    return render(request, 'alugueme/items_my.html', {'items': items, 'owner':user_profile})


@login_required(login_url='login')
def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = get_user(request)
            owner_profile = Profile.objects.get(user=get_user(request))
            #check if owner has reached limit of announcements
            if owner_profile.number_of_items < owner_profile.MAXITEMS:
                owner_profile.number_of_items += 1
                owner_profile.save()
                item.published_date = timezone.now()
                item.save()
                messages.success(request, 'Item cadastrado com sucesso!')
                return redirect('item_detail', pk=item.pk)
            else:
                messages.error(request, 'Você atingiu o limite de anúncios ativos.')
    else:
        form = ItemForm()
    return render(request, 'alugueme/item_edit.html',
                  {'form': form,
                   'title': 'Cadastrar Item'})

@login_required(login_url='login')
def item_act_deact(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.status == Item.INACTIVE_STATUS:
        # check if user has not reached item limit
        owner = Profile.objects.get(user=item.owner)
        if owner.number_of_items < owner.MAXITEMS:
            owner.number_of_items += 1
            owner.save()
            item.status = Item.AVAILABLE_STATUS
            item.save()
            messages.success(request, 'Item reativado com sucesso!')
        else:
            messages.error(request, 'Você já atingiu o limite de itens anunciados.')
    else:
        if item.status == Item.UNAVAILABLE_STATUS:  # Item alugado
            messages.error(
                request,
                'Não é possível desativar um item enquanto ele está com outra pessoa!'
            )
        else:
            item.status = Item.INACTIVE_STATUS
            item.save()
            # change user items
            owner = Profile.objects.get(user=item.owner)
            owner.number_of_items -= 1
            owner.save()
            # Cancel rent requests for item
            other_rent_requests = Rent.objects.filter(
                item=item, status=Rent.PENDING_STATUS)
            for rent_request in other_rent_requests:
                rent_request.status = Rent.CANCELLED_STATUS
                rent_request.save()
                send_templated_mail(
                    template_name='rent_canceled_item_removed',
                    from_email='alugueme@florescer.xyz',
                    recipient_list=[rent_get_user(request).email],
                    context={
                        'item': rent_request.item,
                        'first_name': rent_request.user.first_name,
                    })
            messages.success(request, 'Item desativado com sucesso! Você pode anunciar outro item agora.')

    return redirect('items_my')


@login_required(login_url='login')
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if get_user(request) != item.owner:
        return redirect('index')

    if item.status == Item.UNAVAILABLE_STATUS:  # Item alugado
        messages.error(
            request,
            'Não é possível editar um item enquanto ele está com outra pessoa!'
        )
        return redirect('item_detail', pk=item.pk)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = get_user(request)
            item.published_date = timezone.now()
            item.save()
            # Cancel rent requests for item
            other_rent_requests = Rent.objects.filter(
                item=item, status=Rent.PENDING_STATUS)
            for rent_request in other_rent_requests:
                rent_request.status = Rent.CANCELLED_STATUS
                rent_request.save()
                send_templated_mail(
                    template_name='rent_canceled_item_edited',
                    from_email='alugueme@florescer.xyz',
                    recipient_list=[rent_get_user(request).email],
                    context={
                        'item': rent_request.item,
                        'first_name': rent_request.user.first_name,
                    })
            messages.success(request, 'Item alterado com sucesso!')
            return redirect('item_detail', pk=item.pk)
    else:
        item_rent_requests = Rent.objects.filter(
            item=item, status=Rent.PENDING_STATUS)
        form = ItemForm(instance=item)
        return render(request, 'alugueme/item_edit.html', {
            'form': form,
            'title': 'Editar Item',
            'item_rent_requests': item_rent_requests
        })
    return render(request, 'alugueme/item_edit.html',
                  {'form': form,
                   'title': 'Editar Item'})


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    avaliations = Avaliation.objects.filter(rent__item=item).exclude(user=item.owner)
    if request.method == "POST":
        form = RentForm(request.POST)
        if form.is_valid():
            rent = form.save(commit=False)
            rent.user = get_user(request)
            user_profile = Profile.objects.get(user=rent.user)
            if user_profile.can_rent: # check if user is blocked from delaying items
                rent.item = item
                rent.status = rent.PENDING_STATUS
                rent.request_date = timezone.now()
                rent.save()
                send_templated_mail(
                    template_name='rent',
                    from_email='alugueme@florescer.xyz',
                    recipient_list=[item.owner.email],
                    context={
                        'item': item,
                        'first_name': item.owner.first_name,
                        'rent_user': request.user.first_name
                    })
                messages.success(
                    request,
                    'Pedido realizado com sucesso! Assim que o dono do item avaliá-lo, te enviaremos um e-mail.'
                )
                return redirect('item_detail', pk=item.pk)
            else:
                messages.error(request, 'Você tem itens atrasados, normalize sua situação para fazer novos aluguéis.')

    else:
        if request.user.is_authenticated:
            if Rent.objects.filter(
                    user=get_user(request), item=item,
                    status=Rent.PENDING_STATUS).exists():
                return render(request, 'alugueme/item_detail.html',
                              {'item': item,
                               'alreadyrequested': True,
                               'avaliations': avaliations})
            elif item.status == item.AVAILABLE_STATUS and item.owner != get_user(request):
                form = RentForm()
                return render(request, 'alugueme/item_detail.html',
                              {'item': item,
                               'form': form})
    return render(request, 'alugueme/item_detail.html', {'item': item, 'avaliations': avaliations})

@login_required(login_url='login')
def view_profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    items = Item.objects.filter(owner=user).order_by('published_date')
    avaliations_as_owner = Avaliation.objects.filter(rent__item__owner=user).exclude(user=user)
    avaliations_as_renter = Avaliation.objects.filter(rent__user=user).exclude(user=user)
    args = {'user': user, 'items': items, 'avaliations_as_owner': avaliations_as_owner, 'avaliations_as_renter': avaliations_as_renter}
    return render(request, 'alugueme/profile.html', args)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.course = form.cleaned_data.get('course')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, 'Bem-vindo, {0}!'.format(user.first_name))
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'alugueme/signup.html', {'form': form})


class ItemFilter(BaseFilter):
    def only_available_status_query_method(model_field, request_field_value,
                                           params_dict):
        return Q(status__lte=Item.AVAILABLE_STATUS)

    search_fields = {
        "search_text": ["title", "description"],
        "search_price_min": {
            "operator": "__gte",
            "fields": ["price"]
        },
        "search_price_max": {
            "operator": "__lte",
            "fields": ["price"]
        },
        "search_onlyavailable": {
            "fields": ["status"],
            "custom_query": only_available_status_query_method
        },
    }


class ItemView(SearchListView):
    model = Item
    template_name = "alugueme/search.html"

    form_class = SearchItemForm
    filter_class = ItemFilter


@login_required(login_url='login')
def rents(request):
    my_rent_requests = Rent.objects.filter(
        user=get_user(request), status=Rent.PENDING_STATUS)
    my_current_rents = Rent.objects.filter(
        user=get_user(request), status=Rent.CONFIRMED_STATUS)
    my_past_rents = Rent.objects.filter(
        user=get_user(request), status=Rent.ENDED_STATUS)
    my_items_rent_requests = Rent.objects.filter(
        item__owner=get_user(request), status=Rent.PENDING_STATUS)
    my_items_current_rents = Rent.objects.filter(
        item__owner=get_user(request), status=Rent.CONFIRMED_STATUS) | Rent.objects.filter(item__owner=get_user(request), status=Rent.DELAYED_STATUS)
    my_items_past_rents = Rent.objects.filter(
        item__owner=get_user(request), status=Rent.ENDED_STATUS)
    my_delayed_rents = Rent.objects.filter(
        user=get_user(request), status=Rent.DELAYED_STATUS)

    user_profile = Profile.objects.get(user=get_user(request))

    return render(request, 'alugueme/rents.html', {
        'my_rent_requests': my_rent_requests,
        'my_current_rents': my_current_rents,
        'my_past_rents': my_past_rents,
        'my_items_rent_requests': my_items_rent_requests,
        'my_items_current_rents': my_items_current_rents,
        'my_items_past_rents': my_items_past_rents,
        'my_delayed_rents': my_delayed_rents,
        'payment_choices': Rent.PAYMENT_CHOICES,
        'user_profile':user_profile
    })

@login_required(login_url='login')
def rent_cancel(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and get_user(request) == rent.user:
        rent.status = Rent.CANCELLED_STATUS
        rent.save()
        messages.success(request, 'Pedido cancelado')
        return redirect('rents')
    else:
        raise Http404


@login_required(login_url='login')
def rent_accept(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    # less verbose version of rent reject to be used inside rent_accept
    def rent_reject(request, rent):
        if request.method == "POST" and get_user(request) == rent.item.owner:
            rent.status = Rent.CANCELLED_STATUS
            rent.save()
            send_templated_mail(
                template_name='rent_rejected_automatic',
                from_email='alugueme@florescer.xyz',
                recipient_list=[rent.user.email],
                context={
                    'item': rent.item,
                    'first_name': rent.user.first_name,
                    'item_owner': request.user.first_name
                })
        else:
            raise Http404


    if request.method == "POST" and get_user(request) == rent.item.owner:
        rent_user_profile = Profile.objects.get(user=rent.user)
        # check if renting user has not reached rent limit
        if rent_user_profile.number_of_rents < rent_user_profile.MAXRENTS:
            # check if renting user has no delayed items
            # there are cases where the rent request was made before the user got blocked
            # so this test must be made here
            if rent_user_profile.can_rent:
                rent_user_profile.number_of_rents += 1
                rent.status = Rent.CONFIRMED_STATUS
                rent.confirmation_date = timezone.now()

                rent.due_date = rent.confirmation_date + timedelta(days=rent.months*30) # timedelta only works with day
                #rent.due_date = timezone.now() # <- test case for delayed item
                rent.item.status = Item.UNAVAILABLE_STATUS
                rent.item.save()
                rent_user_profile.save()
                rent.save()

                # Cancel other rent requests for same item
                other_rent_requests = Rent.objects.filter(
                    item=rent.item, status=Rent.PENDING_STATUS)
                for rent_request in other_rent_requests:
                    rent_request.status = Rent.CANCELLED_STATUS
                    rent_request.save()
                    send_templated_mail(
                        template_name='rent_canceled',
                        from_email='alugueme@florescer.xyz',
                        recipient_list=[rent_request.user.email],
                        context={
                            'item': rent_request.item,
                            'first_name': rent_request.user.first_name,
                        })

                send_templated_mail(
                    template_name='rent_accepted',
                    from_email='alugueme@florescer.xyz',
                    recipient_list=[rent.user.email],
                    context={
                        'item': rent.item,
                        'first_name': rent.user.first_name,
                        'item_owner': request.user.first_name
                    })
                messages.success(request, 'Pedido aceito')
                return redirect('rents')
            else: # renting user is blocked
                messages.error(request, "Transação cancelada. O usuário que solicitou seu item está temporariamente suspenso. Pedido será cancelado automaticamente.")
                rent_reject(request, rent)
                return redirect('rents')
        else:
            messages.error(request, "Transação cancelada. O usuário que solicitou seu item atingiu o limite de itens alugados. Pedido será cancelado automaticamente.")
            rent_reject(request, rent)
            return redirect('rents')

    else:
        raise Http404


@login_required(login_url='login')
def rent_terminate(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and get_user(request) == rent.item.owner:
        rent_user_profile = Profile.objects.get(user=rent.user)
        rent.status = Rent.ENDED_STATUS
        rent.due_date = timezone.now()
        rent.item.status = Item.AVAILABLE_STATUS
        rent_user_profile.number_of_rents -= 1
        rent.save()
        rent_user_profile.save()
        rent.item.save()

        # check if rent_user has any other delayed item
        if Rent.objects.filter(due_date__lte=timezone.now(), user=rent.user).count() == 0:
            rent_user_profile.can_rent = True
        else:
            rent_user_profile.can_rent = False

        send_templated_mail(
            template_name='rent_rate',
            from_email='alugueme@florescer.xyz',
            recipient_list=[rent.user.email],
            context={
                'item': rent.item,
                'first_name': rent.user.first_name,
                'rent': rent
            })

        messages.success(request, 'Seu aluguel foi finalizado com sucesso. Por favor, avalie o seu aluguel!')
        return redirect('rent_rate', pk=rent.pk)
    else:
        raise Http404

@login_required(login_url='login')
def rent_reject(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if request.method == "POST" and get_user(request) == rent.item.owner:
        rent.status = Rent.CANCELLED_STATUS
        rent.save()
        send_templated_mail(
            template_name='rent_rejected',
            from_email='alugueme@florescer.xyz',
            recipient_list=[rent.user.email],
            context={
                'item': rent.item,
                'first_name': rent.user.first_name,
                'item_owner': request.user.first_name
            })
        messages.success(request, 'Pedido rejeitado')
        return redirect('rents')
    else:
        raise Http404

@login_required(login_url='login')
def rent_rate(request, pk):
    rent = get_object_or_404(Rent, pk=pk)

    if not (get_user(request) == rent.user or get_user(request) == rent.item.owner):
        raise Http404

    if Avaliation.objects.filter(user=get_user(request), rent=rent).count() > 0:
        messages.error(request, 'Você já avaliou esse aluguel!')
        return redirect('rents')

    if request.method == "POST":
        form = AvaliationForm(request.POST)
        if form.is_valid():
            avaliation = form.save(commit=False)
            avaliation.rent = rent
            avaliation.user = get_user(request)
            avaliation.save()
            messages.success(request, 'Aluguel avaliado com sucesso')
            return redirect('rents')
    else:
        form = AvaliationForm()
    return render(request, 'alugueme/rent_rate.html', {'form': form, 'item': rent.item})
