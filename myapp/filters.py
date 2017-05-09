import django_filters
from myapp.models import Item

class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = {'price': ['lt', 'gt']}
