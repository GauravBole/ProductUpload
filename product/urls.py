from .templates import index
from .views import ProductExcelUploadApiView, eventsource, ProductApiView

from django.urls import path

urlpatterns = [
    path('', index, name="products"),
    path('products/', ProductApiView.as_view(), name="products"),

    path('upload_file/', ProductExcelUploadApiView.as_view(), name="upload_products"),
    path('eventsource/<str:task_id>/', eventsource, name="event_source")
]