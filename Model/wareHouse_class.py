from Model.inventory_class import Inventory
from Model.product_class import Product

class Warehouse:
    def __init__(self, warehouseId: int, location: str, capacity: int):
        self.warehouseId = warehouseId
        self.location = location
        self.capacity = capacity
        self.inventory = Inventory(inventoryId=warehouseId)

    def addProduct(self, product: Product):
        self.inventory.addProduct(product)

    def removeProduct(self, productId: int):
        self.inventory.removeProduct(productId)

    def updateStock(self, productId: int, quantity: int):
        for product in self.inventory.products:
            if product.productId == productId:
                product.updateStock(quantity)
