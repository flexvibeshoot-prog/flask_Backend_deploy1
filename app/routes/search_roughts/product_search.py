from flask import Blueprint,request,jsonify
from app.meilisearch_setup import index

search=Blueprint('search',__name__,url_prefix='/product')

@search.route("/search")
def search_product():
    try:
        return index.search(request.args.get("q", ""))["hits"]
    except:
        return []   # graceful fallback



@search.route("/products")
def search_products():
    query = request.args.get("q", "")  # empty allowed
    category = request.args.get("category")
    max_price = request.args.get("max_price")

    page = int(request.args.get("page", 1))
    limit = 10

    filters = []

    if category:
        filters.append(f'category = "{category}"')

    if max_price and max_price.isdigit():
        filters.append(f"price <= {int(max_price)}")

    result = index.search(query, {
        "filter": filters if filters else None,
        "limit": limit,
        "offset": (page - 1) * limit
    })

    return jsonify({
        "products": result["hits"],
        "total": result["estimatedTotalHits"],
        "page": page
    })



@search.route("/suggest")
def suggest():
    query = request.args.get("q", "")

    if len(query) < 2:
        return jsonify([])

    result = index.search(query, {
        "limit": 8,
        "attributesToRetrieve": ["name"],
        "attributesToHighlight": ["name"]
    })

    suggestions = [
        hit["_formatted"]["name"]
        for hit in result["hits"]
    ]
    return jsonify(suggestions)

