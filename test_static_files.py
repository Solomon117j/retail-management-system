import unittest
import requests

class StaticFilesTest(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/static/"

    def test_main_css(self):
        url = self.BASE_URL + "css/main.css"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Footer Styling", response.text)

    def test_style_css(self):
        url = self.BASE_URL + "css/style.css"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(".footer-title", response.text)

    def test_main_js(self):
        url = self.BASE_URL + "js/main.js"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("function", response.text)

    def test_image_browneye(self):
        url = self.BASE_URL + "images/BrownEye.png"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/png')

    def test_dashboards_main_css(self):
        url = self.BASE_URL.replace("/static/", "/static/dashboards/styles/") + "main.css"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("body", response.text)

    def test_dashboards_main_js(self):
        url = self.BASE_URL.replace("/static/", "/static/dashboards/js/") + "main.js"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("function", response.text)

    def test_dashboards_image_art(self):
        url = self.BASE_URL.replace("/static/", "/static/dashboards/images/") + "art.jpeg"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/jpeg')

    def test_ecommerce_css(self):
        url = self.BASE_URL.replace("/static/", "/static/e_commerce/styles/") + "e_commerce.css"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("body", response.text)

if __name__ == "__main__":
    unittest.main()
