from Model.product_class import Product

class OrderItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
        self.price = product.price * quantity
    
    def to_dict(self):
        return {
            'productId': self.product.productId,
            'quantity': self.quantity,
            'price': self.price
        }