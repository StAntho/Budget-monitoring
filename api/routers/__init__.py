import pkgutil 
import importlib 
from fastapi import APIRouter 

all_routers = [] 

for module_info in pkgutil.iter_modules(__path__): 
    module_name = module_info.name 
    
    if module_name.startswith("_"): 
        continue 

    module = importlib.import_module(f"{__name__}.{module_name}") 
    
    if hasattr(module, "router"): 
        all_routers.append(module.router)