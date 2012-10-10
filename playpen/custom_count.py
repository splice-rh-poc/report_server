from common.products import Product_Def
import collections

product_query = collections.defaultdict(dict)

name = 'RHEL Server'

product_query['name'] = name
product_query[name]['memory']=[0, 8388608, '< 8GB', 8388609, -1, '> 8GB']
product_query[name]['cpu']=[]
product_query[name]['vcpu']=[]
product_query[name]['socket']=[]

