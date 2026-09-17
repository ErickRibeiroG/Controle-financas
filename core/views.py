from django.shortcuts import render, redirect, get_object_or_404
from core.models import Transacao, Categoria, Conta
import sqlite3
from datetime import date
from django.db.models import Sum
from django.db.models.functions import ExtractYear

""" from analytics.analysis import resumo_financeiro """
from analytics import analysis


import pandas as pd #analise
import plotly.express as px #exibição
from plotly.offline import plot
from django.http import HttpResponse

# Create your views here.
def financas(request):

    resumo_financas = analysis.resumo_financeiro()

    if request.method == 'POST':

        #pega o valor do input hidden, pra especificar nas consições
        tipo_form = request.POST.get('tipo_form')

        #Adicionar TransaçÃo
        if tipo_form == 'transacao':

            descricao = request.POST.get('descricao_t')
            valor = request.POST.get('valor')
            data = request.POST.get('data')
            categoria_id = request.POST.get('categoria')
            conta_id = request.POST.get('nome_conta')
            obs = request.POST.get('observacoes')

            Transacao.objects.create(
                descricao = descricao,
                valor = valor,
                data = data,
                categoria_id = categoria_id,
                conta_id = conta_id,
                observacao = obs,
            )

            return redirect('home')
        

        #Adicionar Categoria
        elif tipo_form == 'categoria':

            nome = request.POST.get('nome_cat')
            descricao = request.POST.get('descricao_cat')
            tipo = request.POST.get('tipo')

            Categoria.objects.create(
                nome = nome,
                descricao = descricao,
                tipo = tipo,
            )

            return redirect('home')


        #Adicionar Conta
        elif tipo_form == 'contas':

            nome = request.POST.get('nome_conta')
            saldo_inicial = (request.POST.get('saldo_inicial') or '').strip().replace(',', '.') or '0'

            Conta.objects.create(
                nome = nome,
                saldo_inicial = saldo_inicial
            )

            return redirect('home')

    context = {
        **resumo_financas,
        'categorias': Categoria.objects.all(),
        'contas': Conta.objects.all(),
    }

    return render(request, 'core/home.html', context)


""" ========================TRANSACOES================================ """
def transacoes(request):

    categorias = Categoria.objects.all()
    contas = Conta.objects.all()
    transacoes = Transacao.objects.all()

    context = {
        'categorias': categorias,
        'contas': contas,
        'transacoes': transacoes
    }

    return render(request, 'core/transacoes.html', context)


 #======================== CONFIGURAÇÕES ================================
def configuracoes(request):

    tipo_form = request.POST.get('tipo_form')

    if request.method == 'POST':

        #Transações ----------------------
        if tipo_form == 'editar_transacao':

            transacao_id = request.POST.get('tran_id')

            nova_desc = request.POST.get('nova_descricao')
            nova_data = request.POST.get('nova_data')
            novo_valor = request.POST.get('novo_valor')

            transacao = get_object_or_404(Transacao, id = transacao_id)

            transacao.descricao = nova_desc
            transacao.data = nova_data
            transacao.valor = novo_valor
            transacao.save()

        elif tipo_form == 'excluir_transacao':

            transacao_id = request.POST.get('tran_id')

            Transacao.objects.filter(id = transacao_id).delete()


        #Contas ----------------------
        elif tipo_form == 'editar_conta':

            conta_id = request.POST.get('conta_id')

            novo_nome = request.POST.get('novo_nome')
            novo_saldoI = request.POST.get('novo_saldo')

            conta = get_object_or_404(Conta, id = conta_id)

            conta.nome = novo_nome
            conta.saldo_inicial = novo_saldoI
            conta.save()

        #Excluir conta


        #Categorias ----------------------
        elif tipo_form == 'editar_categoria':

            categoria_id = request.POST.get('categoria_id')

            novo_nome = request.POST.get('novo_nome')
            novo_tipo = request.POST.get('novo_tipo')

            categoria = get_object_or_404(Categoria, id = categoria_id)
            categoria.nome = novo_nome
            categoria.tipo = novo_tipo
            categoria.save()
            
        elif tipo_form == 'excluir_categoria':

            categoria_id = request.POST.get('categoria_id')

            Categoria.objects.filter(id = categoria_id).delete()

    """ filtro_exibicao = request.GET.get('') """

    #Pega a qunatidade de cada um
    qtd_transacoes = Transacao.objects.count()
    qtd_categorias = Categoria.objects.count()
    qtd_contas = Conta.objects.count()

    categorias = Categoria.objects.all()
    contas = Conta.objects.all()
    transacoes = Transacao.objects.all()


    context = {
        'qtd_transacoes': qtd_transacoes,
        'qtd_categorias': qtd_categorias,
        'qtd_contas': qtd_contas,
        'tipos_c': Categoria.TIPO_CHOICES,
        'categorias': categorias,
        'contas': contas,
        'transacoes': transacoes
    }

    return render(request, 'core/configuracoes.html', context)

