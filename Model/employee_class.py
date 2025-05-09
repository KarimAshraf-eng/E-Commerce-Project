from Model.wareHouse_class import Warehouse
from Model.product_class import Product
from Model.order_class import Order

class Employee:
    def __init__(self, employeeId: int, name: str, role: str):
        self.employeeId = employeeId
        self.name = name
        self.role = role

    def manageInventory(self, warehouse: Warehouse, product: Product, action: str):
        if action == "add":
            warehouse.addProduct(product)
        elif action == "remove":
            warehouse.removeProduct(product.productId)

    def processOrder(self, order: Order):
      order.status = "Placed"
