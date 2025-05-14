import sqlite3
from datetime import date
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_name: str = "warehouse.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stockQuantity INTEGER NOT NULL,
            supplierName TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplierId INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            orderId INTEGER PRIMARY KEY,
            orderDate TEXT NOT NULL,
            status TEXT NOT NULL,
            totalAmount REAL NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            itemId INTEGER PRIMARY KEY AUTOINCREMENT,
            orderId INTEGER NOT NULL,
            productId INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (orderId) REFERENCES orders(orderId),
            FOREIGN KEY (productId) REFERENCES products(productId)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipments (
            shipmentId INTEGER PRIMARY KEY,
            orderId INTEGER NOT NULL,
            shipmentDate TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (orderId) REFERENCES orders(orderId)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS supply_records (
            recordId INTEGER PRIMARY KEY AUTOINCREMENT,
            productId INTEGER NOT NULL,
            productName TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            supplierName TEXT NOT NULL,
            supplyDate TEXT NOT NULL,
            FOREIGN KEY (productId) REFERENCES products(productId)
        )
        ''')
        
        self.conn.commit()

    def add_product(self, product: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO products (productId, name, description, price, stockQuantity, supplierName)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (product['productId'], product['name'], product['description'], 
              product['price'], product['stockQuantity'], product.get('supplierName', None)))
        self.conn.commit()

    def get_all_products(self) -> List[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('SELECT * FROM products')
      columns = [column[0] for column in cursor.description]
      return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_max_order_id(self):
      cursor = self.conn.cursor()
      cursor.execute('SELECT MAX(orderId) FROM orders')
      result = cursor.fetchone()[0]
      return result if result is not None else 0

    def get_max_shipment_id(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT MAX(shipmentId) FROM shipments')
        result = cursor.fetchone()[0]
        return result if result is not None else 0

    def get_max_supplier_id(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT MAX(supplierId) FROM suppliers')
        result = cursor.fetchone()[0]
        return result if result is not None else 0
      
    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('SELECT * FROM orders WHERE orderId = ?', (order_id,))
      row = cursor.fetchone()
      if row:
          columns = [column[0] for column in cursor.description]
          return dict(zip(columns, row))
      return None
    
    def get_shipment(self, shipment_id: int) -> Optional[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('''
      SELECT 
          s.shipmentId,
          s.orderId,
          s.shipmentDate,
          s.status,
          o.orderDate,
          o.totalAmount
      FROM shipments s
      JOIN orders o ON s.orderId = o.orderId
      WHERE s.shipmentId = ?
      ''', (shipment_id,))
      row = cursor.fetchone()
      if row:
          columns = [column[0] for column in cursor.description]
          return dict(zip(columns, row))
      return None

    def update_shipment_status(self, shipment_id: int, new_status: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE shipments 
        SET status = ?
        WHERE shipmentId = ?
        ''', (new_status, shipment_id))
        self.conn.commit()
        
    def is_valid_shipment_status(self, status: str) -> bool:
      valid_statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
      return status.capitalize() in valid_statuses
    
    def get_shipment_status(self, shipment_id: int) -> Optional[str]:
      cursor = self.conn.cursor()
      cursor.execute('SELECT status FROM shipments WHERE shipmentId = ?', (shipment_id,))
      result = cursor.fetchone()
      return result[0] if result else None
    
    def remove_product(self, product_id: int):
      cursor = self.conn.cursor()
      
      cursor.execute('SELECT productId FROM products WHERE productId = ?', (product_id,))
      if not cursor.fetchone():
          raise ValueError(f"Product with ID {product_id} does not exist")
      
      cursor.execute('DELETE FROM products WHERE productId = ?', (product_id,))
      self.conn.commit()
      
      self._cleanup_after_product_deletion(product_id)

    def _cleanup_after_product_deletion(self, product_id: int):
        cursor = self.conn.cursor()
        
        cursor.execute('DELETE FROM order_items WHERE productId = ?', (product_id,))
        
        cursor.execute('DELETE FROM supply_records WHERE productId = ?', (product_id,))
        
        self.conn.commit()
    
    def cancel_order(self, order_id: int, update_memory: bool = False):
      cursor = self.conn.cursor()
      returned_quantities = {}
      
      try:
          self.conn.execute("BEGIN TRANSACTION")
          
          cursor.execute('SELECT status FROM orders WHERE orderId = ?', (order_id,))
          result = cursor.fetchone()
          
          if not result:
              raise ValueError(f"Order {order_id} not found")
              
          current_status = result[0]
          
          if current_status == "Cancelled":
              raise ValueError(f"Order {order_id} is already cancelled")
              
          if current_status == "Shipped":
              raise ValueError(f"Cannot cancel shipped order {order_id}")
          
          cursor.execute('''
          SELECT productId, quantity 
          FROM order_items 
          WHERE orderId = ?
          ''', (order_id,))
          items = cursor.fetchall()
          
          if not items:
              raise ValueError(f"No items found for order {order_id}")
          
          for product_id, quantity in items:
              cursor.execute('''
              UPDATE products 
              SET stockQuantity = stockQuantity + ?
              WHERE productId = ?
              ''', (quantity, product_id))
              returned_quantities[product_id] = quantity
          
          cursor.execute('''
          UPDATE orders 
          SET status = 'Cancelled'
          WHERE orderId = ?
          ''', (order_id,))
          
          self.conn.commit()
          return returned_quantities if update_memory else None
          
      except Exception as e:
          self.conn.rollback()
          raise e

    def get_order_items_with_products(self, order_id: int):
      cursor = self.conn.cursor()
      cursor.execute('''
      SELECT 
          oi.productId,
          oi.quantity,
          p.name as productName,
          p.stockQuantity as currentStock
      FROM order_items oi
      JOIN products p ON oi.productId = p.productId
      WHERE oi.orderId = ?
      ''', (order_id,))
      return cursor.fetchall()

    # def _return_order_items_to_stock(self, order_id: int):
    #     cursor = self.conn.cursor()
        
    #     cursor.execute('SELECT productId, quantity FROM order_items WHERE orderId = ?', (order_id,))
    #     items = cursor.fetchall()
        
    #     for product_id, quantity in items:
    #         cursor.execute('''
    #         UPDATE products 
    #         SET stockQuantity = stockQuantity + ?
    #         WHERE productId = ?
    #         ''', (quantity, product_id))
    
    def get_shipment_details(self, shipment_id: int) -> Optional[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('''
      SELECT 
          s.*,
          o.orderDate,
          o.totalAmount,
          o.status as orderStatus
      FROM shipments s
      JOIN orders o ON s.orderId = o.orderId
      WHERE s.shipmentId = ?
      ''', (shipment_id,))
      row = cursor.fetchone()
      if row:
          columns = [column[0] for column in cursor.description]
          return dict(zip(columns, row))
      return None
    
    def get_order_status(self, order_id: int) -> Optional[str]:
      cursor = self.conn.cursor()
      cursor.execute('SELECT status FROM orders WHERE orderId = ?', (order_id,))
      result = cursor.fetchone()
      return result[0] if result else None

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT oi.*, p.name as productName 
        FROM order_items oi
        JOIN products p ON oi.productId = p.productId
        WHERE oi.orderId = ?
        ''', (order_id,))
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
          item = dict(zip(columns,row))
          result.append(item)
        return result

    def get_all_orders(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY orderDate DESC')
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
          item = dict(zip(columns,row))
          result.append(item)
        return result
        # return [dict(zip(columns, row)) for row in cursor.fetchall()]
      
    def get_all_shipments(self) -> List[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('''
      SELECT 
          s.shipmentId,
          s.orderId,
          o.orderDate,
          o.status as orderStatus,
          s.shipmentDate,
          s.status as shipmentStatus,
          o.totalAmount
      FROM shipments s
      JOIN orders o ON s.orderId = o.orderId
      ORDER BY s.shipmentDate DESC
      ''')
      columns = [column[0] for column in cursor.description]
      rows = cursor.fetchall()
      result = []
        
      for row in rows:
        item = dict(zip(columns,row))
        result.append(item)
      return result

    def update_product_stock(self, productId: int, quantity: int):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE products 
        SET stockQuantity = stockQuantity + ? 
        WHERE productId = ?
        ''', (quantity, productId))
        self.conn.commit()
      
    def update_order_status(self, order_id: int, new_status: str):
      cursor = self.conn.cursor()
      cursor.execute('''
      UPDATE orders 
      SET status = ?
      WHERE orderId = ?
      ''', (new_status, order_id))
      self.conn.commit()

    def add_shipment(self, shipment_data: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO shipments (shipmentId, orderId, shipmentDate, status)
        VALUES (?, ?, ?, ?)
        ''', (shipment_data['shipmentId'], shipment_data['orderId'],
              shipment_data['shipmentDate'], shipment_data['status']))
        self.conn.commit()

    def add_supplier(self, supplier: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO suppliers (supplierId, name, contact)
        VALUES (?, ?, ?)
        ''', (supplier['supplierId'], supplier['name'], supplier['contact']))
        self.conn.commit()

    def add_order(self, order: Dict[str, Any], items: List[Dict[str, Any]]):
      cursor = self.conn.cursor()
      cursor.execute('''
      INSERT INTO orders (orderId, orderDate, status, totalAmount)
      VALUES (?, ?, ?, ?)
      ''', (order['orderId'], order['orderDate'], order['status'], order['totalAmount']))
    
      for item in items:
          cursor.execute('''
          INSERT INTO order_items (orderId, productId, quantity, price)
          VALUES (?, ?, ?, ?)
          ''', (order['orderId'], item['productId'], item['quantity'], item['price']))
      
      self.conn.commit()

    def add_shipment(self, shipment: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO shipments (shipmentId, orderId, shipmentDate, status)
        VALUES (?, ?, ?, ?)
        ''', (shipment['shipmentId'], shipment['orderId'], 
              shipment['shipmentDate'], shipment['status']))
        self.conn.commit()

    def add_supply_record(self, record: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO supply_records (productId, productName, quantity, supplierName, supplyDate)
        VALUES (?, ?, ?, ?, ?)
        ''', (record['product_id'], record['product_name'], 
              record['quantity'], record['supplier_name'], record['supply_date']))
        self.conn.commit()

    def get_supply_records(self) -> List[Dict[str, Any]]:
      cursor = self.conn.cursor()
      cursor.execute('''
      SELECT 
          recordId as "recordId",
          productId as "productId",
          productName as "productName",
          quantity as "quantity",
          supplierName as "supplierName",
          supplyDate as "supplyDate"
      FROM supply_records 
      ORDER BY supplyDate DESC
      ''')
      
      columns = [column[0] for column in cursor.description]
      return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()