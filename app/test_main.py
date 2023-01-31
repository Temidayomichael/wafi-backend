

import unittest
from datetime import datetime, timedelta
import jwt
from fastapi.testclient import TestClient
from .app import app


class TestUser(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.token = jwt.encode({'dayo': 'test'},
                                'secret', algorithm='HS256')
        self.wrong_token = jwt.encode(
            {'username': 'test'}, 'wrong-secret', algorithm='HS256')

    def test_balance_success(self):
        response = self.client.get(
            "/balance", headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        username = "testuser"
        user = {"balance": 1000}

        response = self.client.post(
            "/users/{username}", json=user, headers={'Authorization': f'Bearer {self.token}'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_deposit(self):
        username = "testuser"
        amount = 500

        response = self.client.post(
            "/deposit", json={"username": username, "amount": amount}, headers={'Authorization': f'Bearer {self.token}'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("balance", response.json())

    def test_send(self):
        from_username = "testuser1"  # sender's username
        to_username = "testuser2"  # receiver's username
        amount = 500  # amount to be sent

        response = self.client.post(
            "/send", json={"from_username": from_username, "to_username": to_username, "amount": amount}, headers={'Authorization': f'Bearer {self.token}'})

        # check if the status code is 200 (success)
        self.assertEqual(response.status_code, 200)

    def test_balance(self):
        username = "testuser"   # user whose balance is to be checked

        response = self.client.get(
            "/balance/{username}", headers={'Authorization': f'Bearer {self.token}'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("balance", response.json())
