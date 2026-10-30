
######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product API Service Test Suite
"""

import os
import logging
from decimal import Decimal
from urllib.parse import quote_plus
from unittest import TestCase

from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/products"


######################################################################
# TEST CASES
######################################################################

# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################

    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []

        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(
                BASE_URL,
                json=test_product.serialize()
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product"
            )

            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)

        return products

    ############################################################
    # EXISTING TEST CASES
    ############################################################

    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["message"], "OK")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()

        logging.debug("Test Product: %s", test_product.serialize())

        response = self.client.post(
            BASE_URL,
            json=test_product.serialize()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        new_product = response.get_json()

        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(
            new_product["description"],
            test_product.description
        )
        self.assertEqual(
            Decimal(new_product["price"]),
            test_product.price
        )
        self.assertEqual(
            new_product["available"],
            test_product.available
        )
        self.assertEqual(
            new_product["category"],
            test_product.category.name
        )

    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]

        logging.debug("Product no name: %s", new_product)

        response = self.client.post(
            BASE_URL,
            json=new_product
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(
            BASE_URL,
            data="bad data"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with wrong Content-Type"""
        response = self.client.post(
            BASE_URL,
            data={},
            content_type="plain/text"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    ############################################################
    # TEST READ
    ############################################################

    def test_get_product(self):
        """It should Read a Product"""
        test_product = self._create_products(1)[0]

        response = self.client.get(
            f"{BASE_URL}/{test_product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()

        self.assertEqual(data["name"], test_product.name)
        self.assertEqual(
            data["description"],
            test_product.description
        )
        self.assertEqual(
            Decimal(data["price"]),
            test_product.price
        )
        self.assertEqual(
            data["available"],
            test_product.available
        )
        self.assertEqual(
            data["category"],
            test_product.category.name
        )

    def test_get_product_not_found(self):
        """It should not Read a Product that does not exist"""
        response = self.client.get(f"{BASE_URL}/0")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    ############################################################
    # TEST UPDATE
    ############################################################

    def test_update_product(self):
        """It should Update an existing Product"""
        test_product = self._create_products(1)[0]

        new_description = "Updated product description"

        test_product.description = new_description

        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            json=test_product.serialize()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()

        self.assertEqual(data["id"], test_product.id)
        self.assertEqual(data["description"], new_description)

    ############################################################
    # TEST DELETE
    ############################################################

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]

        response = self.client.delete(
            f"{BASE_URL}/{test_product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        response = self.client.get(
            f"{BASE_URL}/{test_product.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    ############################################################
    # TEST LIST ALL
    ############################################################

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)

        response = self.client.get(BASE_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()
        self.assertEqual(len(data), 5)

    ############################################################
    # TEST LIST BY NAME
    ############################################################

    def test_query_product_by_name(self):
        """It should Query Products by Name"""
        products = self._create_products(5)

        name = products[0].name
        name_count = len([
            product for product in products
            if product.name == name
        ])

        response = self.client.get(
            BASE_URL,
            query_string=f"name={quote_plus(name)}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()

        self.assertEqual(len(data), name_count)

        for product in data:
            self.assertEqual(product["name"], name)

    ############################################################
    # TEST LIST BY CATEGORY
    ############################################################

    def test_query_product_by_category(self):
        """It should Query Products by Category"""
        products = self._create_products(10)

        category = products[0].category.name

        category_count = len([
            product for product in products
            if product.category.name == category
        ])

        response = self.client.get(
            BASE_URL,
            query_string=f"category={category}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()

        self.assertEqual(len(data), category_count)

        for product in data:
            self.assertEqual(product["category"], category)

    ############################################################
    # TEST LIST BY AVAILABILITY
    ############################################################

    def test_query_product_by_availability(self):
        """It should Query Products by Availability"""
        products = self._create_products(10)

        available = products[0].available

        available_count = len([
            product for product in products
            if product.available == available
        ])

        response = self.client.get(
            BASE_URL,
            query_string=f"available={str(available).lower()}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()

        self.assertEqual(len(data), available_count)

        for product in data:
            self.assertEqual(product["available"], available)

    ######################################################################
    # UTILITY FUNCTIONS
    ######################################################################

    def get_product_count(self):
        """Save the current number of products"""
        response = self.client.get(BASE_URL)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.get_json()
        return len(data)
