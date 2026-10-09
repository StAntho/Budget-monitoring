from langchain_core.documents import Document

def json_to_docs(payload):
    docs = []
    
    for row in payload["data"]:
        sub_keys = list(row.keys())
        qui = row.get("Qui") or row.get("Paiement")
        revenus = row.get("Revenus")
        depenses = row.get("Dépenses") or row.get("Prix")
        # dir_budg = 'Revenus' if 'Revenus' in row[val] else 'Dépenses'
        # value = row[val].get(dir_budg)
        cat = row.get("Catégorie") or row.get("Categorie")
        sub_cat = row.get("Column 10")
        sous_cat = row.get("Sous-catégorie") or row.get("Type")
        details = row.get("Détails") or row.get("Type")
        banque = row.get("Banque")
        # finalite = row[val].get("Finalité")
        # content = f"{sub_cat} {sous_cat} {details}"
        content = f"{sub_cat} {sous_cat} {details}"
        metadata = {"qui": qui, "revenus": revenus, "depenses": depenses, "categorie": cat, "sub_cat": sub_cat, "sous_cat": sous_cat, "details": details, "banque": banque}
        docs.append(Document(
            page_content=content,
            metadata=metadata 
        ))     
    return docs