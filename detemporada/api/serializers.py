from rest_framework import serializers
from .models import Recipe, Ingredient, Product, Unit
from taggit_serializer.serializers import (TagListSerializerField, TaggitSerializer)
from django.utils.translation import ugettext_lazy as _

class IngredientSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    unit = serializers.CharField(source='unit.name')

    class Meta:
        model = Ingredient
        fields = ('product', 'quantity', 'unit', 'extra')

class RecipeSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    tags = TagListSerializerField()
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    image = serializers.CharField(source='get_image_absolute_url', read_only=True)
    #ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all(), allow_null=False)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Recipe
        fields = ('id', 'name', 'slug', 'url', 'created', 'updated', 'introduction', 'instructions', 'image', 'author', 'source', 'tags', 'preparation_time', 'cooking_time', 'recipe_yield', 'rating', 'ingredients')
        read_only_fields = ('slug', 'created', 'updated')
    
    def validate(self, data):
        errors = {}
        error = False
        if any((data['preparation_time'] < 0, data['preparation_time'] > 10000)):
            errors['preparation_time'] = _("Inserire un valore tra 0 e 10000 minuti")
            error = True
            #raise serializers.ValidationError(errors)
        if any((data['cooking_time'] < 0, data['cooking_time'] > 10000)):
            errors['cooking_time'] = _("Inserire un valore tra 0 e 10000 minuti")
            error = True
            #raise serializers.ValidationError(errors)
        if any((data['recipe_yield'] < 1, data['recipe_yield'] > 20)):
            errors['recipe_yield'] = _("Inserire un valore tra 1 e 20 persone")
            error = True
        if any((data['rating'] < 0, data['rating'] > 5)):
            errors['rating'] = _("Inserire un valore tra 0 e 5")
            error = True
        if not data['ingredients']:
            errors['ingredients'] = _("Selezionare al meno un ingrediente")
            error = True
        if error:
            raise serializers.ValidationError(errors)
     
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            product, created = Product.objects.get_or_create(name=ingredient["product"]["name"])
            unit, created = Unit.objects.get_or_create(name=ingredient["unit"]["name"])
            obj, created = Ingredient.objects.get_or_create(
                product = product,
                quantity = ingredient["quantity"],
                unit = unit,
                extra = ingredient["extra"],
                recipe = recipe
                )

        return recipe

class AutocompleteProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name')

class AutocompleteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name')