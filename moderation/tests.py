from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from FillMyDish.models import User
from moderation.models import SuspiciousRequest


class LogsPageTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        cls.browser = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.moderator = User.objects.create_user(username="testmod", password="pass12345", is_moderator=True)
        self.random_user = User.objects.create_user(username="testuser", password="pass12345")
        self.suspicious = SuspiciousRequest.objects.create(
            user=self.random_user, arguments=["affghjkghj"]
        )
        self.login(self.moderator)

    def login(self, user):
        # force_login creates the session in the DB; copy its cookie into the browser
        self.client.force_login(user)
        cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.browser.get(self.live_server_url)        # the cookie needs a page on the domain first
        self.browser.delete_all_cookies()
        self.browser.add_cookie({
            "name": settings.SESSION_COOKIE_NAME,
            "value": cookie.value,
            "path": "/",
        })

    def open_logs(self):
        self.browser.get(self.live_server_url + reverse("moderation:show_logs"))

    def wait_for_list_text(self, text):
        # "Loading..." shows first, so wait until htmx has swapped in the real content
        self.wait.until(EC.text_to_be_present_in_element((By.ID, "review-list"), text))

    def test_no_suspicious(self):
        SuspiciousRequest.objects.all().delete()
        self.open_logs()
        self.wait_for_list_text("No suspicious requests yet")

    def test_shows_suspicious_request(self):
        self.open_logs()
        self.wait_for_list_text("affghjkghj")
        card = self.browser.find_element(By.CSS_SELECTOR, "#review-list .review-card")
        self.assertIn("testuser", card.text)
        self.assertNotIn("Loading...", self.browser.find_element(By.ID, "review-list").text)

    def test_review_link_points_to_review_page(self):
        self.open_logs()
        link = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#review-list .review-card__actions a")
        ))
        self.assertIn(
            reverse("moderation:review", args=[self.suspicious.pk]),
            link.get_attribute("href"),
        )
    def test_anonymous_redirected_to_login(self):
        self.browser.delete_all_cookies()                      # log out
        self.browser.get(self.live_server_url + reverse("moderation:show_logs"))

        self.wait.until(EC.url_contains(reverse("login")))
        self.assertIn("next=", self.browser.current_url) 
    
    def test_login_redirects_to_next(self):
        self.browser.delete_all_cookies()
        next_path = reverse("recipefinder:input_ingredients")
        self.browser.get(f"{self.live_server_url}{reverse('login')}?next={next_path}")
    
        self.browser.find_element(By.NAME, "username").send_keys("testmod")
        self.browser.find_element(By.NAME, "password").send_keys("pass12345")
        self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    
        self.wait.until(EC.url_to_be(self.live_server_url + next_path))
        
    def test_non_mod_redirected_to_main(self):
        self.browser.delete_all_cookies() 
        self.login(self.random_user)
        self.browser.get(self.live_server_url + reverse("moderation:show_logs"))
        self.wait.until(EC.url_contains(reverse("main:show_main")))
    
    def test_flag_review(self):
        badge = (By.CSS_SELECTOR, "#review-list .review-card .review-card__status")

        self.open_logs()
        before = self.wait.until(EC.presence_of_element_located(badge)).text.strip()

        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#review-list .review-card__actions a")
        )).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#modal.is-open")))

        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#modal button[name=status][value=flagged]")
        )).click()

        
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".review-toast"), "Request successfully reviewed"
        ))
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#modal.is-open")))

        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#review-list .review-card__status--flagged")
        ))
        self.assertNotEqual(self.browser.find_element(*badge).text.strip(), before)

        
        self.assertIn("affghjkghj", self.browser.find_element(By.ID, "review-list").text)

        self.suspicious.refresh_from_db()
        self.assertEqual(self.suspicious.status, "flagged")
        
    def test_clear_review(self):
        self.open_logs()
        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#review-list .review-card__actions a")
        )).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#modal.is-open")))
        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#modal button[name=status][value=cleared]")
        )).click()

        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#review-list .review-card__status--cleared")
        ))
        self.suspicious.refresh_from_db()
        self.assertEqual(self.suspicious.status, "cleared")