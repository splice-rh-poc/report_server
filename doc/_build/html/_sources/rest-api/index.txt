REST API
========

.. toctree::
   :maxdepth: 2

.. http:post:: /api/v1/productusage/

   Import product usage into the report server.

   **Sample Request**:

   .. sourcecode:: http

      POST /api/v1/productusage/ HTTP/1.1
      Host: example.com
      Accept: application/json

      [
         {
            "splice_server" : "splice_server_uuid-1",
            "allowed_product_info" : [
               "69"
            ],
            "unallowed_product_info" : [ ],
            "facts" : {
               "lscpu_dot_cpu(s)" : "1",
               "memory_dot_memtotal" : "604836",
               "lscpu_dot_cpu_socket(s)" : "1"
            },
            "instance_identifier" : "12:31:3D:08:40:00",
            "date" : ISODate("2012-10-26T02:00:00Z"),
            "consumer" : "8d401b5e-2fa5-4cb6-be64-5f57386fda86"
         }
         {
            "splice_server" : "splice_server_uuid-1",
            "allowed_product_info" : [
               "69",
               "183"
            ],
            "unallowed_product_info" : [ ],
            "facts" : {
               "lscpu_dot_cpu(s)" : "1",
               "memory_dot_memtotal" : "604836",
               "lscpu_dot_cpu_socket(s)" : "1"
            },
            "instance_identifier" : "12:31:3D:08:40:00",
            "date" : ISODate("2012-10-26T02:00:00Z"),
            "consumer" : "fea363f5-af37-4a23-a2fd-bea8d1fff9e8"
         }
      ]

   **Sample Response**:

   .. sourcecode:: http

      HTTP/1.0 202 Accepted
      Content-Type: application/json

   :statuscode 202: Accepted


