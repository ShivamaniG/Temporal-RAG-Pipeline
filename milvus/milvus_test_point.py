from pymilvus import connections, Collection, DataType

connections.connect(alias="default", host="localhost", port="19530")

collection_name = "doc_chunks"
collection = Collection(name=collection_name)

schema = collection.schema

print("Collection name:", collection.name)
print("Description:", schema.description)

for field in schema.fields:
    print(f"Field name: {field.name}")
    print(f" - DataType: {field.dtype}")
    print(f" - Is primary key: {field.is_primary}")
    print(f" - Auto id: {field.auto_id}")
    if field.dtype == DataType.FLOAT_VECTOR:
        print(f" - Dimension: {field.dim}")
    print()
