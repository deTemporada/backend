from django.contrib import admin
from .models import Ingredient, Season, Recipe, Product, ProductTag, TaggedProduct, RecipeTag, TaggedRecipe#, IngredientCategory, RecipeCategory

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Season)
admin.site.register(Recipe)
admin.site.register(Product)
admin.site.register(ProductTag)
admin.site.register(TaggedProduct)
admin.site.register(RecipeTag)
admin.site.register(TaggedRecipe)