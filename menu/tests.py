from django.test import TestCase, Client
from django.urls import reverse
from menu.models import Category, MenuItem
from tables.models import Table
from decimal import Decimal

class MenuTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Food", slug="food")
        self.item = MenuItem.objects.create(
            category=self.category,
            name="Pizza",
            price=Decimal("299.00"),
            is_available=True
        )
        self.unavailable_item = MenuItem.objects.create(
            category=self.category,
            name="Sold Out Cake",
            price=Decimal("150.00"),
            is_available=False
        )
        self.table = Table.objects.create(number=1)

    def test_menu_view_status_code(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)

    def test_menu_filters_unavailable_items(self):
        # Now that we've fixed bug #13 and #10, unavailable items should not even be in context
        response = self.client.get(reverse('menu'))
        categories = response.context['categories']
        for cat in categories:
            for item in cat.items.all():
                self.assertTrue(item.is_available)
                self.assertNotEqual(item.name, "Sold Out Cake")

    def test_cart_math(self):
        # Verify fix for bug #7 (Decimal math)
        session = self.client.session
        session['cart'] = {
            str(self.item.id): {
                'name': self.item.name,
                'price': '299.00',
                'quantity': 3
            }
        }
        session.save()
        
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        # 299 * 3 = 897.00
        self.assertEqual(response.context['total'], Decimal('897.00'))
