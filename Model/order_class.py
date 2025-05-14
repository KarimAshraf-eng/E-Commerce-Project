from datetime import date
from typing import List
from Model.orderItem_class import OrderItem

class Order:
    def __init__(self, orderId: int, orderDate: date, status: str, items: List[OrderItem]):
        self.orderId = orderId
        self.orderDate = orderDate
        self.status = status
        self.items = items
        self.totalAmount = sum(item.price for item in items)

    def placeOrder(self):
        self.status = "Placed"

    def cancelOrder(self):
      if self.status == "Cancelled":
          raise ValueError("Order is already cancelled")
          
      if self.status == "Shipped":
          raise ValueError("Cannot cancel shipped order")
      
      for item in self.items:
          item.product.stockQuantity += item.quantity
      
      self.status = "Cancelled"

    def trackOrder(self):
        return f"Order {self.orderId} is currently {self.status}"

    def to_dict(self):
        return {
            'orderId': self.orderId,
            'orderDate': str(self.orderDate),
            'status': self.status,
            'totalAmount': self.totalAmount
        }

    def items_to_dict(self):
        return [item.to_dict() for item in self.items]