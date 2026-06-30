import chromadb

client = chromadb.Client()
collection = client.create_collection("test")

collection.add(
    documents=["The Indian MSME market is worth 48 lakh crore"],
    ids=["doc1"]
)

results = collection.query(
    query_texts=["What is the MSME market size?"],
    n_results=1
)

print(results["documents"])