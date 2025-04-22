from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


User = get_user_model()


class UserProfileTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("create-user-profile")
        self.employee_data = {
            "full_name": "Alice Employer",
            "email": "alice@example.com",
            "password": "strongpass123",
            "user_type": "employer",
            "phone_number": "1234567890",
            "company": "OpenAI Corp",
        }
        self.job_seeker_data = {
            "full_name": "Ale Emoyer",
            "email": "alejob@jobseek.com",
            "password": "strosngpass123",
            "user_type": "job_seeker",
            "phone_number": "1234567890",
            "skills": "python",
        }

    def test_user_profile_creation_employee(self):
        # Send POST request to create the user
        response = self.client.post(self.url, self.employee_data, format="json")
        print(response)

        # Assert the status code of the response (201 Created is the expected result)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the response contains the 'token' and 'user' fields
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

        # Assert that the user is created in the database
        user = User.objects.get(email=self.employee_data["email"])
        self.assertEqual(user.full_name, self.employee_data["full_name"])
        self.assertEqual(user.email, self.employee_data["email"])
        self.assertEqual(user.phone_number, self.employee_data["phone_number"])
        self.assertEqual(user.company, self.employee_data["company"])

        # Assert that a token has been created for the user
        token = Token.objects.get(user=user)
        self.assertEqual(response.data["token"], token.key)

    def test_missing_required_field(self):
        # Test case when a required field is missing (e.g., no email)
        incomplete_data = {
            key: value for key, value in self.employee_data.items() if key != "email"
        }

        response = self.client.post(self.url, incomplete_data, format="json")

        # Check if the response contains validation errors for missing fields
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)