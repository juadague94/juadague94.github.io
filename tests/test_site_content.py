from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SiteContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.es = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.en = (ROOT / "en.html").read_text(encoding="utf-8")

    def test_spanish_hero_keeps_all_services_in_priority_order(self):
        labels = [
            "Compensación (EQ)", "Coaching online", "Asesoría 1:1",
            "Coaching mental", "Entrena en Dominica", "Entrena en San Andrés",
        ]
        positions = [self.es.index(label, self.es.index('<div class="hero-actions">')) for label in labels]
        self.assertEqual(positions, sorted(positions))

    def test_english_hero_keeps_all_services_in_priority_order(self):
        labels = [
            "Equalization (EQ)", "Online coaching", "1:1 consultation",
            "Mental performance", "Train in Dominica", "Train in San Andrés",
        ]
        positions = [self.en.index(label, self.en.index('<div class="hero-actions">')) for label in labels]
        self.assertEqual(positions, sorted(positions))

    def test_school_uses_exact_brand_name(self):
        for page in (self.es, self.en):
            self.assertIn("Freedive San Andres", page)
            self.assertNotIn("Freedive San Andrés", page)

    def test_coaching_copy_is_concrete(self):
        self.assertIn("Cinco sesiones para ordenar tu temporada", self.es)
        self.assertIn("No quiero que termines siguiendo un plan que solo yo entiendo", self.es)
        self.assertIn("Five sessions to organize your season", self.en)
        self.assertIn("I do not want you to end up following a plan that only I understand", self.en)

    def test_school_copy_explains_team_and_preparation(self):
        self.assertIn("No depende de que yo esté en cada sesión", self.es)
        self.assertIn("El entrenamiento empieza antes de llegar a la isla", self.es)
        self.assertIn("It does not depend on me being present at every session", self.en)
        self.assertIn("Training starts before you arrive on the island", self.en)

    def test_smiling_student_photo_is_only_in_coaching(self):
        for page in (self.es, self.en):
            eq = page[page.index('id="eq-online"'):page.index('id="coaching-online"')]
            coaching = page[page.index('id="coaching-online"'):page.index('id="asesoria-online"')]
            self.assertNotIn("sonriente en el agua", eq)
            self.assertNotIn("relaxed and smiling", eq)
            self.assertEqual(
                coaching.count("sonriente en el agua") + coaching.count("relaxed and smiling"),
                1,
            )

    def test_no_literal_newline_escape_tokens(self):
        for page in (self.es, self.en):
            self.assertIsNone(re.search(r">\\n|\\n<", page))

    def test_metadata_uses_short_public_url(self):
        for page in (self.es, self.en):
            self.assertNotIn("juadague94.github.io/drfish/", page)
        self.assertIn('href="https://juadague94.github.io/" rel="canonical"', self.es)
        self.assertIn('href="https://juadague94.github.io/en.html" rel="canonical"', self.en)

    def test_all_internal_section_links_have_a_target(self):
        for page in (self.es, self.en):
            targets = set(re.findall(r'\bid="([^"]+)"', page))
            links = re.findall(r'href="#([^"]+)"', page)
            self.assertEqual([], sorted({link for link in links if link not in targets}))

    def test_legacy_instagram_url_redirects_to_public_root(self):
        redirect_path = ROOT / "drfish" / "index.html"
        self.assertTrue(redirect_path.is_file())
        redirect = redirect_path.read_text(encoding="utf-8")
        self.assertIn('http-equiv="refresh" content="0; url=https://juadague94.github.io/"', redirect)
        self.assertIn('href="https://juadague94.github.io/" rel="canonical"', redirect)

    def test_eq_courses_path_serves_the_dedicated_landing(self):
        landing_path = ROOT / "eq-cursos" / "index.html"
        self.assertTrue(landing_path.is_file())
        body = landing_path.read_text(encoding="utf-8")
        self.assertIn("Cursos de compensación EQ · Dr.Fish", body)
        for section_id in ("basica", "intermedia", "avanzada"):
            self.assertIn(f'id="{section_id}"', body)

    def test_github_pages_serves_plain_static_files(self):
        self.assertTrue((ROOT / ".nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()
