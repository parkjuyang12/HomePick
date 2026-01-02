# backend/properties/services/history.py
import os
from elasticsearch import Elasticsearch
from django.conf import settings

ES_HOST = os.environ.get("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
es = Elasticsearch(ES_HOST)


def format_deal_date(value):
    if not value:
        return None
    value = str(value).strip()
    if value.isdigit():
        if len(value) == 8:
            return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
        if len(value) == 6:
            return f"{value[0:4]}-{value[4:6]}"
    return value


def normalize_price(row):
    if not row:
        return None
    price = row.get("price") or row.get("deal_amount") or row.get("amount")
    if price is None:
        return None
    if isinstance(price, (int, float)):
        return price
    value = str(price).strip().replace(",", "")
    try:
        return int(value)
    except ValueError:
        return price

def search_property_history(property_id, size=1000):
    property_id = property_id.rstrip(".")
    query = {
        "query": {"term": {"property_id.keyword": property_id}},
        "sort": [{"deal_date": "desc"}],
        "size": size,
    }
    res = es.search(index="realestate_history", body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]
