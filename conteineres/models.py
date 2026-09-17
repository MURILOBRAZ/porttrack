from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .validators import validar_numero_conteiner


class TimeStampedModel(models.Model):
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True


class Cliente(TimeStampedModel):
    nome = models.CharField("nome", max_length=120, unique=True)
    documento = models.CharField("CNPJ/CPF", max_length=18, blank=True)
    email = models.EmailField("e-mail", blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("cliente_detail", args=[self.pk])


class Conteiner(TimeStampedModel):
    class Tipo(models.TextChoices):
        VINTE = "20", "20 pés"
        QUARENTA = "40", "40 pés"

    class Status(models.TextChoices):
        CHEIO = "cheio", "Cheio"
        VAZIO = "vazio", "Vazio"

    class Categoria(models.TextChoices):
        IMPORTACAO = "importacao", "Importação"
        EXPORTACAO = "exportacao", "Exportação"

    numero = models.CharField(
        "número",
        max_length=11,
        unique=True,
        validators=[validar_numero_conteiner],
        help_text="Código ISO 6346, ex.: CSQU3054383",
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="conteineres", verbose_name="cliente")
    tipo = models.CharField("tipo", max_length=2, choices=Tipo.choices)
    status = models.CharField("status", max_length=5, choices=Status.choices)
    categoria = models.CharField("categoria", max_length=10, choices=Categoria.choices)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "contêiner"
        verbose_name_plural = "contêineres"
        indexes = [models.Index(fields=["status", "categoria"])]

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        self.numero = (self.numero or "").strip().upper()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("conteiner_detail", args=[self.pk])


class MovimentacaoQuerySet(models.QuerySet):
    def em_andamento(self):
        return self.filter(data_fim__isnull=True)

    def finalizadas(self):
        return self.filter(data_fim__isnull=False)


class Movimentacao(TimeStampedModel):
    class Tipo(models.TextChoices):
        EMBARQUE = "embarque", "Embarque"
        DESEMBARQUE = "desembarque", "Desembarque"
        GATE_IN = "gate_in", "Gate In"
        GATE_OUT = "gate_out", "Gate Out"
        REPOSICIONAMENTO = "reposicionamento", "Reposicionamento"
        PESAGEM = "pesagem", "Pesagem"
        SCANNER = "scanner", "Scanner"

    conteiner = models.ForeignKey(
        Conteiner, on_delete=models.CASCADE, related_name="movimentacoes", verbose_name="contêiner"
    )
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices)
    data_inicio = models.DateTimeField("início")
    data_fim = models.DateTimeField("fim", null=True, blank=True, help_text="Deixe em branco se estiver em andamento.")
    observacao = models.TextField("observação", blank=True)

    objects = MovimentacaoQuerySet.as_manager()

    class Meta:
        ordering = ["-data_inicio"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=models.F("data_inicio")),
                name="movimentacao_fim_apos_inicio",
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.conteiner.numero}"

    def clean(self):
        super().clean()
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValidationError({"data_fim": "A data de fim não pode ser anterior à data de início."})

    @property
    def em_andamento(self) -> bool:
        return self.data_fim is None
