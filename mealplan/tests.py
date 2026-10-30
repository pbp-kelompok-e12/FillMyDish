from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from saved_recipe.models import SavedRecipe

from .models import MealPlan, MealPlanItem


class MealPlanFlowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="mealplan-user",
            password="test-password",
        )
        self.other_user = user_model.objects.create_user(
            username="other-user",
            password="test-password",
        )
        self.client.force_login(self.user)

    def make_recipe(self, user=None, name="Test Recipe"):
        return SavedRecipe.objects.create(
            user=user or self.user,
            name=name,
            description=f"Description for {name}",
        )

    def make_plan(self, title="Weekly Plan", description="Plan description"):
        return MealPlan.objects.create(
            user=self.user,
            title=title,
            description=description,
        )

    def add_recipe_to_plan(self, plan, recipe, order=0):
        return MealPlanItem.objects.create(
            meal_plan=plan,
            recipe=recipe,
            order=order,
        )

    def set_session_value(self, key, value):
        session = self.client.session
        session[key] = value
        session.save()

    def test_mealplan_pages_require_login(self):
        self.client.logout()
        urls = [
            reverse("mealplan:show_mealplan"),
            reverse("mealplan:create_mealplan"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith("/login/"))

    def test_plan_list_only_shows_the_current_users_plans_and_back_link(self):
        own_plan = self.make_plan()
        MealPlan.objects.create(user=self.other_user, title="Private Plan")

        response = self.client.get(reverse("mealplan:show_mealplan"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, own_plan.title)
        self.assertNotContains(response, "Private Plan")
        self.assertContains(response, "Back to Main Menu")

    def test_create_requires_a_title_and_stores_a_session_draft(self):
        response = self.client.post(
            reverse("mealplan:create_mealplan"),
            {"title": "   ", "description": "Optional description"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Plan title is required.")
        self.assertFalse(MealPlan.objects.exists())
        self.assertNotIn("mealplan_draft", self.client.session)

        response = self.client.post(
            reverse("mealplan:create_mealplan"),
            {"title": "  Weekday meals  ", "description": "   "},
        )

        self.assertRedirects(response, reverse("saved_recipe"))
        self.assertEqual(
            self.client.session["mealplan_draft"],
            {
                "title": "Weekday meals",
                "description": "",
                "recipe_ids": [],
            },
        )
        self.assertFalse(MealPlan.objects.exists())

    def test_saved_recipe_toggle_adds_then_removes_a_recipe_from_create_draft(self):
        recipe = self.make_recipe()
        self.set_session_value(
            "mealplan_draft",
            {"title": "Weekday meals", "description": "", "recipe_ids": []},
        )
        toggle_url = reverse("mealplan:toggle_draft_recipe", args=[recipe.pk])

        add_response = self.client.post(toggle_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(add_response.status_code, 200)
        self.assertTrue(add_response.json()["added"])
        self.assertEqual(self.client.session["mealplan_draft"]["recipe_ids"], [recipe.pk])

        remove_response = self.client.post(
            toggle_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(remove_response.json()["added"])
        self.assertEqual(self.client.session["mealplan_draft"]["recipe_ids"], [])

    def test_recipe_toggle_requires_a_draft_and_recipe_owned_by_user(self):
        recipe = self.make_recipe()
        toggle_url = reverse("mealplan:toggle_draft_recipe", args=[recipe.pk])

        response_without_draft = self.client.post(toggle_url)
        self.assertEqual(response_without_draft.status_code, 400)

        self.set_session_value(
            "mealplan_draft",
            {"title": "Plan", "description": "", "recipe_ids": []},
        )
        another_users_recipe = self.make_recipe(
            user=self.other_user,
            name="Private Recipe",
        )
        response_for_private_recipe = self.client.post(
            reverse("mealplan:toggle_draft_recipe", args=[another_users_recipe.pk])
        )
        self.assertEqual(response_for_private_recipe.status_code, 404)

        get_response = self.client.get(toggle_url)
        self.assertEqual(get_response.status_code, 405)

    def test_create_draft_requires_a_recipe_and_saves_plan_with_selected_recipes(self):
        recipe_one = self.make_recipe(name="Rice Bowl")
        recipe_two = self.make_recipe(name="Vegetable Soup")
        save_url = reverse("mealplan:save_mealplan_draft")
        self.set_session_value(
            "mealplan_draft",
            {"title": "Dinner", "description": "", "recipe_ids": []},
        )

        empty_response = self.client.post(save_url)
        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(MealPlan.objects.count(), 0)

        self.set_session_value(
            "mealplan_draft",
            {
                "title": "Dinner",
                "description": "Quick meals",
                "recipe_ids": [recipe_two.pk, recipe_one.pk],
            },
        )
        response = self.client.post(save_url)

        self.assertEqual(response.status_code, 200)
        result = response.json()
        plan = MealPlan.objects.get()
        self.assertEqual(result["redirect_url"], reverse("mealplan:mealplan_detail", args=[plan.pk]))
        self.assertEqual(plan.title, "Dinner")
        self.assertEqual(plan.description, "Quick meals")
        self.assertEqual(
            list(plan.items.order_by("order").values_list("recipe_id", flat=True)),
            [recipe_two.pk, recipe_one.pk],
        )
        self.assertNotIn("mealplan_draft", self.client.session)

    def test_create_draft_rejects_recipes_owned_by_another_user(self):
        private_recipe = self.make_recipe(
            user=self.other_user,
            name="Private recipe",
        )
        self.set_session_value(
            "mealplan_draft",
            {"title": "Dinner", "description": "", "recipe_ids": [private_recipe.pk]},
        )

        response = self.client.post(reverse("mealplan:save_mealplan_draft"))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(MealPlan.objects.exists())

    def test_cancel_create_discards_draft_without_creating_a_plan(self):
        self.set_session_value(
            "mealplan_draft",
            {"title": "Unfinished", "description": "", "recipe_ids": []},
        )

        response = self.client.post(reverse("mealplan:cancel_mealplan_draft"))

        self.assertRedirects(response, reverse("mealplan:show_mealplan"))
        self.assertNotIn("mealplan_draft", self.client.session)
        self.assertFalse(MealPlan.objects.exists())

    def test_edit_metadata_is_staged_and_saved_recipe_page_receives_edit_draft(self):
        plan = self.make_plan()
        recipe = self.make_recipe()
        self.add_recipe_to_plan(plan, recipe)

        edit_url = reverse("mealplan:update_mealplan", args=[plan.pk])
        get_response = self.client.get(edit_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(self.client.session["mealplan_edit_draft"]["plan_id"], plan.pk)

        response = self.client.post(
            edit_url,
            {"title": "  Updated Plan  ", "description": "  Updated description  "},
        )
        self.assertRedirects(
            response,
            reverse("mealplan:edit_mealplan_recipes", args=[plan.pk]),
        )
        self.assertEqual(plan.title, "Weekly Plan")
        self.assertEqual(plan.description, "Plan description")
        self.assertEqual(self.client.session["mealplan_edit_draft"]["title"], "Updated Plan")

        saved_recipe_response = self.client.get(
            reverse("saved_recipe"),
            {"editing_plan": plan.pk},
        )
        self.assertEqual(saved_recipe_response.status_code, 200)
        self.assertIsNotNone(saved_recipe_response.context["mealplan_edit_draft"])
        self.assertEqual(saved_recipe_response.context["draft_recipe_ids"], [recipe.pk])
        self.assertContains(saved_recipe_response, "Back to Plan")

        normal_saved_recipes_response = self.client.get(reverse("saved_recipe"))
        self.assertIsNone(normal_saved_recipes_response.context["mealplan_edit_draft"])

    def test_skip_metadata_keeps_current_plan_details(self):
        plan = self.make_plan()

        self.client.get(reverse("mealplan:update_mealplan", args=[plan.pk]))
        response = self.client.get(
            reverse("mealplan:edit_mealplan_recipes", args=[plan.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["plan"].title, "Weekly Plan")
        self.assertEqual(response.context["plan"].description, "Plan description")
        self.assertEqual(self.client.session["mealplan_edit_draft"]["title"], "Weekly Plan")

    def test_edit_rejects_empty_title(self):
        plan = self.make_plan()
        edit_url = reverse("mealplan:update_mealplan", args=[plan.pk])
        self.client.get(edit_url)

        response = self.client.post(
            edit_url,
            {"title": "   ", "description": "New description"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Plan title is required.", status_code=400)
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Weekly Plan")

    def test_edit_recipe_selection_is_staged_then_saved_together(self):
        plan = self.make_plan()
        old_recipe = self.make_recipe(name="Old recipe")
        new_recipe = self.make_recipe(name="New recipe")
        self.add_recipe_to_plan(plan, old_recipe)

        self.client.get(reverse("mealplan:update_mealplan", args=[plan.pk]))
        self.client.post(
            reverse("mealplan:update_mealplan", args=[plan.pk]),
            {"title": "Updated Plan", "description": "New description"},
        )

        toggle_url = reverse("mealplan:toggle_draft_recipe", args=[old_recipe.pk])
        self.client.post(toggle_url)
        self.client.post(
            reverse("mealplan:toggle_draft_recipe", args=[new_recipe.pk])
        )

        plan.refresh_from_db()
        self.assertEqual(plan.title, "Weekly Plan")
        self.assertEqual(
            list(plan.items.values_list("recipe_id", flat=True)),
            [old_recipe.pk],
        )

        detail_response = self.client.get(
            reverse("mealplan:edit_mealplan_recipes", args=[plan.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Manage Recipes")
        self.assertNotContains(detail_response, "delete-recipe-modal")
        self.assertNotContains(detail_response, "sr-btn-delete")
        self.assertEqual(
            [item["recipe"].pk for item in detail_response.context["items"]],
            [new_recipe.pk],
        )

        response = self.client.post(
            reverse("mealplan:save_mealplan_recipe_changes", args=[plan.pk])
        )

        self.assertRedirects(response, reverse("mealplan:mealplan_detail", args=[plan.pk]))
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Updated Plan")
        self.assertEqual(plan.description, "New description")
        self.assertEqual(
            list(plan.items.values_list("recipe_id", flat=True)),
            [new_recipe.pk],
        )
        self.assertNotIn("mealplan_edit_draft", self.client.session)

    def test_cancel_edit_discards_staged_changes(self):
        plan = self.make_plan()
        original_recipe = self.make_recipe(name="Original")
        new_recipe = self.make_recipe(name="Draft addition")
        self.add_recipe_to_plan(plan, original_recipe)

        self.client.get(reverse("mealplan:update_mealplan", args=[plan.pk]))
        self.client.post(
            reverse("mealplan:update_mealplan", args=[plan.pk]),
            {"title": "Unsaved title", "description": "Unsaved description"},
        )
        self.client.post(
            reverse("mealplan:toggle_draft_recipe", args=[new_recipe.pk])
        )

        response = self.client.post(
            reverse("mealplan:save_mealplan_recipe_changes", args=[plan.pk]),
            {"action": "cancel"},
        )

        self.assertRedirects(response, reverse("mealplan:mealplan_detail", args=[plan.pk]))
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Weekly Plan")
        self.assertEqual(plan.description, "Plan description")
        self.assertEqual(
            list(plan.items.values_list("recipe_id", flat=True)),
            [original_recipe.pk],
        )
        self.assertNotIn("mealplan_edit_draft", self.client.session)

    def test_cancel_from_edit_metadata_discards_draft(self):
        plan = self.make_plan()
        edit_url = reverse("mealplan:update_mealplan", args=[plan.pk])
        self.client.get(edit_url)
        self.client.post(
            edit_url,
            {"title": "Unsaved title", "description": "Unsaved"},
        )

        response = self.client.post(
            edit_url,
            {"action": "cancel"},
        )

        self.assertRedirects(response, reverse("mealplan:mealplan_detail", args=[plan.pk]))
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Weekly Plan")
        self.assertNotIn("mealplan_edit_draft", self.client.session)

    def test_detail_page_has_back_link_and_only_owner_can_view_or_edit(self):
        plan = self.make_plan()
        own_recipe = self.make_recipe()
        self.add_recipe_to_plan(plan, own_recipe)

        response = self.client.get(reverse("mealplan:mealplan_detail", args=[plan.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Back to Meal Plans")
        self.assertContains(response, "Edit Your Plan")

        another_users_plan = MealPlan.objects.create(
            user=self.other_user,
            title="Private Plan",
        )
        private_detail = self.client.get(
            reverse("mealplan:mealplan_detail", args=[another_users_plan.pk])
        )
        private_edit = self.client.get(
            reverse("mealplan:update_mealplan", args=[another_users_plan.pk])
        )
        self.assertEqual(private_detail.status_code, 404)
        self.assertEqual(private_edit.status_code, 404)

    def test_delete_plan_is_post_only_and_removes_only_owned_plan(self):
        plan = self.make_plan()
        delete_url = reverse("mealplan:delete_mealplan", args=[plan.pk])

        get_response = self.client.get(delete_url)
        self.assertEqual(get_response.status_code, 405)

        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["message"])
        self.assertFalse(MealPlan.objects.filter(pk=plan.pk).exists())

        another_users_plan = MealPlan.objects.create(
            user=self.other_user,
            title="Private Plan",
        )
        private_delete = self.client.post(
            reverse("mealplan:delete_mealplan", args=[another_users_plan.pk])
        )
        self.assertEqual(private_delete.status_code, 404)
        self.assertTrue(MealPlan.objects.filter(pk=another_users_plan.pk).exists())
