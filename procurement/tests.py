from django.test import TestCase
from django.utils import timezone
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from store_management.models import Store  # Assuming Store model exists
from human_resources.models import Employee  # Assuming Employee model exists

class PurchaseOrderItemTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="test@supplier.com"
        )
        self.store = Store.objects.create(
            name="Test Store",
            address="123 Test St"
        )
        self.employee = Employee.objects.create(
            first_name="Test",
            last_name="Employee",
            email="test@employee.com"
        )
        self.purchase_order = PurchaseOrder.objects.create(
            supplier=self.supplier,
            store=self.store,
            created_by=self.employee
        )

    def test_create_purchase_order_item_with_product_name(self):
        """Test creating PurchaseOrderItem with product_name"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="Test Product",
            quantity=10,
            unit_price=5.00
        )
        self.assertEqual(item.product_name, "Test Product")
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.unit_price, 5.00)

    def test_create_purchase_order_item_without_product_name(self):
        """Test creating PurchaseOrderItem without product_name (blank)"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="",  # Blank
            quantity=5,
            unit_price=10.00
        )
        self.assertEqual(item.product_name, "")
        item.refresh_from_db()
        self.assertEqual(item.product_name, "")

    def test_purchase_order_total_calculation(self):
        """Test that PurchaseOrder total_amount is calculated correctly"""
        item1 = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="Product 1",
            quantity=2,
            unit_price=10.00
        )
        item2 = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="Product 2",
            quantity=3,
            unit_price=5.00
        )
        self.purchase_order.refresh_from_db()
        expected_total = (2 * 10.00) + (3 * 5.00)  # 20 + 15 = 35
        self.assertEqual(self.purchase_order.total_amount, expected_total)

    def test_str_method(self):
        """Test the __str__ method of PurchaseOrderItem"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="Test Product",
            quantity=1,
            unit_price=1.00
        )
        self.assertEqual(str(item), "1 x Test Product")

    def test_save_updates_order_total(self):
        """Test that saving an item updates the order's total_amount"""
        item = PurchaseOrderItem.objects.create(
            order=self.purchase_order,
            product_name="Test Product",
            quantity=1,
            unit_price=20.00
        )
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.total_amount, 20.00)

        # Update item
        item.quantity = 2
        item.save()
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.total_amount, 40.00)
