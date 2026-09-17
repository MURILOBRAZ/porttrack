import django_filters
from django import forms
from django.db.models import Q

from .forms import BootstrapFormMixin
from .models import Cliente, Conteiner, Movimentacao


class BootstrapFilterForm(BootstrapFormMixin, forms.Form):
    pass


class ConteinerFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="buscar", label="Buscar", widget=forms.TextInput(attrs={"placeholder": "Número ou cliente"})
    )
    cliente = django_filters.ModelChoiceFilter(queryset=Cliente.objects.all())

    class Meta:
        model = Conteiner
        form = BootstrapFilterForm
        fields = ["q", "cliente", "tipo", "status", "categoria"]

    def buscar(self, queryset, name, value):
        return queryset.filter(Q(numero__icontains=value) | Q(cliente__nome__icontains=value))


class MovimentacaoFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method="buscar", label="Buscar", widget=forms.TextInput(attrs={"placeholder": "Número ou cliente"})
    )
    cliente = django_filters.ModelChoiceFilter(field_name="conteiner__cliente", queryset=Cliente.objects.all())
    data_inicio_de = django_filters.DateFilter(
        field_name="data_inicio", lookup_expr="date__gte", label="De", widget=forms.DateInput(attrs={"type": "date"})
    )
    data_inicio_ate = django_filters.DateFilter(
        field_name="data_inicio", lookup_expr="date__lte", label="Até", widget=forms.DateInput(attrs={"type": "date"})
    )
    em_andamento = django_filters.BooleanFilter(field_name="data_fim", lookup_expr="isnull", label="Em andamento")

    class Meta:
        model = Movimentacao
        form = BootstrapFilterForm
        fields = ["q", "cliente", "conteiner", "tipo", "data_inicio_de", "data_inicio_ate", "em_andamento"]

    def buscar(self, queryset, name, value):
        return queryset.filter(Q(conteiner__numero__icontains=value) | Q(conteiner__cliente__nome__icontains=value))
