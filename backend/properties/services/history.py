# backend/properties/services/history.py
from elasticsearch import Elasticsearch
from django.conf import settings

def search_property_history(property_id, size=1000):
    query = {
        "query": {"term": {"property_id": property_id}},
        "sort": [{"deal_date": "desc"}],
        "size": size,
    }
    res = es.search(index="history", body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]
