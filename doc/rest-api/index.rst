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

   **Sample Response**:

   .. sourcecode:: http

      HTTP/1.0 202 Accepted
      Content-Type: application/json

   :statuscode 202: Accepted


