from django import forms

from .models import Cliente, Conteiner, Movimentacao


class BootstrapFormMixin:
    """Aplica as classes CSS do Bootstrap 5 a todos os campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css = "form-select"
            elif isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            else:
                css = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()

    def full_clean(self):
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} is-invalid".strip()


class ClienteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "documento", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Nome ou razão social"}),
            "documento": forms.TextInput(attrs={"placeholder": "00.000.000/0000-00"}),
            "email": forms.EmailInput(attrs={"placeholder": "contato@empresa.com"}),
        }


class ConteinerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Conteiner
        fields = ["numero", "cliente", "tipo", "status", "categoria"]
        widgets = {
            "numero": forms.TextInput(
                attrs={"placeholder": "CSQU3054383", "style": "text-transform: uppercase", "maxlength": 11}
            ),
        }

    def clean_numero(self):
        return self.cleaned_data["numero"].strip().upper()


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%dT%H:%M", **kwargs)


class MovimentacaoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ["conteiner", "tipo", "data_inicio", "data_fim", "observacao"]
        widgets = {
            "data_inicio": DateTimeLocalInput(),
            "data_fim": DateTimeLocalInput(),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["conteiner"].queryset = Conteiner.objects.select_related("cliente")
