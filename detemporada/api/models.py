from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from datetime import datetime
from taggit.models import TagBase, ItemBase
from taggit.managers import TaggableManager
from django_extensions.db.fields import AutoSlugField

class StandardMetadata(models.Model):
    """
    A basic (abstract) model for metadata.
    Subclass new models from 'StandardMetadata' instead of 'models.Model'.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class ProductTag(TagBase):
    parent = models.ForeignKey('self', null=True, blank=True)
    
    class Meta:
        verbose_name = _('categoria del prodotto')
        verbose_name_plural = _('categorie dei prodotti')

class TaggedProduct(ItemBase):
    content_object = models.ForeignKey('Product')
    tag = models.ForeignKey('ProductTag', related_name='product_tags')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()

class RecipeTag(TagBase):
    parent = models.ForeignKey('self', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('categoria della ricetta')
        verbose_name_plural = _('categorie delle ricette')

class TaggedRecipe(ItemBase):
    content_object = models.ForeignKey('Recipe')
    tag = models.ForeignKey('RecipeTag', related_name='recipe_tags')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()
    
class Product(StandardMetadata):
    """Class represents the Products Model"""
    name = models.CharField(_('nome'), max_length=255, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=50, help_text=_("Lascia vuoto per crearne uno automaticamente."))
    description = models.TextField(_('descrizione'), blank=True)
    tags = TaggableManager(through=TaggedProduct, blank=True)
    image = FilerImageField(null=True, blank=True, related_name="product_image")
    # Afegir temporada field

    class Meta:
        verbose_name = _('prodotto')
        verbose_name_plural = _('prodotti')

class Season(StandardMetadata):
    """Class represents the intervals an product is in season"""
    start = models.DateField(_('inizio'), db_index=True)
    end = models.DateField(_('fine'), db_index=True, help_text=_('La data iniziale deve precedere quella finale.'))
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return self.product + ': ' + self.start.isoformat() + ' - ' + self.end.isoformat()

    class Meta:
        verbose_name = _('stagione')
        verbose_name_plural = _('stagioni')

class Recipe(StandardMetadata):
    """Class represents a recipe"""
    name = models.CharField(_("nome"), max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=50, help_text=_("Lascia vuoto per crearne uno automaticamente."))
    introduction = models.TextField(_('introduzione'), blank=True)
    instructions = models.TextField(_('preparazione'), blank=True)
    author = models.CharField(_("autore"), max_length=50, blank=True)
    source = models.URLField(_("fonte"), max_length=255)
    tags = TaggableManager(through=TaggedRecipe, blank=True)
    preparation_time = models.PositiveSmallIntegerField(_('tempo di preparazione'))
    cooking_time = models.PositiveSmallIntegerField(_('tempo di cottura'))
    recipe_yield = models.PositiveSmallIntegerField(_('dose'))
    rating = models.DecimalField(_('rating'), max_digits=2, decimal_places=1)
    image = FilerImageField(null=True, blank=True, related_name="recipe_image")
    
    class Meta:
        verbose_name = _('ricetta')
        verbose_name_plural = _('ricette')

    @models.permalink
    def get_absolute_url(self):
        return ('RecipeDetails', [self.slug])

    def get_image_absolute_url(self):
        return self.image.url if self.image else None

    def get_ingredients(self):
        return Ingredient.objects.get(recipe=self)


class Ingredient(StandardMetadata):
    """Class represents the Products Model"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ingredient_product')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='ingredients')
    extra = models.CharField(_('informazione complementaria'), max_length=255, blank=True)
    quantity = models.CharField(_('quantità'), max_length=255, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='+', null=True)
    
    class Meta:
        verbose_name = _('ingrediente')
        verbose_name_plural = _('ingredienti')

    def __str__(self):
        return self.product.name + ' (' + self.extra + ') ' + self.quantity + ' ' + str(self.unit)

    def __unicode__(self):
        return '%s (%s) %d %d' % (self.product.name, self.extra, self.quantity, self.unit)

class Unit(StandardMetadata):
    name = models.CharField(_("nome"), max_length=255, unique=True)
    plural = models.CharField(_("plurale"), max_length=255, default=name)

    class Meta:
        verbose_name = _('unità')
        verbose_name_plural = _('unità')