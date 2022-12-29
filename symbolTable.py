class SymbolItem:

    def __init__(self, type, value, scopeLevel: int = 0):
        self.type = type
        self.value = value
        self.scopeLevel = scopeLevel
    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type
    
    def get_value(self):
        return self.value
    
    def set_value(self,value):
        self.value = value

class SymbolTable:
    def __init__(self):
        self.table = [{}] # a stack of dicts
    
    def enterScope(self):
        self.table.append({})

    def exitScope(self):
        self.table.pop()

    def addGlobal(self, name: str, item: SymbolItem):
        if name in self.table[0].keys():
            raise Exception("global name item exist")
        item.scopeLevel = 0
        print(name)
        self.table[0][name] = item
    
    def addLocal(self, name: str, item: SymbolItem):
        if name in self.table[-1].keys():
            raise Exception("local name item exist")
        item.scopeLevel = self.get_current_level()
        self.table[-1][name] = item

    def getSymbolItem(self, name: str):
        for i in range(self.get_current_level(), -1, -1):
            if name in self.table[i].keys():
                return self.table[i][name]
        raise Exception(f"no item {name} in symbol item")

    def setSymbolItem(self, name: str, value):
        for i in range(self.get_current_level(), -1, -1):
            if name in self.table[i].keys():
                self.table[i][name].set_value(value)
                return
        raise Exception(f"no item {name} in symbol item")

    def get_current_level(self):
        return len(self.table) - 1