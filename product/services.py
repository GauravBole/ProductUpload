from .models import Product
from django.db.models import Q
import sys

class ProductService:
    def add_product_search_filter(self,product_obj,request_data):
        search_query = request_data['search_query']
        product_obj = product_obj.filter(
            Q(sku__icontains=search_query) |
            Q(name__icontains=search_query)
        )
        return product_obj
    def add_order_filter(self, product_obj, request_data):
        orderable_column_data, orderable_column, order = request_data.get('orderable_column_data')\
        , request_data.get('orderable_column'), request_data.get('order')

        if order not in ["", None]:
            if order == "asc":
                product_obj = product_obj.order_by(f'-{orderable_column_data}')
            else:
                product_obj = product_obj.order_by(f'{orderable_column_data}')
        else:
            product_obj = product_obj.order_by('id')
        return product_obj

    def list_products(self, request_data):
        draw, recordsTotal, recordsFiltered, data = request_data.get('draw'), 0, 0, []
        try:
            start, length = int(request_data.get('start')), int(request_data.get('length'))
            product_obj = Product.objects.all()
            recordsTotal = product_obj.count()

            product_obj = self.add_product_search_filter(product_obj, request_data)
            product_obj = self.add_order_filter(product_obj, request_data)

            recordsFiltered = product_obj.count()
            product_obj = product_obj[start: start + length]

            data = product_obj.values('sku', 'name', 'description')
        except Exception as e:
            
            print("Error in bank_list()")
            print("Line number of error is {}".format(sys.exc_info()[-1].tb_lineno), e)
        return data, draw, recordsTotal, recordsFiltered