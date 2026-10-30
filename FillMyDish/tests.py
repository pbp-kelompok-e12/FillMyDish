from FillMyDish.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import ConnectionForm, ConnectionFormSet, ProfileForm, RegisterForm
from .models import Connection, Profile

# tests.py -> berisi unit test untuk model, form, dan view terkait profil pengguna, koneksi media 
#             sosial, dan pendaftaran akun. Unit test ini memastikan bahwa model, form, dan view 
#             berfungsi sesuai harapan, termasuk validasi input, penyimpanan data, dan pengalihan 
#             halaman

class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="nadhif", password="Testpass123!")

    def test_profile_string_representation(self):
        profile = Profile.objects.create(user=self.user)

        self.assertEqual(str(profile), "nadhif's profile")

    def test_connection_string_representation(self):
        profile = Profile.objects.create(user=self.user)
        connection = Connection.objects.create(
            profile=profile,
            platform="Instagram",
            url="https://instagram.com/nadhif",
        )

        self.assertEqual(str(connection), "Instagram: https://instagram.com/nadhif")

    def test_deleting_profile_cascades_to_connections(self):
        profile = Profile.objects.create(user=self.user)
        connection = Connection.objects.create(
            profile=profile,
            platform="Instagram",
            url="https://instagram.com/nadhif",
        )

        profile.delete()

        self.assertFalse(Connection.objects.filter(pk=connection.pk).exists())

    def test_deleting_user_cascades_to_profile(self):
        profile = Profile.objects.create(user=self.user)

        self.user.delete()

        self.assertFalse(Profile.objects.filter(pk=profile.pk).exists())


class ProfileFormTests(TestCase):
    def test_profile_form_accepts_valid_profile_data(self):
        form = ProfileForm(data={
            "full_name": "Nadhif Aydin",
            "username": "nadhif",
            "email": "nadhif@example.com",
            "date_of_birth": "2004-02-03",
            "bio": "Food enthusiast",
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_profile_form_rejects_invalid_email(self):
        form = ProfileForm(data={
            "full_name": "Nadhif Aydin",
            "username": "nadhif",
            "email": "not-an-email",
            "date_of_birth": "",
            "bio": "Food enthusiast",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_profile_form_rejects_invalid_date(self):
        form = ProfileForm(data={
            "full_name": "Nadhif Aydin",
            "username": "nadhif",
            "email": "nadhif@example.com",
            "date_of_birth": "not-a-date",
            "bio": "Food enthusiast",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)

    def test_connection_form_accepts_valid_connection(self):
        form = ConnectionForm(data={
            "platform": "Instagram",
            "url": "https://instagram.com/nadhif",
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_connection_form_rejects_invalid_url(self):
        form = ConnectionForm(data={"platform": "Instagram", "url": "not-a-url"})

        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)

    def test_connection_formset_accepts_empty_extra_form(self):
        profile = Profile(user=User(username="nadhif"))
        formset = ConnectionFormSet(data={
            "connections-TOTAL_FORMS": "1",
            "connections-INITIAL_FORMS": "0",
            "connections-MIN_NUM_FORMS": "0",
            "connections-MAX_NUM_FORMS": "1000",
            "connections-0-platform": "",
            "connections-0-url": "",
        }, instance=profile)

        self.assertTrue(formset.is_valid(), formset.errors)


class ProfileViewTests(TestCase):
    password = "Testpass123!"

    def setUp(self):
        self.user = User.objects.create_user(
            username="nadhif",
            email="old@example.com",
            password=self.password,
        )
        self.profile = Profile.objects.create(
            user=self.user,
            username="nadhif",
            email="old@example.com",
            full_name="Old Name",
            bio="Old bio",
        )

    def profile_payload(self, **overrides):
        data = {
            "full_name": "Nadhif Aydin",
            "username": "nadhif_new",
            "email": "new@example.com",
            "date_of_birth": "2004-02-03",
            "bio": "Food enthusiast",
            "connections-TOTAL_FORMS": "1",
            "connections-INITIAL_FORMS": "0",
            "connections-MIN_NUM_FORMS": "0",
            "connections-MAX_NUM_FORMS": "1000",
            "connections-0-platform": "",
            "connections-0-url": "",
        }
        data.update(overrides)
        return data

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_edit_profile_requires_authentication(self):
        response = self.client.get(reverse("edit_profile"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('edit_profile')}")

    def test_profile_view_displays_profile_and_assets(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")
        self.assertContains(response, "@nadhif")
        self.assertContains(response, "profile-page.css")
        self.assertContains(response, "profile-page.js")

    def test_profile_view_creates_missing_profile(self):
        self.client.force_login(self.user)
        self.profile.delete()

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_public_profile_creates_profile_for_user_and_hides_edit_button(self):
        visitor = User.objects.create_user(username="visitor", password=self.password)

        response = self.client.get(reverse("user_profile", kwargs={"username": visitor.username}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "@visitor")
        self.assertTrue(Profile.objects.filter(user=visitor).exists())
        self.assertNotContains(response, "profile-edit-btn")

    def test_edit_profile_get_displays_profile_form_and_connections(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_profile.html")
        self.assertIsInstance(response.context["form"], ProfileForm)
        self.assertTrue(response.context["formset"].is_bound is False)

    def test_edit_profile_post_updates_profile_and_user(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("edit_profile"), self.profile_payload())

        self.assertRedirects(response, reverse("profile"))
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Nadhif Aydin")
        self.assertEqual(self.profile.username, "nadhif_new")
        self.assertEqual(self.profile.email, "new@example.com")
        self.assertEqual(self.profile.bio, "Food enthusiast")
        self.assertEqual(self.user.username, "nadhif_new")
        self.assertEqual(self.user.email, "new@example.com")

    def test_edit_profile_post_creates_connection(self):
        self.client.force_login(self.user)
        payload = self.profile_payload(**{
            "connections-TOTAL_FORMS": "2",
            "connections-1-platform": "Instagram",
            "connections-1-url": "https://instagram.com/nadhif",
        })

        response = self.client.post(reverse("edit_profile"), payload)

        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(self.profile.connections.filter(
            platform="Instagram",
            url="https://instagram.com/nadhif",
        ).exists())

    def test_edit_profile_post_updates_connection(self):
        connection = Connection.objects.create(
            profile=self.profile,
            platform="Instagram",
            url="https://instagram.com/old",
        )
        self.client.force_login(self.user)
        payload = self.profile_payload(**{
            "connections-TOTAL_FORMS": "1",
            "connections-INITIAL_FORMS": "1",
            "connections-0-id": str(connection.pk),
            "connections-0-platform": "TikTok",
            "connections-0-url": "https://tiktok.com/@nadhif",
        })

        response = self.client.post(reverse("edit_profile"), payload)

        self.assertRedirects(response, reverse("profile"))
        connection.refresh_from_db()
        self.assertEqual(connection.platform, "TikTok")
        self.assertEqual(connection.url, "https://tiktok.com/@nadhif")

    def test_edit_profile_post_deletes_connection(self):
        connection = Connection.objects.create(
            profile=self.profile,
            platform="Instagram",
            url="https://instagram.com/nadhif",
        )
        self.client.force_login(self.user)
        payload = self.profile_payload(**{
            "connections-TOTAL_FORMS": "1",
            "connections-INITIAL_FORMS": "1",
            "connections-0-id": str(connection.pk),
            "connections-0-platform": "Instagram",
            "connections-0-url": "https://instagram.com/nadhif",
            "connections-0-DELETE": "on",
        })

        response = self.client.post(reverse("edit_profile"), payload)

        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(Connection.objects.filter(pk=connection.pk).exists())

    def test_invalid_profile_data_does_not_save_profile_or_user(self):
        self.client.force_login(self.user)
        payload = self.profile_payload(email="invalid-email")

        response = self.client.post(reverse("edit_profile"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Old Name")
        self.assertEqual(self.profile.email, "old@example.com")
        self.assertEqual(self.user.username, "nadhif")

    def test_invalid_connection_does_not_save_profile_or_connections(self):
        self.client.force_login(self.user)
        payload = self.profile_payload(**{
            "connections-TOTAL_FORMS": "2",
            "connections-1-platform": "Instagram",
            "connections-1-url": "not-a-url",
        })

        response = self.client.post(reverse("edit_profile"), payload)

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Old Name")
        self.assertEqual(self.user.username, "nadhif")
        self.assertFalse(self.profile.connections.exists())


class RegistrationViewTests(TestCase):
    def valid_registration_payload(self):
        return {
            "username": "new_user",
            "email": "new@example.com",
            "full_name": "New User",
            "password1": "StrongTestPass123!",
            "password2": "StrongTestPass123!",
        }

    def test_registration_get_displays_form(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertIsInstance(response.context["form"], RegisterForm)

    def test_registration_post_creates_user_profile_and_logs_user_in(self):
        response = self.client.post(reverse("register"), self.valid_registration_payload())

        self.assertRedirects(response, reverse("profile"))
        user = User.objects.get(username="new_user")
        self.assertTrue(user.check_password("StrongTestPass123!"))
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.profile.full_name, "New User")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_registration_rejects_mismatched_passwords(self):
        payload = self.valid_registration_payload()
        payload["password2"] = "DifferentPassword123!"

        response = self.client.post(reverse("register"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new_user").exists())

    def test_authenticated_user_is_redirected_from_registration(self):
        user = User.objects.create_user(username="existing", password="Testpass123!")
        self.client.force_login(user)

        response = self.client.get(reverse("register"))

        self.assertRedirects(response, reverse("profile"))
