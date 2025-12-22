import json
import urllib.request
import urllib.error

from config import ES_HOST, CURRENT_INDEX_PREFIX, HISTORY_INDEX


def create_current_sink():
    """
    최신 상태(current) 인덱스용 Sink
    - index: realestate_current_{asset_type}
    - _id: property_id (UPSERT)
    - bulk flush 1: 이벤트마다 즉시 전송
    """

    def send(value):
        tag, doc = value
        if tag != "current":
            return value

        index = f"{CURRENT_INDEX_PREFIX}_{doc['asset_type'].lower()}"
        print(f"[ES SINK CALL] current index={index} id={doc.get('property_id')}")
        meta = {"index": {"_index": index, "_id": doc["property_id"]}}
        payload = "\n".join([
            json.dumps(meta, ensure_ascii=False),
            json.dumps(doc, ensure_ascii=False),
        ]) + "\n"

        try:
            req = urllib.request.Request(
                url=f"{ES_HOST}/_bulk",
                data=payload.encode("utf-8"),
                headers={"Content-Type": "application/x-ndjson"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
                try:
                    data = json.loads(body.decode('utf-8'))
                except Exception:
                    data = None

                # Bulk API may return 200 even when some items failed; check "errors" field
                if resp.status >= 300 or (isinstance(data, dict) and data.get('errors')):
                    print(f"[ES ERROR] status={resp.status} index={index} body={body}")
                else:
                    items = None
                    if isinstance(data, dict) and data.get('items'):
                        items = len(data.get('items'))
                    print(f"[ES BULK OK] index={index} status={resp.status} items={items}")
        except Exception as e:
            print(f"[ES ERROR] index={index} err={e}")

        return value

    return send


def create_history_sink():
    """
    히스토리(history) 인덱스용 Sink
    - index: realestate_history
    - append-only
    """

    def send(value):
        tag, doc = value
        if tag != "history":
            return value

        # history도 건물 기준으로 연결되도록 _id와 _routing을 property_id 기반으로 설정
        print(f"[ES SINK CALL] history index={HISTORY_INDEX} property_id={doc.get('property_id')}")
        hist_id = f"{doc.get('property_id')}|{doc.get('trade_fingerprint')}"
        # ES Bulk 메타데이터는 'routing' 키 사용 (ES 7.x)
        meta = {"index": {"_index": HISTORY_INDEX, "_id": hist_id, "routing": doc.get('property_id')}}
        payload = "\n".join([
            json.dumps(meta, ensure_ascii=False),
            json.dumps(doc, ensure_ascii=False),
        ]) + "\n"

        try:
            req = urllib.request.Request(
                url=f"{ES_HOST}/_bulk",
                data=payload.encode("utf-8"),
                headers={"Content-Type": "application/x-ndjson"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read()
                try:
                    data = json.loads(body.decode('utf-8'))
                except Exception:
                    data = None

                if resp.status >= 300 or (isinstance(data, dict) and data.get('errors')):
                    print(f"[ES ERROR] status={resp.status} index={HISTORY_INDEX} body={body}")
                else:
                    items = None
                    if isinstance(data, dict) and data.get('items'):
                        items = len(data.get('items'))
                    print(f"[ES BULK OK] index={HISTORY_INDEX} status={resp.status} items={items}")
        except urllib.error.HTTPError as e:
            try:
                body = e.read()
                print(f"[ES HTTP ERROR] status={e.code} index={HISTORY_INDEX} body={body}")
            except Exception:
                print(f"[ES ERROR] index={HISTORY_INDEX} err={e}")
        except Exception as e:
            print(f"[ES ERROR] index={HISTORY_INDEX} err={e}")

        return value

    return send
