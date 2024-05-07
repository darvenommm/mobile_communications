from typing import cast, TypeAlias

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import test, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


HttpStatusesType: TypeAlias = tuple[int, ...]


# without wrapper this mixin class that be executed by django manage.py test
class ApiStatusTestCaseWrapper:
    class ApiStatusTestCase(TestCase):
        entity_name: str
        entity_data: dict

        do_it_use_token: bool = True

        get_all_statuses: HttpStatusesType = (status.HTTP_200_OK, status.HTTP_200_OK)
        get_one_statuses: HttpStatusesType = (status.HTTP_200_OK, status.HTTP_200_OK)
        create_statuses: HttpStatusesType = (status.HTTP_201_CREATED, status.HTTP_201_CREATED)
        change_put_statuses: HttpStatusesType = (status.HTTP_200_OK, status.HTTP_200_OK)
        change_patch_statuses: HttpStatusesType = (status.HTTP_200_OK, status.HTTP_200_OK)
        delete_statuses: HttpStatusesType = (status.HTTP_204_NO_CONTENT, status.HTTP_204_NO_CONTENT)

        __test_users: tuple[test.APIClient, ...] = ()

        __user_fields = ("first_name", "last_name", "username", "password")

        @classmethod
        def setUpClass(cls) -> None:
            cls.anonym = cls.__create_anonym()
            cls.authorized = cls.__create_authorized()
            cls.admin = cls.__create_admin()

            cls.add_to_test_users(cls.anonym, cls.authorized)

            cls.__entities_url = cls.__get_entities_url()

            super().setUpClass()

        @classmethod
        def add_to_test_users(cls, *test_users: test.APIClient) -> None:
            for test_user in test_users:
                cls.__test_users += (test_user,)

        @classmethod
        def reset_test_users(cls) -> None:
            cls.__test_users = ()

        def test_get_all(self) -> None:
            for index, test_user in enumerate(self.__test_users):
                response = cast(Response, test_user.get(self.__entities_url))
                self.assertEqual(response.status_code, self.get_all_statuses[index])

        def test_get_one(self) -> None:
            entity_url = self.__create_and_get_entity_url()

            for index, test_user in enumerate(self.__test_users):
                response = cast(Response, test_user.get(entity_url))
                self.assertEqual(response.status_code, self.get_one_statuses[index])

            self.__delete_by_entity_url(entity_url)

        def test_create(self) -> None:
            for index, test_user in enumerate(self.__test_users):
                response = cast(
                    Response, test_user.post(self.__entities_url, self.entity_data, format="json")
                )
                self.assertEqual(response.status_code, self.create_statuses[index])

                created_entity_pk = cast(str, response.json().get("id"))
                self.__delete_by_entity_url(self.__get_entity_url(created_entity_pk))

        def test_put_update(self) -> None:
            entity_url = self.__create_and_get_entity_url()

            for index, test_user in enumerate(self.__test_users):
                response = cast(
                    Response, test_user.put(entity_url, self.entity_data, format="json")
                )
                self.assertEqual(response.status_code, self.change_put_statuses[index])

            self.__delete_by_entity_url(entity_url)

        def test_patch_update(self) -> None:
            entity_url = self.__create_and_get_entity_url()

            for index, test_user in enumerate(self.__test_users):
                response = cast(
                    Response, test_user.patch(entity_url, self.entity_data, format="json")
                )
                self.assertEqual(response.status_code, self.change_patch_statuses[index])

            self.__delete_by_entity_url(entity_url)

        def test_delete_update(self) -> None:
            entity_url = self.__create_and_get_entity_url()

            for index, test_user in enumerate(self.__test_users):
                response = cast(
                    Response, test_user.delete(entity_url, self.entity_data, format="json")
                )
                self.assertEqual(response.status_code, self.delete_statuses[index])

        @classmethod
        def __create_anonym(cls) -> test.APIClient:
            return test.APIClient()

        @classmethod
        def __create_authorized(cls) -> test.APIClient:
            authorized_user_created_data = cls.__create_unique_user_data("token_authorized")
            authorized_user = get_user_model().objects.create(**authorized_user_created_data)

            authorized_client = test.APIClient()
            authorized_client.login(
                username=authorized_user_created_data["username"],
                password=authorized_user_created_data["password"],
            )

            if cls.do_it_use_token:
                user_token = cast(Token, getattr(authorized_user, "auth_token")).key
                authorized_client.credentials(HTTP_AUTHORIZATION=f"Token {user_token}")

            return authorized_client

        @classmethod
        def __create_admin(cls) -> test.APIClient:
            admin_created_data = cls.__create_unique_user_data("admin")
            admin_user = get_user_model().objects.create(
                **admin_created_data,
                is_staff=True,
                is_superuser=True,
            )

            admin_client = test.APIClient()

            admin_client.login(
                username=admin_created_data["username"],
                password=admin_created_data["password"],
            )

            if cls.do_it_use_token:
                admin_token = cast(Token, getattr(admin_user, "auth_token")).key
                admin_client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token}")

            return admin_client

        @classmethod
        def __create_unique_user_data(cls, unique_name: str) -> dict[str, str]:
            return {
                field_name: f"{cls.__name__}_{unique_name}_{field_name}"
                for field_name in cls.__user_fields
            }

        @classmethod
        def __get_entities_url(cls) -> str:
            api_url = cast(str, settings.REST_FRAMEWORK_API_PATH).strip("/")
            entity_name = cls.entity_name.strip("/")

            return f"/{api_url}/{entity_name}/"

        def __get_entity_url(self, entity_pk: str) -> str:
            return f"{self.__get_entities_url()}{entity_pk}/"

        def __create_and_get_entity_url(self) -> str:
            response = cast(
                Response, self.admin.post(self.__entities_url, self.entity_data, format="json")
            )

            if response.status_code != 201:
                raise ValueError("Incorrect post method returned status code")

            returned_data = response.json()

            if not isinstance(returned_data, dict):
                raise TypeError("Incorrect post method returned value")

            entity_pk = returned_data.get("id")

            if entity_pk is None:
                raise ValueError("Not found pk in post method returned value!")

            return self.__get_entity_url(entity_pk)

        def __delete_by_entity_url(self, entity_url: str) -> None:
            self.admin.delete(entity_url)
