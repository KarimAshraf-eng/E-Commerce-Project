class Product:
    def __init__(self, productId: int, name: str, description: str, price: float, 
                 stockQuantity: int, supplierName: str = None):
        self.productId = productId
        self.name = name
        self.description = description
        self.price = price
        self.stockQuantity = stockQuantity
        self.supplierName = supplierName

    def updateStock(self, quantity: int):
        self.stockQuantity += quantity

    def to_dict(self):
        return {
            'productId': self.productId,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stockQuantity': self.stockQuantity,
            'supplierName': self.supplierName
        }