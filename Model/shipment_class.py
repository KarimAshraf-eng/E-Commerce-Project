from datetime import date
from Model.order_class import Order

class Shipment:
    def __init__(self, shipmentId: int, order: Order, shipmentDate: 'date', status: str):
        self.shipmentId = shipmentId
        self.order = order
        self.shipmentDate = shipmentDate
        self.status = status

    def updateStatus(self, newStatus: str):
        self.status = newStatus
        if newStatus.lower() in ['delivered', 'done']:
            self.order.status = "Delivered"
