from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import RecipeView, RecipeDetailsView, AutocompleteProductView, AutocompleteRecipeView, SearchRecipeByIngredientsView, SearchRecipeByNameView

urlpatterns = {
    url(r'^api/recipes/create$', RecipeView.as_view(), name="RecipeCreate"),
    url(r'^api/recipes/(?P<slug>[-\w]+)/$', RecipeDetailsView.as_view(), name="RecipeDetails"),
	url(r'^api/recipes/search$', SearchRecipeByNameView.as_view(), name="RecipeSearch"),
	url(r'^api/recipes/sbi$', SearchRecipeByIngredientsView.as_view(), name="RecipeSBI"),
    url(r'^api/products/autocomplete$', AutocompleteProductView.as_view(), name="AutocompleteProduct"),
    url(r'^api/recipes/autocomplete$', AutocompleteRecipeView.as_view(), name="AutocompleteRecipe"),
}

urlpatterns = format_suffix_patterns(urlpatterns)