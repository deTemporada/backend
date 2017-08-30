from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from filer.models import Image
import urllib.request as req
from decimal import Decimal

import json
from api.models import Recipe, Product, Ingredient, RecipeTag, TaggedRecipe, Unit

class Command(BaseCommand):
    help = 'import products from a json'
    def add_arguments(self, parser):
            # Positional arguments
            parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        # ...
        print("importing file =>", options['filename'][0])

        with open(options['filename'][0], "r") as data:
            rows = json.load(data)
            print("start importing file")
            recipes = 0
            for row in rows:
                if row['recipeIngredient']:
                    print(row)
                    recipes += 1
                    user = User.objects.get(username='ciaran')
                    
                    if row['image']:
                        image_split = row['image'].split("/")
                        image_name = image_split[len(image_split)-1]
                        image = Image.objects.create(
                            owner=user,
                            original_filename=image_name,
                            file=File(ContentFile(req.urlopen(row['image']).read()), image_name)
                            )
                        print("Image created")
                        print(image)
                    
                    category, created = RecipeTag.objects.get_or_create(name=row['category'])
                    print("Category %s created? %s" % (category, created))
                    
                    if not row['subcategory']:
                        subcategory = category
                        print("No subcategory, using category %s" % category)
                    else:
                        subcategory, created = RecipeTag.objects.get_or_create(
                            name=row['subcategory'], 
                            parent=category
                        )
                        print("Subcategory %s created? %s" % (subcategory, created))
                    
                    recipe, created = Recipe.objects.get_or_create(
                        name = row['name'], 
                        introduction = row['description'],
                        instructions = row['recipeInstructions'],
                        author = "GialloZafferano",
                        source = row['link'],
                        preparation_time = 0 if row['prepTime'] == '' else row['prepTime'],
                        cooking_time = 0 if row['totalTime'] == '' else row['totalTime'],
                        recipe_yield = 0 if row['recipeYield'] == '' else row['recipeYield'],
                        rating = row['aggregateRating'] if "aggregateRating" in row.keys() else 0,
                        image = image
                    )
                    print("Recipe %s created? %s" % (recipe, created))
                    taggedrecipe, created = TaggedRecipe.objects.get_or_create(content_object=recipe, tag=subcategory)
                    
                    for recipe_ingredient in row['recipeIngredient']:
                        product, created = Product.objects.get_or_create(name=recipe_ingredient['ingredient'])
                        print("Product %s created? %s" % (product, created))
                        if recipe_ingredient['unit']:
                            unit, created = Unit.objects.get_or_create(name=recipe_ingredient['unit'])
                            print("Unit %s created? %s" % (unit, created))
                            ingredient, created = Ingredient.objects.get_or_create(
                                product=product, 
                                recipe=recipe, 
                                extra=recipe_ingredient['extra'], 
                                quantity=recipe_ingredient['quantity'], 
                                unit=unit
                            )
                        else:
                            ingredient, created = Ingredient.objects.get_or_create(
                                product=product, 
                                recipe=recipe, 
                                extra=recipe_ingredient['extra'], 
                                quantity=recipe_ingredient['quantity']
                            )

                        print("Ingredient %s created? %s" % (ingredient, created))
            print("end importing file, imported %d recipes" % recipes)