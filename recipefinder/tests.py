from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from recipefinder.models import Recipe, RecipeCache
from recipefinder.views import get_recipe_cache
from strip_tags import strip_tags
import html

def escape_html(value):
    return html.escape(str(value if value is not None else ''), quote=True)
raw = {
    "id": 641901,
    "title": "Easy Chicken Pot Pie",
    "image": "https://img.spoonacular.com/recipes/641901-312x231.jpg",
    "summary": "Easy Chicken Pot Pie is a <b>dairy free</b> hor d'oeuvre. For <b>58 cents per serving</b>, this recipe <b>covers 10%</b> of your daily requirements of vitamins and minerals. This recipe serves 6. One serving contains <b>177 calories</b>, <b>5g of protein</b>, and <b>6g of fat</b>. This recipe is liked by 1 foodies and cooks. From preparation to the plate, this recipe takes roughly <b>45 minutes</b>. This recipe from Foodista requires boned chicken, vegetables, cream of chicken, and bisquick. Taking all factors into account, this recipe <b>earns a spoonacular score of 56%</b>, which is solid. If you like this recipe, you might also like recipes such as <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-617704\">Easy Chicken Pot Pie</a>, <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-71564\">Easy Chicken Pot Pie</a>, and <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-288238\">Easy Chicken Pot Pie</a>.",
    "instructions": [
        {
            "name": "",
            "steps": [
                {
                    "number": 1,
                    "step": "Mix first 3 ingredients and pour into a greased baking dish.",
                    "ingredients": [],
                    "equipment": [
                        {
                            "id": 404646,
                            "name": "baking pan",
                            "localizedName": "baking pan",
                            "image": "https://spoonacular.com/cdn/equipment_100x100/roasting-pan.jpg"
                        }
                    ]
                },
                {
                    "number": 2,
                    "step": "Mix Bisquick with water, pour over first mixture and bake in a 400 degree oven for 45 to 50 minutes. (You may use left over chicken or turkey.)",
                    "ingredients": [
                        {
                            "id": 18010,
                            "name": "baking mix",
                            "localizedName": "baking mix",
                            "image": "brown-flour.jpg"
                        },
                        {
                            "id": 0,
                            "name": "chicken",
                            "localizedName": "chicken",
                            "image": "https://spoonacular.com/cdn/ingredients_100x100/whole-chicken.jpg"
                        },
                        {
                            "id": 5165,
                            "name": "whole turkey",
                            "localizedName": "whole turkey",
                            "image": "turkey-raw-whole.jpg"
                        },
                        {
                            "id": 14412,
                            "name": "water",
                            "localizedName": "water",
                            "image": "water.png"
                        }
                    ],
                    "equipment": [
                        {
                            "id": 404784,
                            "name": "oven",
                            "localizedName": "oven",
                            "image": "https://spoonacular.com/cdn/equipment_100x100/oven.jpg"
                        }
                    ],
                    "length": {
                        "number": 45,
                        "unit": "minutes"
                    }
                }
            ]
        }
    ],
    "nutrients": {
    "nutrients": [
        {
            "name": "Calories",
            "amount": 177.04,
            "unit": "kcal",
            "percentOfDailyNeeds": 8.85
        },
        {
            "name": "Fat",
            "amount": 6.41,
            "unit": "g",
            "percentOfDailyNeeds": 9.86
        },
        {
            "name": "Saturated Fat",
            "amount": 1.73,
            "unit": "g",
            "percentOfDailyNeeds": 10.83
        },
        {
            "name": "Carbohydrates",
            "amount": 25.83,
            "unit": "g",
            "percentOfDailyNeeds": 8.61
        },
        {
            "name": "Net Carbohydrates",
            "amount": 22.58,
            "unit": "g",
            "percentOfDailyNeeds": 8.21
        },
        {
            "name": "Sugar",
            "amount": 2.6,
            "unit": "g",
            "percentOfDailyNeeds": 2.89
        },
        {
            "name": "Cholesterol",
            "amount": 4.59,
            "unit": "mg",
            "percentOfDailyNeeds": 1.53
        },
        {
            "name": "Sodium",
            "amount": 647.43,
            "unit": "mg",
            "percentOfDailyNeeds": 28.15
        },
        {
            "name": "Alcohol",
            "amount": 0,
            "unit": "g",
            "percentOfDailyNeeds": 100
        },
        {
            "name": "Alcohol %",
            "amount": 0,
            "unit": "%",
            "percentOfDailyNeeds": 100
        },
        {
            "name": "Protein",
            "amount": 5.2,
            "unit": "g",
            "percentOfDailyNeeds": 10.4
        },
        {
            "name": "Vitamin A",
            "amount": 3690.47,
            "unit": "IU",
            "percentOfDailyNeeds": 73.81
        },
        {
            "name": "Phosphorus",
            "amount": 174.79,
            "unit": "mg",
            "percentOfDailyNeeds": 17.48
        },
        {
            "name": "Vitamin B1",
            "amount": 0.21,
            "unit": "mg",
            "percentOfDailyNeeds": 13.88
        },
        {
            "name": "Manganese",
            "amount": 0.28,
            "unit": "mg",
            "percentOfDailyNeeds": 13.77
        },
        {
            "name": "Fiber",
            "amount": 3.25,
            "unit": "g",
            "percentOfDailyNeeds": 13.01
        },
        {
            "name": "Folate",
            "amount": 46.57,
            "unit": "µg",
            "percentOfDailyNeeds": 11.64
        },
        {
            "name": "Vitamin B2",
            "amount": 0.17,
            "unit": "mg",
            "percentOfDailyNeeds": 10.07
        },
        {
            "name": "Vitamin B3",
            "amount": 2.01,
            "unit": "mg",
            "percentOfDailyNeeds": 10.03
        },
        {
            "name": "Iron",
            "amount": 1.77,
            "unit": "mg",
            "percentOfDailyNeeds": 9.82
        },
        {
            "name": "Vitamin C",
            "amount": 7.48,
            "unit": "mg",
            "percentOfDailyNeeds": 9.07
        },
        {
            "name": "Copper",
            "amount": 0.17,
            "unit": "mg",
            "percentOfDailyNeeds": 8.41
        },
        {
            "name": "Calcium",
            "amount": 61.83,
            "unit": "mg",
            "percentOfDailyNeeds": 6.18
        },
        {
            "name": "Magnesium",
            "amount": 24.46,
            "unit": "mg",
            "percentOfDailyNeeds": 6.12
        },
        {
            "name": "Potassium",
            "amount": 207.99,
            "unit": "mg",
            "percentOfDailyNeeds": 5.94
        },
        {
            "name": "Vitamin B6",
            "amount": 0.08,
            "unit": "mg",
            "percentOfDailyNeeds": 4.19
        },
        {
            "name": "Selenium",
            "amount": 2.77,
            "unit": "µg",
            "percentOfDailyNeeds": 3.96
        },
        {
            "name": "Zinc",
            "amount": 0.59,
            "unit": "mg",
            "percentOfDailyNeeds": 3.95
        },
        {
            "name": "Vitamin B5",
            "amount": 0.39,
            "unit": "mg",
            "percentOfDailyNeeds": 3.91
        },
        {
            "name": "Vitamin K",
            "amount": 3.39,
            "unit": "µg",
            "percentOfDailyNeeds": 3.23
        },
        {
            "name": "Vitamin E",
            "amount": 0.3,
            "unit": "mg",
            "percentOfDailyNeeds": 2.01
        },
        {
            "name": "Vitamin B12",
            "amount": 0.08,
            "unit": "µg",
            "percentOfDailyNeeds": 1.31
        }
    ],
    "properties": [
        {
            "name": "Glycemic Index",
            "amount": 14.67,
            "unit": ""
        },
        {
            "name": "Glycemic Load",
            "amount": 4.58,
            "unit": ""
        },
        {
            "name": "Inflammation Score",
            "amount": -9,
            "unit": ""
        },
        {
            "name": "Nutrition Score",
            "amount": 10.07782595053963,
            "unit": "%"
        }
    ],
    "flavonoids": [
        {
            "name": "Cyanidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Petunidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Delphinidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Malvidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Pelargonidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Peonidin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Catechin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Epigallocatechin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Epicatechin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Epicatechin 3-gallate",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Epigallocatechin 3-gallate",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Theaflavin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Thearubigins",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Eriodictyol",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Hesperetin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Naringenin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Apigenin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Luteolin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Isorhamnetin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Kaempferol",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Myricetin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Quercetin",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Theaflavin-3,3'-digallate",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Theaflavin-3'-gallate",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Theaflavin-3-gallate",
            "amount": 0,
            "unit": ""
        },
        {
            "name": "Gallocatechin",
            "amount": 0,
            "unit": ""
        }
    ],
},
    "source": "https://www.foodista.com/recipe/M4FWCSF4/pot-pie"
}

class MainTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.client.force_login(self.user) 
        self.recipe = Recipe.objects.create(**raw)
        self.recipe_cache = get_recipe_cache()
    

    def test_find_url_is_accessible(self):
        response = self.client.get(reverse("recipefinder:find_recipe"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "find.html")
        self.assertContains(response, f'data-url="{reverse("recipefinder:input_ingredients")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")
        self.assertEqual(response.status_code, 404)

    def test_recipe_model(self):
        self.assertEqual(self.recipe.title, "Easy Chicken Pot Pie")
        self.assertEqual(self.recipe.id, 641901)
        self.assertEqual(self.recipe.summary, "Easy Chicken Pot Pie is a <b>dairy free</b> hor d'oeuvre. For <b>58 cents per serving</b>, this recipe <b>covers 10%</b> of your daily requirements of vitamins and minerals. This recipe serves 6. One serving contains <b>177 calories</b>, <b>5g of protein</b>, and <b>6g of fat</b>. This recipe is liked by 1 foodies and cooks. From preparation to the plate, this recipe takes roughly <b>45 minutes</b>. This recipe from Foodista requires boned chicken, vegetables, cream of chicken, and bisquick. Taking all factors into account, this recipe <b>earns a spoonacular score of 56%</b>, which is solid. If you like this recipe, you might also like recipes such as <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-617704\">Easy Chicken Pot Pie</a>, <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-71564\">Easy Chicken Pot Pie</a>, and <a href=\"https://spoonacular.com/recipes/easy-chicken-pot-pie-288238\">Easy Chicken Pot Pie</a>.")
        self.assertEqual(self.recipe.image, "https://img.spoonacular.com/recipes/641901-312x231.jpg")
        self.assertEqual(self.recipe.source, "https://www.foodista.com/recipe/M4FWCSF4/pot-pie")
        self.assertEqual(self.recipe.instructions[0].get("steps")[0].get("step"), "Mix first 3 ingredients and pour into a greased baking dish.")
        self.assertEqual(self.recipe.nutrients.get("nutrients")[0].get("name"), "Calories")
    
    def test_input_ingredient_page(self):
        response = self.client.get(reverse("recipefinder:input_ingredients"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "input.html")
        self.assertContains(response, f'action="{reverse('recipefinder:show_recipes')}"')

    def test_recipe_result_with_no_ingredients(self):
            response = self.client.get(f'{reverse("recipefinder:show_recipes")}')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "results.html")
            self.assertContains(response, f'No ingredients were entered')
            self.assertContains(response, f'href="javascript:history.back()"')
            
    def test_recipe_result_with_no_recipes(self):
        response = self.client.get(f'{reverse("recipefinder:show_recipes")}?ingredients=a')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "results.html")
        self.assertContains(response, f'No recipes found for a')
        self.assertContains(response, f'href="javascript:history.back()"')
                
    def test_recipe_result_page_no_cache_with_results(self):
        response = self.client.get(f'{reverse("recipefinder:show_recipes")}?ingredients=chicken')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "results.html")
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, f'<img src="{ self.recipe.image }" alt="{self.recipe.title}" loading="lazy">')
        self.assertContains(response, f'href="{reverse('recipefinder:show_recipe_details', kwargs={"recipe_id":641901})}"')
        self.assertContains(response, f'href="javascript:history.back()"')

    def test_recipe_result_page_cache_with_results(self):
        self.recipe_cache.recipes["recipes:chicken||"] = [raw]
        self.recipe_cache.save()
        response = self.client.get(f'{reverse("recipefinder:show_recipes")}?ingredients=chicken')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "results.html")
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, f'<img src="{ self.recipe.image }" alt="{self.recipe.title}" loading="lazy">')
        self.assertContains(response, f'href="{reverse('recipefinder:show_recipe_details', kwargs={"recipe_id":641901})}"')
        self.assertContains(response, f'href="javascript:history.back()"')
   
    def test_details_page_invalid(self):
        response = self.client.get(f'{reverse("recipefinder:show_recipe_details", kwargs={"recipe_id":123})}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")
        self.assertContains(response, f'Could not find recipe with id 123')
        self.assertContains(response, f'href="javascript:history.back()"')
        
    def test_details_page_valid(self):
        response = self.client.get(f'{reverse("recipefinder:show_recipe_details", kwargs={"recipe_id":self.recipe.id})}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, escape_html(strip_tags(self.recipe.summary)))
        self.assertContains(response, f'<img src="{ self.recipe.image }" alt="{self.recipe.title}">')
        self.assertContains(response, f'href="javascript:history.back()"')