"""Automated tests for the Saved Recipe Django application.

Place this file at: saved_recipe/tests.py
Run: python manage.py test saved_recipe -v 2

Tests use Django's temporary test database; they do not modify db.sqlite3.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import SavedRecipe


class SavedRecipeModelTests(TestCase):
    """Memeriksa model SavedRecipe dan nilai defaultnya."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="model_user", password="TestPassword123!"
        )

    def test_default_category_favorite_and_string_representation(self):
        recipe = SavedRecipe.objects.create(user=self.user, name="Nasi Goreng")

        self.assertEqual(recipe.meal_category, "uncategorized")
        self.assertEqual(recipe.get_meal_category_display(), "Uncategorized")
        self.assertFalse(recipe.is_favorite)
        self.assertEqual(str(recipe), "Nasi Goreng")
        self.assertIsNotNone(recipe.created_at)

    def test_deleting_user_removes_their_saved_recipes(self):
        SavedRecipe.objects.create(user=self.user, name="Nasi Goreng")

        self.user.delete()

        self.assertEqual(SavedRecipe.objects.count(), 0)


class SavedRecipeCRUDTests(TestCase):
    """Memeriksa Create, Read, Update, Delete serta pembatasan akses."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="recipe_user", password="TestPassword123!"
        )
        cls.other_user = User.objects.create_user(
            username="other_recipe_user", password="TestPassword123!"
        )

        cls.breakfast = SavedRecipe.objects.create(
            user=cls.user,
            name="Nasi Goreng",
            description="Nasi goreng dengan telur",
            meal_category="breakfast",
            is_favorite=True,
            image_url="https://example.com/nasi-goreng.jpg",
        )
        cls.lunch = SavedRecipe.objects.create(
            user=cls.user,
            name="Ayam Bakar",
            description="Ayam dengan kecap",
            meal_category="lunch",
        )
        cls.dinner = SavedRecipe.objects.create(
            user=cls.user,
            name="Sup Ayam",
            description="Sup ayam hangat",
            meal_category="dinner",
        )
        cls.other_recipe = SavedRecipe.objects.create(
            user=cls.other_user,
            name="Resep Rahasia",
            meal_category="breakfast",
        )

    def setUp(self):
        # Semua tes dimulai dari akun yang login kecuali disebutkan berbeda.
        self.client.force_login(self.user)

    def _visible_recipe_ids(self, response):
        return set(response.context["recipes"].values_list("pk", flat=True))

    # READ
    def test_read_shows_only_current_users_recipes(self):
        response = self.client.get(reverse("saved_recipe"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "saved_recipe/saved_recipe.html")
        self.assertEqual(
            self._visible_recipe_ids(response),
            {self.breakfast.pk, self.lunch.pk, self.dinner.pk},
        )
        self.assertNotContains(response, "Resep Rahasia")

    def test_read_filter_by_category(self):
        response = self.client.get(reverse("saved_recipe"), {"category": "lunch"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._visible_recipe_ids(response), {self.lunch.pk})

    def test_read_search_ignores_letter_case(self):
        response = self.client.get(reverse("saved_recipe"), {"q": "nAsI"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._visible_recipe_ids(response), {self.breakfast.pk})

    def test_read_search_and_category_together(self):
        response = self.client.get(
            reverse("saved_recipe"), {"q": "AYAM", "category": "lunch"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._visible_recipe_ids(response), {self.lunch.pk})

    def test_read_shows_empty_message_when_no_results(self):
        response = self.client.get(reverse("saved_recipe"), {"q": "tidakada"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No saved recipes found.")
        self.assertEqual(self._visible_recipe_ids(response), set())

    def test_read_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse("saved_recipe"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)

    # CREATE
    def test_create_valid_recipe_is_owned_by_logged_in_user(self):
        response = self.client.post(
            reverse("create_saved_recipe"),
            {
                "name": "Pancake",
                "description": "Pancake lembut",
                "image_url": "https://example.com/pancake.jpg",
            },
        )

        self.assertRedirects(response, reverse("saved_recipe"))
        recipe = SavedRecipe.objects.get(user=self.user, name="Pancake")
        self.assertEqual(recipe.description, "Pancake lembut")
        self.assertEqual(recipe.image_url, "https://example.com/pancake.jpg")
        self.assertEqual(recipe.meal_category, "uncategorized")
        self.assertFalse(recipe.is_favorite)

    def test_create_rejects_empty_name(self):
        count_before = SavedRecipe.objects.count()

        response = self.client.post(
            reverse("create_saved_recipe"), {"name": "", "description": "Tanpa nama"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.content.decode())
        self.assertEqual(SavedRecipe.objects.count(), count_before)

    def test_create_rejects_invalid_image_url(self):
        response = self.client.post(
            reverse("create_saved_recipe"),
            {"name": "Pancake", "image_url": "bukan-url-valid"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(SavedRecipe.objects.filter(name="Pancake").exists())

    def test_create_ignores_user_category_and_favorite_submitted_by_client(self):
        response = self.client.post(
            reverse("create_saved_recipe"),
            {
                "name": "Resep Baru",
                "user": self.other_user.pk,
                "meal_category": "dinner",
                "is_favorite": "true",
            },
        )

        self.assertEqual(response.status_code, 302)
        recipe = SavedRecipe.objects.get(name="Resep Baru")
        self.assertEqual(recipe.user_id, self.user.pk)
        self.assertEqual(recipe.meal_category, "uncategorized")
        self.assertFalse(recipe.is_favorite)

    def test_create_requires_login(self):
        self.client.logout()

        response = self.client.post(reverse("create_saved_recipe"), {"name": "Pancake"})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SavedRecipe.objects.filter(name="Pancake").exists())

    def test_create_accepts_post_only(self):
        response = self.client.get(reverse("create_saved_recipe"))
        self.assertEqual(response.status_code, 405)

    # UPDATE
    def test_update_category_and_favorite_persists_to_database(self):
        response = self.client.post(
            reverse("update_saved_recipe", args=[self.breakfast.pk]),
            {"meal_category": "dinner", "is_favorite": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"success": True, "category": "Dinner", "is_favorite": False},
        )
        self.breakfast.refresh_from_db()
        self.assertEqual(self.breakfast.meal_category, "dinner")
        self.assertFalse(self.breakfast.is_favorite)

    def test_update_can_set_favorite_true(self):
        response = self.client.post(
            reverse("update_saved_recipe", args=[self.lunch.pk]),
            {"meal_category": "lunch", "is_favorite": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.lunch.refresh_from_db()
        self.assertTrue(self.lunch.is_favorite)

    def test_update_rejects_invalid_category_without_changing_recipe(self):
        response = self.client.post(
            reverse("update_saved_recipe", args=[self.breakfast.pk]),
            {"meal_category": "brunch", "is_favorite": "false"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.breakfast.refresh_from_db()
        self.assertEqual(self.breakfast.meal_category, "breakfast")
        self.assertTrue(self.breakfast.is_favorite)

    def test_update_other_users_recipe_returns_404(self):
        response = self.client.post(
            reverse("update_saved_recipe", args=[self.other_recipe.pk]),
            {"meal_category": "dinner", "is_favorite": "true"},
        )

        self.assertEqual(response.status_code, 404)
        self.other_recipe.refresh_from_db()
        self.assertEqual(self.other_recipe.meal_category, "breakfast")

    def test_update_nonexistent_recipe_returns_404(self):
        response = self.client.post(
            reverse("update_saved_recipe", args=[999999]),
            {"meal_category": "lunch", "is_favorite": "true"},
        )
        self.assertEqual(response.status_code, 404)

    def test_update_accepts_post_only(self):
        response = self.client.get(reverse("update_saved_recipe", args=[self.breakfast.pk]))
        self.assertEqual(response.status_code, 405)

    def test_update_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse("update_saved_recipe", args=[self.breakfast.pk]),
            {"meal_category": "dinner", "is_favorite": "false"},
        )
        self.assertEqual(response.status_code, 302)
        self.breakfast.refresh_from_db()
        self.assertEqual(self.breakfast.meal_category, "breakfast")

    # DELETE
    def test_delete_removes_only_selected_recipe(self):
        response = self.client.post(reverse("delete_saved_recipe", args=[self.breakfast.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertFalse(SavedRecipe.objects.filter(pk=self.breakfast.pk).exists())
        self.assertTrue(SavedRecipe.objects.filter(pk=self.lunch.pk).exists())

    def test_delete_other_users_recipe_returns_404(self):
        response = self.client.post(reverse("delete_saved_recipe", args=[self.other_recipe.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavedRecipe.objects.filter(pk=self.other_recipe.pk).exists())

    def test_delete_nonexistent_recipe_returns_404(self):
        response = self.client.post(reverse("delete_saved_recipe", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_accepts_post_only(self):
        response = self.client.get(reverse("delete_saved_recipe", args=[self.breakfast.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(SavedRecipe.objects.filter(pk=self.breakfast.pk).exists())

    def test_delete_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("delete_saved_recipe", args=[self.breakfast.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SavedRecipe.objects.filter(pk=self.breakfast.pk).exists())


class SavedRecipeCSRFTests(TestCase):
    """Memastikan operasi yang mengubah data memerlukan token CSRF."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="csrf_user", password="TestPassword123!"
        )
        self.recipe = SavedRecipe.objects.create(user=self.user, name="Nasi Goreng")
        self.strict_client = Client(enforce_csrf_checks=True)
        self.strict_client.force_login(self.user)

    def test_update_without_csrf_token_is_rejected(self):
        response = self.strict_client.post(
            reverse("update_saved_recipe", args=[self.recipe.pk]),
            {"meal_category": "lunch", "is_favorite": "true"},
        )

        self.assertEqual(response.status_code, 403)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.meal_category, "uncategorized")

    def test_delete_without_csrf_token_is_rejected(self):
        response = self.strict_client.post(
            reverse("delete_saved_recipe", args=[self.recipe.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(SavedRecipe.objects.filter(pk=self.recipe.pk).exists())


class SaveRecipeFromDetailsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from recipefinder.models import Recipe

        cls.user = get_user_model().objects.create_user(
            username="test_saver",
            password="TestPassword123!"
        )

        cls.recipe = Recipe.objects.create(
            id=659581,
            title="Scotch Eggs",
            image="https://example.com/scotch-eggs.jpg",
            summary="<p>Eggs wrapped in sausage.</p>",
            nutrients={"nutrients": []},
            instructions=[{"steps": []}],
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_save_recipe_success(self):
        response = self.client.post(
            reverse("create_saved_recipe"),
            {"recipe_id": 659581}
        )

        self.assertEqual(response.status_code, 302)

        saved = SavedRecipe.objects.get(
            user=self.user,
            source_recipe=self.recipe
        )

        self.assertEqual(saved.name, "Scotch Eggs")

    def test_save_recipe_no_duplicate(self):
        url = reverse("create_saved_recipe")

        self.client.post(url, {"recipe_id": 659581})
        self.client.post(url, {"recipe_id": 659581})

        total = SavedRecipe.objects.filter(
            user=self.user,
            source_recipe=self.recipe
        ).count()

        self.assertEqual(total, 1)

    def test_saved_button_appears(self):
        self.client.post(
            reverse("create_saved_recipe"),
            {"recipe_id": 659581}
        )

        response = self.client.get(
            reverse(
                "recipefinder:show_recipe_details",
                args=[659581]
            )
        )

        self.assertContains(
            response,
            "Saved — View Saved Recipes"
        )
