from rest_framework import generics
from .serializers import RecipeSerializer, AutocompleteProductSerializer, AutocompleteRecipeSerializer
from .models import Recipe, Ingredient, Product

class RecipeView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Recipe.objects.all()[:10]
    serializer_class = RecipeSerializer
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('name', 'description', 'instructions', 'ingredients')

    def perform_create(self, serializer):
        serializer.save()

class RecipeDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = 'slug'

    def perform_update(self, serializer):
        new_ingredients = serializer.validated_data.pop('ingredients')
        recipe = serializer.instance
        old_ingredients = Ingredient.objects.filter(recipe=recipe).iterator()

        for old_ingredient in old_ingredients:
            if old_ingredient.product not in new_ingredients:
                old_ingredient.delete()

        for new_ingredient in new_ingredients:
            obj, created = Ingredient.objects.get_or_create(
                product = new_ingredient,
                recipe = recipe
                )
        serializer.save()

class AutocompleteProductView(generics.ListAPIView):
    serializer_class = AutocompleteProductSerializer

    def get_queryset(self):
        qs = Product.objects.all().values('name', 'id')
        q = self.request.query_params.get('q', None)
        lookup_regex = r'(%s)' % q
        if q is not None and len(q) > 2:
            qs = qs.filter(name__iregex=lookup_regex)
            return qs[:10]

class AutocompleteRecipeView(generics.ListAPIView):
    serializer_class = AutocompleteRecipeSerializer

    def get_queryset(self):
        qs = Recipe.objects.all().values('name', 'id')
        q = self.request.query_params.get('q', None)
        lookup_regex = r'(%s)' % q
        if q is not None and len(q) > 2:
            qs = qs.filter(name__iregex=lookup_regex)
            return qs[:10]

"""class AutocompleteView(generics.ListAPIView):
    serializer_class = AutocompleteRecipeSerializer

    def get_queryset(self):
        qs1 = Recipe.objects.all().values('name', 'id')
        qs2 = Product.objects.all().values('name', 'id')
        q = self.request.query_params.get('q', None)
        lookup_regex = r'(%s)' % q
        if q is not None and len(q) > 2:
            qs1 = qs1.filter(name__iregex=lookup_regex)
        if q is not None and len(q) > 2:
            qs2 = qs2.filter(name__iregex=lookup_regex)
        qs1.union(qs2)

        return qs1[:10]"""

class SearchRecipeByIngredientsView(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        qs = Recipe.objects.all()
        yes_ingredients = self.request.query_params.get('y', None)
        no_ingredients = self.request.query_params.get('n', None)
        if yes_ingredients is not None:
            for yes_ingredient in yes_ingredients.split("|"):
                qs = qs.filter(ingredients__product=yes_ingredient)
        if no_ingredients is not None:
            for no_ingredient in no_ingredients:
                qs = qs.exclude(ingredients__product=no_ingredient)

        return qs[:10]


