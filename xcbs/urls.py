"""xcbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mal import views as mal_views
import sys
sys.setrecursionlimit(1000000)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',mal_views.index,name='index'),
    path('index',mal_views.index,name='index'),
    path('tree',mal_views.tree,name='tree'),
    path('tree2',mal_views.tree2,name='tree2'),
    path('detect',mal_views.detect,name='detect'),
    path('FileUploads',mal_views.FileUploads,name='FileUploads'),
    path('result',mal_views.result,name='result'),
]
