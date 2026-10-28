from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ReviewForm
from .models import Review

User = get_user_model()
PASSWORD = 'pass12345'


class ReviewTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            'owner', email='owner@example.com', password=PASSWORD
        )
        cls.other = User.objects.create_user('other', password=PASSWORD)
        cls.review = Review.objects.create(user=cls.owner, message='Enak banget')

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password=PASSWORD))



class ReviewModelTests(ReviewTestBase):
    def test_defaults(self):
        self.assertTrue(self.review.is_visible)
        self.assertIsNotNone(self.review.created_at)
        self.assertIsNotNone(self.review.updated_at)

    def test_str_truncates_message(self):
        r = Review.objects.create(user=self.owner, message='x' * 100)
        self.assertEqual(str(r), f'owner - {"x" * 30}')

    def test_str_short_message(self):
        self.assertEqual(str(self.review), 'owner - Enak banget')

    def test_default_ordering_newest_first(self):
        newer = Review.objects.create(user=self.owner, message='baru')
        Review.objects.filter(pk=self.review.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        self.assertEqual(list(Review.objects.all()), [newer, self.review])

    def test_deleting_user_deletes_reviews(self):
        self.owner.delete()
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_related_name(self):
        self.assertIn(self.review, self.owner.reviews.all())



class ReviewFormTests(TestCase):
    def test_valid(self):
        self.assertTrue(ReviewForm(data={'message': 'Mantap'}).is_valid())

    def test_empty_message_invalid(self):
        form = ReviewForm(data={'message': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_whitespace_message_invalid(self):
        self.assertFalse(ReviewForm(data={'message': '   '}).is_valid())

    def test_only_message_field(self):
        self.assertEqual(list(ReviewForm().fields), ['message'])

    def test_placeholder(self):
        widget = ReviewForm().fields['message'].widget
        self.assertEqual(widget.attrs['placeholder'], 'Input Your Message')


class ReviewListViewTests(ReviewTestBase):
    def test_anonymous_can_open(self):
        res = self.client.get(reverse('review:list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'review_list.html')

    def test_context_has_form(self):
        res = self.client.get(reverse('review:list'))
        self.assertIsInstance(res.context['form'], ReviewForm)


class ReviewJsonTests(ReviewTestBase):
    url_name = 'review:json'

    def test_empty_list(self):
        Review.objects.all().delete()
        res = self.client.get(reverse(self.url_name))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_hidden_review_not_returned(self):
        Review.objects.create(user=self.owner, message='hidden', is_visible=False)
        data = self.client.get(reverse(self.url_name)).json()
        self.assertEqual([d['fields']['message'] for d in data], ['Enak banget'])

    def test_newest_first(self):
        Review.objects.create(user=self.other, message='lebih baru')
        Review.objects.filter(pk=self.review.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        data = self.client.get(reverse(self.url_name)).json()
        self.assertEqual(
            [d['fields']['message'] for d in data], ['lebih baru', 'Enak banget']
        )

    def test_structure(self):
        item = self.client.get(reverse(self.url_name)).json()[0]
        self.assertEqual(item['pk'], str(self.review.pk))
        self.assertIsInstance(item['pk'], str)
        self.assertEqual(
            set(item['fields']),
            {
                'user', 'profile_username', 'profile_image', 'profile_url',
                'is_owner', 'message', 'created_at', 'updated_at',
            },
        )
        self.assertEqual(item['fields']['user'], 'owner')

    def test_author_profile_data_uses_safe_defaults(self):
        item = self.client.get(reverse(self.url_name)).json()[0]

        self.assertEqual(item['fields']['profile_username'], 'owner')
        self.assertEqual(item['fields']['profile_image'], '')
        self.assertEqual(item['fields']['profile_url'], reverse('user_profile', args=['owner']))

    def test_is_owner_flag(self):
        self.login('owner')
        data = self.client.get(reverse(self.url_name)).json()
        self.assertTrue(data[0]['fields']['is_owner'])

        self.client.logout()
        self.login('other')
        data = self.client.get(reverse(self.url_name)).json()
        self.assertFalse(data[0]['fields']['is_owner'])

    def test_anonymous_is_not_owner(self):
        data = self.client.get(reverse(self.url_name)).json()
        self.assertFalse(data[0]['fields']['is_owner'])

    def test_no_sensitive_data(self):
        body = self.client.get(reverse(self.url_name)).content.decode()
        self.assertNotIn('owner@example.com', body)
        self.assertNotIn('password', body)

class CreateReviewAjaxTests(ReviewTestBase):
    def setUp(self):
        self.url = reverse('review:create_ajax')

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_gets_401(self):
        res = self.client.post(self.url, {'message': 'hai'})
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['message'], 'Silakan login terlebih dahulu')
        self.assertEqual(Review.objects.count(), 1)

    def test_valid_creates_review(self):
        self.login('other')
        res = self.client.post(self.url, {'message': 'hai'})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Review.objects.count(), 2)
        new = Review.objects.get(pk=res.json()['pk'])
        self.assertEqual(new.user, self.other)
        self.assertEqual(new.message, 'hai')
        self.assertTrue(new.is_visible)
        self.assertEqual(res.json()['message'], 'Review berhasil ditambahkan.')

    def test_empty_message_returns_400(self):
        self.login('other')
        res = self.client.post(self.url, {'message': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('message', res.json()['errors'])
        self.assertEqual(Review.objects.count(), 1)

    def test_cannot_set_user_or_visibility_from_post(self):
        self.login('other')
        res = self.client.post(
            self.url,
            {'message': 'curang', 'user': self.owner.pk, 'is_visible': ''},
        )
        new = Review.objects.get(pk=res.json()['pk'])
        self.assertEqual(new.user, self.other)
        self.assertTrue(new.is_visible)


class UpdateReviewTests(ReviewTestBase):
    def setUp(self):
        self.url = reverse('review:update', args=[self.review.pk])

    def test_anonymous_redirects_to_login(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith('/login'))
        self.assertIn(self.url, res.url)

    def test_owner_get_shows_old_message(self):
        self.login('owner')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'update_review.html')
        self.assertEqual(res.context['form'].instance, self.review)
        self.assertContains(res, 'Enak banget')

    def test_owner_post_valid(self):
        self.login('owner')
        res = self.client.post(self.url, {'message': 'Baru'})
        self.assertRedirects(
            res, reverse('review:list'), fetch_redirect_response=False
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.message, 'Baru')
        msgs = [str(m) for m in res.wsgi_request._messages]
        self.assertIn('Review berhasil diperbarui!', msgs)

    def test_owner_post_empty_keeps_data(self):
        self.login('owner')
        res = self.client.post(self.url, {'message': ''})
        self.assertEqual(res.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.message, 'Enak banget')

    def test_other_user_gets_404(self):
        self.login('other')
        res = self.client.post(self.url, {'message': 'Hack'})
        self.assertEqual(res.status_code, 404)
        self.review.refresh_from_db()
        self.assertEqual(self.review.message, 'Enak banget')

    def test_nonexistent_pk_404(self):
        self.login('owner')
        res = self.client.get(reverse('review:update', args=[9999]))
        self.assertEqual(res.status_code, 404)


# ---------------------------------------------------------------- delete
class DeleteReviewTests(ReviewTestBase):
    def setUp(self):
        self.url = reverse('review:delete', args=[self.review.pk])

    def exists(self):
        return Review.objects.filter(pk=self.review.pk).exists()

    def test_anonymous_redirects_and_data_stays(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith('/login'))
        self.assertTrue(self.exists())

    def test_get_not_allowed(self):
        self.login('owner')
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertTrue(self.exists())

    def test_owner_can_delete(self):
        self.login('owner')
        res = self.client.post(self.url)
        self.assertRedirects(
            res, reverse('review:list'), fetch_redirect_response=False
        )
        self.assertFalse(self.exists())
        msgs = [str(m) for m in res.wsgi_request._messages]
        self.assertIn('Review berhasil dihapus!', msgs)

    def test_other_user_gets_404(self):
        self.login('other')
        self.assertEqual(self.client.post(self.url).status_code, 404)
        self.assertTrue(self.exists())

    def test_nonexistent_pk_404(self):
        self.login('owner')
        res = self.client.post(reverse('review:delete', args=[9999]))
        self.assertEqual(res.status_code, 404)


# ---------------------------------------------------------------- URL
class ReviewUrlTests(TestCase):
    def test_reverse_paths(self):
        self.assertEqual(reverse('review:list'), '/review/')
        self.assertEqual(reverse('review:json'), '/review/json/')
        self.assertEqual(reverse('review:create_ajax'), '/review/create-ajax/')
        self.assertEqual(reverse('review:update', args=[1]), '/review/1/update/')
        self.assertEqual(reverse('review:delete', args=[1]), '/review/1/delete/')


# ---------------------------------------------------------------- Keamanan
class ReviewSecurityTests(ReviewTestBase):
    def test_script_stored_and_returned_as_is(self):
        self.login('other')
        payload = '<script>alert(1)</script>'
        self.client.post(reverse('review:create_ajax'), {'message': payload})
        data = self.client.get(reverse('review:json')).json()
        self.assertIn(payload, [d['fields']['message'] for d in data])

    def test_csrf_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.login(username='other', password=PASSWORD)
        res = client.post(reverse('review:create_ajax'), {'message': 'hai'})
        self.assertEqual(res.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)
