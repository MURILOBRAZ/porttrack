import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from conteineres.models import Cliente, Conteiner, Movimentacao
from conteineres.validators import calcular_digito_verificador

CLIENTES = [
    ("Maersk Line Brasil", "12.345.678/0001-90"),
    ("MSC Mediterranean Shipping", "23.456.789/0001-01"),
    ("CMA CGM do Brasil", "34.567.890/0001-12"),
    ("Hapag-Lloyd", "45.678.901/0001-23"),
    ("Cooperativa Agrícola Sul", "56.789.012/0001-34"),
    ("Exportadora Café Minas", "67.890.123/0001-45"),
]
OWNER_CODES = ["MSK", "MSC", "CMA", "HLX", "CAS", "ECM"]


def gerar_numero(owner: str, rng: random.Random) -> str:
    base = f"{owner}U{rng.randint(0, 999999):06d}"
    return f"{base}{calcular_digito_verificador(base)}"


class Command(BaseCommand):
    help = "Popula o banco com dados de demonstração e cria o usuário demo."

    def add_arguments(self, parser):
        parser.add_argument("--conteineres", type=int, default=40)
        parser.add_argument("--reset", action="store_true", help="Apaga os dados existentes antes de popular.")
        parser.add_argument("--seed", type=int, default=42, help="Semente aleatória (resultados reprodutíveis).")
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="demo1234")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(options["seed"])

        if options["reset"]:
            Movimentacao.objects.all().delete()
            Conteiner.objects.all().delete()
            Cliente.objects.all().delete()

        User = get_user_model()
        user, created = User.objects.get_or_create(username=options["username"], defaults={"is_staff": False})
        if created:
            user.set_password(options["password"])
            user.save()
            self.stdout.write(f"Usuário '{user.username}' criado.")

        clientes = [Cliente.objects.get_or_create(nome=nome, defaults={"documento": doc})[0] for nome, doc in CLIENTES]

        agora = timezone.now()
        fluxo = [
            Movimentacao.Tipo.GATE_IN,
            Movimentacao.Tipo.SCANNER,
            Movimentacao.Tipo.PESAGEM,
            Movimentacao.Tipo.REPOSICIONAMENTO,
            Movimentacao.Tipo.EMBARQUE,
        ]
        criados = 0
        for _ in range(options["conteineres"]):
            idx = rng.randrange(len(clientes))
            numero = gerar_numero(OWNER_CODES[idx], rng)
            if Conteiner.objects.filter(numero=numero).exists():
                continue
            categoria = rng.choice(Conteiner.Categoria.values)
            conteiner = Conteiner.objects.create(
                numero=numero,
                cliente=clientes[idx],
                tipo=rng.choice(Conteiner.Tipo.values),
                status=rng.choice(Conteiner.Status.values),
                categoria=categoria,
            )
            criados += 1

            etapas = (
                fluxo
                if categoria == Conteiner.Categoria.EXPORTACAO
                else [
                    Movimentacao.Tipo.DESEMBARQUE,
                    Movimentacao.Tipo.SCANNER,
                    Movimentacao.Tipo.REPOSICIONAMENTO,
                    Movimentacao.Tipo.GATE_OUT,
                ]
            )
            etapas = etapas[: rng.randint(1, len(etapas))]
            inicio = agora - timedelta(days=rng.randint(0, 29), hours=rng.randint(0, 23))
            for tipo in etapas:
                if inicio >= agora:
                    break
                fim = inicio + timedelta(minutes=rng.randint(15, 240))
                em_andamento = fim > agora
                Movimentacao.objects.create(
                    conteiner=conteiner,
                    tipo=tipo,
                    data_inicio=inicio,
                    data_fim=None if em_andamento else fim,
                )
                if em_andamento:
                    break
                inicio = fim + timedelta(hours=rng.randint(1, 12))

        self.stdout.write(
            self.style.SUCCESS(
                f"Pronto: {len(clientes)} clientes, {criados} contêineres novos, "
                f"{Movimentacao.objects.count()} movimentações no total."
            )
        )
