from Model.product_class import Product
from typing import List

class Inventory:
    def __init__(self, inventoryId: int):
        self.inventoryId = inventoryId
        self.products: List[Product] = []

    def addProduct(self, product: Product):
        self.products.append(product)

    def removeProduct(self, productId: int):
        self.products = [p for p in self.products if p.productId != productId]

    def checkStock(self, productId: int):
        for product in self.products:
            if product.productId == productId:
                return product.stockQuantity
        return 0
