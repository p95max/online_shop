from django.urls import path
from shop.views import (test)

app_name = 'shop'

urlpatterns = [
    path('test/', test, name='test'),

]