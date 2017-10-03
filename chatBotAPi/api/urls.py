from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^chat/$',
        views.chat_data,
        name="chat_data")
]