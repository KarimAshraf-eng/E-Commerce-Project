from Model.product_class import Product

class Supplier:
    def __init__(self, supplierId: int, name: str, contact: str):
        self.supplierId = supplierId
        self.name = name
        self.contact = contact

    def supplyProduct(self, product: Product, quantity: int):
        product.updateStock(quantity)
        product.supplierName = self.name
