# meili.py
from meilisearch import Client

client = Client(
    "https://meilisearch-render-l3jw.onrender.com",
    "f9Kp2XvL8ZqA1mWcR7eS0YH2"
)

index = client.index("products")
