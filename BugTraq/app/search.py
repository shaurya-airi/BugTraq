from app import app


def add_to_index(index, model):
    if not app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    app.elasticsearch.index(index=index, id=model.bug_id, body=payload)


def remove_from_index(index, model):
    if not app.elasticsearch:
        return
    app.elasticsearch.delete(index=index, id=model.bug_id)


def query_index(index, query):
    if not app.elasticsearch:
        return [], 0
    search = app.elasticsearch.search(
        index=index,
        body={'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*'],
                    'type': 'phrase_prefix'}
                    },
                'size': '200'
              })
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
