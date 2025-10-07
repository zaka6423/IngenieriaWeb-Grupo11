from haystack import indexes
from .models import Comedor

class ComedorIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    nombre = indexes.CharField(model_attr='nombre')
    barrio = indexes.CharField(model_attr='barrio')

    def get_model(self):
        return Comedor