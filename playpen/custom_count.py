from common.products import Product_Def
import collections

product_query = collections.defaultdict(dict)

RHEL = 'RHEL Server'

product_query['name'] = RHEL
product_query[RHEL]['memory']['high']=[0, 8388608, '< 8GB']
product_query[RHEL]['memory']['low']=[8388609, -1, '> 8GB']
product_query[RHEL]['cpu']=[]
product_query[RHEL]['vcpu']=[]
product_query[RHEL]['socket']=[]



Product_Def.get_product_match_config()