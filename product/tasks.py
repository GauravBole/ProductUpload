from celery import shared_task, current_task
from django.db.models import Q
from functools import reduce
import pandas as pd
import os
from .models import Product

@shared_task(bind=True)
def products_upload(self, file_path):
    # try:
    os.getcwd()
    os.chdir('media')
    df = pd.read_csv(file_path)
    df['sku'] = df['sku'].apply(lambda x: x.lower())

    unique_values = df.drop_duplicates(subset=['sku'], keep="first")
    duplicate_values = df[df.duplicated(subset=['sku'], keep="first")]
    intervals = 500
    final = [unique_values[i * intervals:(i + 1) * intervals] for i in
            range((len(unique_values) + intervals - 1) // intervals)]
    current_task.update_state(state="PROGRESS_STATE",
                            meta={
                                    "message": "{0} duplicate products (SKU) found in a uploaded csv".format({len(duplicate_values)})
                            })
    for ind, i in enumerate(final):
        # print(i['sku'])
        current_task.update_state(state="PROGRESS_STATE",
                                meta={
                                    "message": "pass {0} - 500 products new product uploadding".format(
                                        {ind})
                                })
        q_list = map(lambda n: Q(sku__iexact=n), i['sku'])

        q_list = reduce(lambda a, b: a | b, q_list)

        gb = Product.objects.filter(q_list)
        create_obj = []
        for d in gb:
            
            update_required = unique_values.loc[unique_values['sku'] == d.sku]
            duplicate_values.append(update_required)
            # print(unique_values.head())
            i.drop(i[i['sku'] == d.sku].index, inplace=True)
            # print(d.sku)
        # create_value = unique_values.dict()
        print(i.to_dict('records'))
        for l in i.to_dict('records'):
            create_obj.append(Product(**l))
        Product.objects.bulk_create(create_obj)
        current_task.update_state(state="PROGRESS_STATE",
                            meta={
                                "message": "pass {0} - 500 new products compleated".format(
                                    {ind})
                            })
    final_dup = [duplicate_values.to_dict('records')[i * intervals:(i + 1) * intervals] for i in
            range((len(duplicate_values) + intervals - 1) // intervals)]
    
    for ind, i in enumerate(final_dup):
        current_task.update_state(state="PROGRESS_STATE",
                                meta={
                                    "message": "pass {0} - 500 old products updating".format(
                                        {ind})
                                })
        existing_products_set = {}
        all_sku = [j['sku'] for j in i]
        all_products = Product.objects.filter(sku__in=all_sku)
        for prod in all_products:
            existing_products_set[prod.sku] = prod
        
        update_obj = []
        for u in i:
            if u['sku'] in existing_products_set:
                product_obj = existing_products_set[u['sku']]
                product_obj.name = u['name']
                product_obj.discription = u['description']
                update_obj.append(product_obj)
    
        Product.objects.bulk_update(update_obj, ['sku', 'name', 'description'])
        current_task.update_state(state="PROGRESS_STATE",
                                meta={
                                    "message": "pass {0} - 500 old products compleated".format(
                                        {ind})
                                })
    # except Exception as e:
    #     print(e)
    #     current_task.update_state(state="FAIL",
    #                                 meta={
    #                                     "message": "Task Fail"
    #                                 })
                
    #     return "fail"
    return "done"

