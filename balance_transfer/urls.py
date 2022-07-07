"""balance_transfer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from balance_transfer.settings import DEBUG

schema_view = get_schema_view(
   openapi.Info(
      title="Transaction API",
      default_version='v1.0',
      description="Api description",
      contact=openapi.Contact(email="omar.iut.09@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=False,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('transaction.urls')),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
if DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]