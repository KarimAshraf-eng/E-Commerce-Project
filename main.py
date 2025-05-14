from datetime import date
from Model.wareHouse_class import Warehouse
from Model.employee_class import Employee
from Model.product_class import Product
from Model.order_class import Order
from Model.supplier_class import Supplier
from Model.shipment_class import Shipment
from Model.orderItem_class import OrderItem
from database import Database

def main():
    db = Database()
    warehouse = Warehouse(1, "New York", 500)
    employee = Employee(1, "Alice", "Manager")

    products = {}
    all_products = db.get_all_products()
    for p in all_products:
      product_id = p['productId']
      
      product_object = Product(**p)
      product[product_id] = product_object
    # products = {p['productId']: Product(**p) for p in db.get_all_products()}
    orders = {}
    shipments = {}
    
    order_counter = db.get_max_order_id() + 1
    shipment_counter = db.get_max_shipment_id() + 1 if db.get_max_shipment_id() else 1
    supplier_counter = db.get_max_supplier_id() + 1 if db.get_max_supplier_id() else 1

    while True:
        print("\n=== Warehouse Management System ===")
        print("1. Product Management")
        print("2. Supplier Management")
        print("3. Order Management")
        print("4. Shipment Management")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            print("\n--- Product Management ---")
            print("1. Add New Product")
            print("2. View All Products")
            print("3. Remove Product")
            print("4. Check Product Stock")
            print("5. Add Stock to Product")
            choice_1 = input("Select an option: ")

            if choice_1 == "1":
                try:
                    pid = int(input("Product ID: "))
                    if pid in products:
                        print("⚠️ This ID is already in use!")
                        continue
                        
                    name = input("Product Name: ")
                    desc = input("Description: ")
                    price = float(input("Price: "))
                    qty = int(input("Quantity: "))
                    
                    product = Product(pid, name, desc, price, qty)
                    products[pid] = product
                    employee.manageInventory(warehouse, product, "add")
                    db.add_product(product.to_dict())
                    print("✅ Product added successfully.")
                except ValueError:
                    print("❌ Invalid input!")

            elif choice_1 == "2":
                print("\n--- All Products ---")
                if not products:
                    print("No products registered.")
                else:
                    for p in products.values():
                        print(f"ID: {p.productId}, Name: {p.name}, Price: {p.price}, Stock: {p.stockQuantity}")

            elif choice_1 == "3":
              try:
                  pid = int(input("Enter Product ID to remove: "))
                  
                  if pid not in products:
                      print("❌ Product not found in current session!")
                      continue
                      
                  db.remove_product(pid)
                  
                  warehouse.removeProduct(pid)
                  del products[pid]
                  
                  print("✅ Product removed successfully.")
                  
              except ValueError as ve:
                  print(f"❌ Error: {ve}")
              except Exception as e:
                  print(f"❌ Failed to remove product: {e}")

            elif choice_1 == "4":
                pid = int(input("Enter Product ID to check stock: "))
                if pid in products:
                    print(f"Available quantity: {products[pid].stockQuantity}")
                else:
                    print("❌ Product not found.")

            elif choice_1 == "5":
                pid = int(input("Product ID: "))
                if pid in products:
                    qty = int(input("Quantity to add: "))
                    products[pid].updateStock(qty)
                    db.update_product_stock(pid, qty)
                    print("✅ Stock updated.")
                else:
                    print("❌ Product not found.")

        elif choice == "2":
            print("\n--- Supplier Management ---")
            print("1. Add Supplier and Supply Products")
            print("2. View Supply Records")
            choice_2 = input("Select an option: ")

            if choice_2 == "1":
                name = input("Supplier Name: ")
                contact = input("Contact Info: ")
                
                supplier = Supplier(supplier_counter, name, contact)
                db.add_supplier({
                    'supplierId': supplier_counter,
                    'name': name,
                    'contact': contact
                })
                print(f"✅ Supplier registered with ID {supplier_counter}")
                supplier_counter += 1

                pid = int(input("Product ID to supply: "))
                if pid in products:
                    qty = int(input("Quantity supplied: "))
                    supplier.supplyProduct(products[pid], qty)
                    db.update_product_stock(pid, qty)
                    db.add_supply_record({
                        'product_id': pid,
                        'product_name': products[pid].name,
                        'quantity': qty,
                        'supplier_name': supplier.name,
                        'supply_date': str(date.today())
                    })
                    print("✅ Product supplied successfully.")
                else:
                    print("❌ Product not found.")

            elif choice_2 == "2":
                print("\n--- Supply Records ---")
                records = db.get_supply_records()
                if not records:
                    print("No supply records found.")
                else:
                    for record in records:
                        print(f"Date: {record['supplyDate']}, Product: {record['productName']}, Quantity: {record['quantity']}, Supplier: {record['supplierName']}")

        elif choice == "3":
            print("\n--- Order Management ---")
            print("1. Create New Order")
            print("2. Cancel Order")
            print("3. Track Order Status")
            print("4. View All Orders")
            choice_3 = input("Select an option: ")

            if choice_3 == "1":
              order_items = []
              while True:
                  try:
                      pid = int(input("Enter Product ID: "))
                      if pid not in products:
                          print("❌ Product not found!")
                          continue
                          
                      qty = int(input("Enter Quantity: "))
                      if qty <= 0:
                          print("❌ Quantity must be positive!")
                          continue
                          
                      if qty > products[pid].stockQuantity:
                          print(f"❌ Not enough stock! Available: {products[pid].stockQuantity}")
                          continue
                          
                      order_items.append(OrderItem(products[pid], qty))
                      products[pid].stockQuantity -= qty
                      db.update_product_stock(pid, -qty)
                      
                      cont = input("Add another product? (yes/no): ").lower()
                      if cont not in ['yes', 'y']:
                          break
                          
                  except ValueError:
                      print("❌ Invalid input! Please enter numbers only.")
                      continue

              if not order_items:
                  print("⚠️ No products added to order!")
                  continue
                  
              order = Order(order_counter, date.today(), "Pending", order_items)
              employee.processOrder(order)
              db.add_order(order.to_dict(), order.items_to_dict())
              orders[order_counter] = order
              print(f"✅ Order #{order_counter} created. Total: ${order.totalAmount:.2f}")
              order_counter += 1

            elif choice_3 == "2":
              try:
                  oid = int(input("Enter Order ID to cancel: "))
                  
                  updated_products = db.cancel_order(oid, update_memory=True)
                  
                  if oid in orders:
                      orders[oid].status = "Cancelled"
                      
                      for product_id, quantity in updated_products.items():
                          if product_id in products:
                              products[product_id].stockQuantity += quantity
                  
                  print("✅ Order cancelled successfully. Stock quantities updated.")
                  
              except ValueError as ve:
                  print(f"❌ Error: {ve}")
              except Exception as e:
                  print(f"❌ Failed to cancel order: {e}")

            elif choice_3 == "3":
              try:
                  oid = int(input("Enter Order ID to track: "))
                  order_data = db.get_order(oid)
                  if order_data:
                      items = db.get_order_items(oid)
                      print("\n--- Order Details ---")
                      print(f"Order ID: {order_data['orderId']}")
                      print(f"Date: {order_data['orderDate']}")
                      print(f"Status: {order_data['status']}")
                      print(f"Total Amount: ${order_data['totalAmount']:.2f}")
                      print("\n--- Order Items ---")
                      for item in items:
                          print(f"Product: {item['productName']}, Quantity: {item['quantity']}, Price: ${item['price']:.2f}")
                  else:
                      print("❌ Order not found!")
              except ValueError:
                  print("❌ Please enter a valid order ID!")

            elif choice_3 == "4":
                print("\n--- All Orders ---")
                all_orders = db.get_all_orders()
                if not all_orders:
                    print("No orders found.")
                else:
                    for order in all_orders:
                        print(f"ID: {order['orderId']}, Status: {order['status']}, Date: {order['orderDate']}, Total: ${order['totalAmount']}")

        elif choice == "4":
            print("\n--- Shipment Management ---")
            print("1. Create New Shipment")
            print("2. Update Shipment Status")
            print("3. View All Shipments")
            choice_4 = input("Select an option: ")

            if choice_4 == "1":
                try:
                    oid = int(input("Enter Order ID to ship: "))
                    
                    order_data = db.get_order(oid)
                    if not order_data:
                        print("❌ Order not found!")
                        continue
                        
                    if order_data['status'] == "Cancelled":
                        print("❌ Cannot ship a cancelled order!")
                        continue
                        
                    if order_data['status'] == "Shipped":
                        print("⚠️ This order has already been shipped!")
                        continue
                        
                    shipment_data = {
                        'shipmentId': shipment_counter,
                        'orderId': oid,
                        'shipmentDate': str(date.today()),
                        'status': "Shipped"
                    }
                    
                    db.add_shipment(shipment_data)
                    db.update_order_status(oid, "Shipped")
                    
                    print(f"✅ Shipment #{shipment_counter} created successfully.")
                    shipment_counter += 1
                    
                except ValueError:
                    print("❌ Please enter a valid order ID!")
                except Exception as e:
                    print(f"❌ Error creating shipment: {e}")

            elif choice_4 == "2":
              try:
                  sid = int(input("Enter Shipment ID to update: "))
                  shipment = db.get_shipment(sid)
                  
                  if not shipment:
                      print("❌ Shipment not found!")
                      continue
                      
                  print("\n--- Current Shipment Details ---")
                  print(f"Shipment ID: {shipment['shipmentId']}")
                  print(f"Order ID: {shipment['orderId']}")
                  print(f"Current Status: {shipment['status']}")
                  print(f"Shipment Date: {shipment['shipmentDate']}")
                  
                  print("\nAvailable statuses: Pending, Shipped, Delivered, Cancelled")
                  new_status = input("Enter new status: ").strip().capitalize()
                  
                  if new_status not in ["Pending", "Shipped", "Delivered", "Cancelled"]:
                      print("❌ Invalid status! Please choose from available options.")
                      continue
                      
                  db.update_shipment_status(sid, new_status)
                  
                  if new_status == "Delivered":
                      db.update_order_status(shipment['orderId'], "Delivered")
                  
                  print(f"✅ Shipment {sid} status updated to '{new_status}'")
                  
              except ValueError:
                  print("❌ Please enter a valid shipment ID!")
              except Exception as e:
                  print(f"❌ Error updating shipment: {e}")

            elif choice_4 == "3":
              print("\n--- All Shipments ---")
              try:
                  shipments = db.get_all_shipments()
                  if not shipments:
                      print("No shipments found.")
                  else:
                      print(f"{'ID':<8} {'Order ID':<10} {'Shipment Date':<15} {'Status':<15} {'Order Total':<12}")
                      print("-" * 60)
                      for ship in shipments:
                          print(
                              f"{ship['shipmentId']:<8} "
                              f"{ship['orderId']:<10} "
                              f"{ship['shipmentDate']:<15} "
                              f"{ship['shipmentStatus']:<15} "
                              f"${ship['totalAmount']:<10.2f}"
                          )
              except Exception as e:
                  print(f"❌ Error retrieving shipments: {e}")

        elif choice == "5":
            print("Shutting down system...")
            db.close()
            break

        else:
            print("❌ Invalid option, please try again.")

if __name__ == "__main__":
    main()