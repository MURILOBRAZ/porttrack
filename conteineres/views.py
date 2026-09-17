import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, DetailView, TemplateView, UpdateView
from django_filters.views import FilterView

from . import services
from .filters import ConteinerFilter, MovimentacaoFilter
from .forms import ClienteForm, ConteinerForm, MovimentacaoForm
from .models import Cliente, Conteiner, Movimentacao


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "conteineres/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["indicadores"] = services.indicadores_gerais()
        ctx["chart_por_tipo"] = services.movimentacoes_por_tipo()
        ctx["chart_por_dia"] = services.movimentacoes_por_dia(30)
        ctx["ultimas_movimentacoes"] = Movimentacao.objects.select_related("conteiner__cliente")[:8]
        return ctx


# ---------------------------------------------------------------- Clientes


class ClienteListView(LoginRequiredMixin, FilterView):
    model = Cliente
    template_name = "conteineres/cliente_list.html"
    paginate_by = 15
    filterset_fields = {"nome": ["icontains"]}

    def get_queryset(self):
        return Cliente.objects.annotate(total_conteineres=Count("conteineres")).order_by("nome")


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "conteineres/cliente_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["conteineres"] = self.object.conteineres.annotate(total_movimentacoes=Count("movimentacoes")).order_by(
            "numero"
        )
        return ctx


class ClienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "conteineres/form.html"
    success_message = "Cliente “%(nome)s” cadastrado com sucesso."
    extra_context = {"titulo": "Novo cliente", "voltar": reverse_lazy("cliente_list")}


class ClienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "conteineres/form.html"
    success_message = "Cliente “%(nome)s” atualizado."
    extra_context = {"titulo": "Editar cliente", "voltar": reverse_lazy("cliente_list")}


class ProtectedDeleteView(LoginRequiredMixin, DeleteView):
    """DeleteView que trata ProtectedError exibindo uma mensagem amigável."""

    template_name = "conteineres/confirm_delete.html"
    protected_message = "Este registro não pode ser excluído porque possui dados vinculados."
    success_message = "Registro excluído."

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.object.get_absolute_url())
        messages.success(self.request, self.success_message)
        return response


class ClienteDeleteView(ProtectedDeleteView):
    model = Cliente
    success_url = reverse_lazy("cliente_list")
    protected_message = "Não é possível excluir um cliente que possui contêineres cadastrados."
    success_message = "Cliente excluído."


# ------------------------------------------------------------- Contêineres


class ConteinerListView(LoginRequiredMixin, FilterView):
    model = Conteiner
    filterset_class = ConteinerFilter
    template_name = "conteineres/conteiner_list.html"
    paginate_by = 15

    def get_queryset(self):
        return (
            Conteiner.objects.select_related("cliente")
            .annotate(total_movimentacoes=Count("movimentacoes"))
            .order_by("-criado_em")
        )


class ConteinerDetailView(LoginRequiredMixin, DetailView):
    model = Conteiner
    template_name = "conteineres/conteiner_detail.html"

    def get_queryset(self):
        return Conteiner.objects.select_related("cliente")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["movimentacoes"] = self.object.movimentacoes.all()
        return ctx


class ConteinerCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Conteiner
    form_class = ConteinerForm
    template_name = "conteineres/form.html"
    success_message = "Contêiner %(numero)s cadastrado com sucesso."
    extra_context = {"titulo": "Novo contêiner", "voltar": reverse_lazy("conteiner_list")}

    def get_initial(self):
        initial = super().get_initial()
        if cliente := self.request.GET.get("cliente"):
            initial["cliente"] = cliente
        return initial


class ConteinerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Conteiner
    form_class = ConteinerForm
    template_name = "conteineres/form.html"
    success_message = "Contêiner %(numero)s atualizado."
    extra_context = {"titulo": "Editar contêiner", "voltar": reverse_lazy("conteiner_list")}


class ConteinerDeleteView(ProtectedDeleteView):
    model = Conteiner
    success_url = reverse_lazy("conteiner_list")
    success_message = "Contêiner excluído."


# ----------------------------------------------------------- Movimentações


class MovimentacaoListView(LoginRequiredMixin, FilterView):
    model = Movimentacao
    filterset_class = MovimentacaoFilter
    template_name = "conteineres/movimentacao_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Movimentacao.objects.select_related("conteiner__cliente")


class MovimentacaoSuccessUrlMixin:
    def get_success_url(self):
        return self.object.conteiner.get_absolute_url()


class MovimentacaoCreateView(LoginRequiredMixin, SuccessMessageMixin, MovimentacaoSuccessUrlMixin, CreateView):
    model = Movimentacao
    form_class = MovimentacaoForm
    template_name = "conteineres/form.html"
    success_message = "Movimentação registrada."
    extra_context = {"titulo": "Nova movimentação", "voltar": reverse_lazy("movimentacao_list")}

    def get_initial(self):
        initial = super().get_initial()
        initial["data_inicio"] = timezone.localtime().replace(second=0, microsecond=0)
        if conteiner := self.request.GET.get("conteiner"):
            initial["conteiner"] = conteiner
        return initial


class MovimentacaoUpdateView(LoginRequiredMixin, SuccessMessageMixin, MovimentacaoSuccessUrlMixin, UpdateView):
    model = Movimentacao
    form_class = MovimentacaoForm
    template_name = "conteineres/form.html"
    success_message = "Movimentação atualizada."
    extra_context = {"titulo": "Editar movimentação", "voltar": reverse_lazy("movimentacao_list")}


class MovimentacaoDeleteView(ProtectedDeleteView):
    model = Movimentacao
    success_url = reverse_lazy("movimentacao_list")
    success_message = "Movimentação excluída."


class MovimentacaoFinalizarView(LoginRequiredMixin, DetailView):
    """Encerra uma movimentação em andamento (POST)."""

    model = Movimentacao
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        movimentacao = self.get_object()
        if movimentacao.em_andamento:
            movimentacao.data_fim = max(timezone.now(), movimentacao.data_inicio)
            movimentacao.save(update_fields=["data_fim", "atualizado_em"])
            messages.success(request, f"Movimentação “{movimentacao}” finalizada.")
        next_url = request.POST.get("next")
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = movimentacao.conteiner.get_absolute_url()
        return redirect(next_url)


# --------------------------------------------------------------- Relatório


class RelatorioView(LoginRequiredMixin, TemplateView):
    template_name = "conteineres/relatorio.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tipos"] = Movimentacao.Tipo.choices
        ctx["linhas"] = services.relatorio_por_cliente()
        ctx["indicadores"] = services.indicadores_gerais()
        return ctx


class RelatorioCsvView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorio-movimentacoes-{timezone.localdate():%Y%m%d}.csv"'
        )
        response.write("﻿")  # BOM para o Excel reconhecer UTF-8
        writer = csv.writer(response, delimiter=";")
        tipos = Movimentacao.Tipo.choices
        writer.writerow(["Cliente", *[label for _, label in tipos], "Total", "Importação", "Exportação"])
        for linha in services.relatorio_por_cliente():
            writer.writerow(
                [
                    linha["cliente"],
                    *[linha["por_tipo"][valor] for valor, _ in tipos],
                    linha["total"],
                    linha["importacao"],
                    linha["exportacao"],
                ]
            )
        return response
