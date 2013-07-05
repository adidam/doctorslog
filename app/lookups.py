#look ups for search functionality

from selectable.base import ModelLookup
from selectable.registry import registry
from app.models import Fruit
from django.contrib.auth.models import User

class FruitLookUp(ModelLookup):
    model = Fruit
    search_fields = ('name__icontains',)

registry.register(FruitLookUp)

#look up for User model
class UserLookup(ModelLookup):
    model = User
    search_fields = ('username__istartswith','first_name__istartswith','last_name__istartswith',)

    def get_item_label(self, item):
        return u"Dr %s " % item.get_full_name().capitalize()
    def get_item_value(self, item):
        return u"Dr %s " % item.get_full_name().capitalize()

registry.register(UserLookup)
