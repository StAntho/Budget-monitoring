import json
import streamlit as st
import pandas as pd

_CSV_ENCODINGS = ["utf-8", "latin-1", "utf-8-sig", "cp1252"]               
_CSV_SEPARATORS = [",", ";", "\t", "|"] 

def detect_file_type(file):
    name = file.name.lower()
    if name.endswith(".csv"):
        return "csv"
    elif name.endswith(".xlsx"):
        return "xlsx"
    elif name.endswith(".json"):
        return "json"
    return None

def _read_csv(file):                                                       
    raw = file.read()                                                      
    for encoding in _CSV_ENCODINGS:                                        
        try:                                                               
            text = raw.decode(encoding)                                    
            # sniff separator on first line                                
            first_line = text.split("\n")[0]                               
            sep = max(_CSV_SEPARATORS, key=lambda s: first_line.count(s))  
            import io                                                      
            return pd.read_csv(io.StringIO(text), sep=sep)                 
        except (UnicodeDecodeError, Exception):                            
            continue                                                       
    st.error("Impossible de décoder le fichier CSV. Essayez de le convertir en UTF-8.")                                                               
    return None      

def load_file(file, file_type):
    try:
        if file_type == "csv":
            return _read_csv(file)
        elif file_type == "xlsx":
            return pd.read_excel(file)
        elif file_type == "json":
            data = json.load(file)
            return pd.json_normalize(data)
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None