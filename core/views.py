from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from analytics.analysis import resumo_financeiro
from .forms import (
    CategoriaForm,
    ContaForm,
    EdicaoCategoriaForm,
    EdicaoContaForm,
    EdicaoTransacaoForm,
    TransacaoForm,
)
from .models import Categoria, Conta, Transacao


FORMULARIOS_CADASTRO = {
    'transacao': TransacaoForm,
    'categoria': CategoriaForm,
    'contas': ContaForm,
}
FORMULARIOS_EDICAO = {
    'editar_transacao': (Transacao, 'tran_id', EdicaoTransacaoForm),
    'editar_conta': (Conta, 'conta_id', EdicaoContaForm),
    'editar_categoria': (Categoria, 'categoria_id', EdicaoCategoriaForm),
}
MODELOS_EXCLUSAO = {
    'excluir_transacao': (Transacao, 'tran_id'),
    'excluir_conta': (Conta, 'conta_id'),
    'excluir_categoria': (Categoria, 'categoria_id'),
}


def financas(request):
    erro_formulario = None
    if request.method == 'POST':
        classe_formulario = FORMULARIOS_CADASTRO.get(request.POST.get('tipo_form'))
        if classe_formulario:
            formulario = classe_formulario(request.POST)
            if formulario.is_valid():
                formulario.save()
                return redirect('home')
            erro_formulario = formulario.errors

    contexto = {
        **resumo_financeiro(),
        'categorias': Categoria.objects.all(),
        'contas': Conta.objects.all(),
        'erro_formulario': erro_formulario,
    }
    return render(request, 'core/home.html', contexto)


def transacoes(request):
    contexto = {
        'categorias': Categoria.objects.all(),
        'contas': Conta.objects.all(),
        'transacoes': Transacao.objects.select_related('categoria', 'conta'),
    }
    return render(request, 'core/transacoes.html', contexto)


def configuracoes(request):
    if request.method == 'POST':
        acao = request.POST.get('tipo_form')

        if acao in FORMULARIOS_EDICAO:
            modelo, campo_id, classe_formulario = FORMULARIOS_EDICAO[acao]
            instancia = get_object_or_404(modelo, pk=request.POST.get(campo_id))
            formulario = classe_formulario(request.POST)
            if formulario.is_valid():
                formulario.save(instancia)
            else:
                messages.error(request, f'Revise os dados informados: {formulario.errors.as_text()}')
        elif acao in MODELOS_EXCLUSAO:
            modelo, campo_id = MODELOS_EXCLUSAO[acao]
            instancia = get_object_or_404(modelo, pk=request.POST.get(campo_id))
            try:
                instancia.delete()
            except ProtectedError:
                messages.error(request, 'O registro possui transações e não pode ser excluído.')

        return redirect('configuracoes')

    contexto = {
        'qtd_transacoes': Transacao.objects.count(),
        'qtd_categorias': Categoria.objects.count(),
        'qtd_contas': Conta.objects.count(),
        'tipos_c': Categoria.TIPO_CHOICES,
        'categorias': Categoria.objects.all(),
        'contas': Conta.objects.all(),
        'transacoes': Transacao.objects.select_related('categoria', 'conta'),
    }
    return render(request, 'core/configuracoes.html', contexto)