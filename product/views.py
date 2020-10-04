from django.shortcuts import render
from django.views.generic import View
import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from celery.result import AsyncResult
from django.http import StreamingHttpResponse
from .models import Product
from .tasks import products_upload
from .services import ProductService
# Create your views here.

class ProductApiView(View):

    def get(self, request):
        response = {"status": 500, "response_message": "Something went wrong.", "all_data": [], "recordsTotal": 0,
                    "recordsFiltered": 0, "draw": 0}
        start = request.GET.get("start") or 0
        length = request.GET.get("length") or 10
        draw = request.GET.get("draw") or 0
        search_query = request.GET.get("search[value]") or ""
        order = request.GET.get("order[0][dir]") or "asc"
        orderable_column = request.GET.get("order[0][column]")
        orderable_column_data = "updated_at"
        if order not in ["", None]:
            if orderable_column is not None:
                orderable_column_data = request.GET.get(f"columns[{int(orderable_column)}][data]")
        # actual_orderable_column = request.GET.get(f"columns[{int(orderable_column)}][data]")
        product_service_obj = ProductService()
        request_data = {"start": start, "length": length, "draw": draw, "search_query": search_query, "order": order,
                        "orderable_column": orderable_column, "orderable_column_data": orderable_column_data}
        data, draw, recordsTotal, recordsFiltered = product_service_obj.list_products(request_data)
        response["all_data"] = list(data)
        response["recordsTotal"] = recordsTotal
        response["recordsFiltered"] = recordsFiltered
        response["draw"] = draw
        response["status"] = 200
        response["response_message"] = "success"
        return JsonResponse(response, safe=False)

    def post(self, request):
        pass



class ProductExcelUploadApiView(View):

    def post(self, request):
        uploaded_file = request.FILES['user_file_upload']
        uploaded_file_ = (uploaded_file.name)
        os.getcwd()
        if not os.path.exists('media'):
            os.makedirs('media')
        os.chdir('media')
        path = default_storage.save(uploaded_file_, ContentFile(uploaded_file.read()))
        # uploaded_file.save(os.path.join(os.getcwd()+"/media/", uploaded_file_))
        task = products_upload.delay(path)
        print(task.id, "*"*100)
        return JsonResponse({"message": "success", "task_id": task.id})

def eventsource(request, task_id):
    response = StreamingHttpResponse(stream_generator(task_id), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    return response


def stream_generator(task_id):
    res = AsyncResult(task_id)
    print(res.info)
    # time.sleep(2)
    # while res.state == "done" or res.status == "fail":
    yield u'data: %s\n\n' % res.info