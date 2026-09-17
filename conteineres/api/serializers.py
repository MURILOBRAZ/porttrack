from rest_framework import serializers

from ..models import Cliente, Conteiner, Movimentacao


class ClienteSerializer(serializers.ModelSerializer):
    total_conteineres = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cliente
        fields = ["id", "nome", "documento", "email", "total_conteineres", "criado_em", "atualizado_em"]
        read_only_fields = ["criado_em", "atualizado_em"]


class ConteinerSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    categoria_display = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = Conteiner
        fields = [
            "id",
            "numero",
            "cliente",
            "cliente_nome",
            "tipo",
            "tipo_display",
            "status",
            "status_display",
            "categoria",
            "categoria_display",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]

    def validate_numero(self, value):
        return value.strip().upper()


class MovimentacaoSerializer(serializers.ModelSerializer):
    conteiner_numero = serializers.CharField(source="conteiner.numero", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    em_andamento = serializers.BooleanField(read_only=True)

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "conteiner",
            "conteiner_numero",
            "tipo",
            "tipo_display",
            "data_inicio",
            "data_fim",
            "em_andamento",
            "observacao",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]

    def validate(self, attrs):
        inicio = attrs.get("data_inicio", getattr(self.instance, "data_inicio", None))
        fim = attrs.get("data_fim", getattr(self.instance, "data_fim", None))
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError({"data_fim": "A data de fim não pode ser anterior à data de início."})
        return attrs


class RelatorioClienteSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    cliente = serializers.CharField()
    por_tipo = serializers.DictField(child=serializers.IntegerField())
    total = serializers.IntegerField()
    importacao = serializers.IntegerField()
    exportacao = serializers.IntegerField()
