from datetime import date

import pandas as pd
import plotly.express as px
from django.db.models.functions import ExtractYear
from plotly.offline import plot

from core.models import Transacao
from .analysis import total_por_tipo


MESES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
    (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
    (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
    (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]
NOMES_MESES = dict(MESES)
COLUNAS = [
    'descricao', 'valor', 'data',
    'categoria__nome', 'categoria__tipo', 'conta__nome',
]


def selecionar_periodo(mes, ano):
    hoje = date.today()
    try:
        mes = int(mes)
        if not 1 <= mes <= 12:
            raise ValueError
    except (TypeError, ValueError):
        mes = hoje.month

    try:
        ano = int(ano)
    except (TypeError, ValueError):
        ano = hoje.year

    return mes, ano


def carregar_transacoes():
    registros = Transacao.objects.values(*COLUNAS)
    dados = pd.DataFrame.from_records(registros, columns=COLUNAS)
    dados = dados.rename(columns={
        'categoria__nome': 'categoria',
        'categoria__tipo': 'tipo',
        'conta__nome': 'conta',
    })
    dados['data'] = pd.to_datetime(dados['data'])
    dados['ano'] = dados['data'].dt.year
    dados['mes_num'] = dados['data'].dt.month
    dados['mes_nome'] = dados['mes_num'].map(NOMES_MESES)
    return dados


def maior_mes(resumo_mensal, tipo):
    linhas = resumo_mensal[resumo_mensal['tipo'] == tipo]
    if linhas.empty:
        return None, 0
    linha = linhas.loc[linhas['valor'].idxmax()]
    return f"{linha['mes_nome']} de {int(linha['ano'])}", linha['valor']


def gerar_graficos(dados, resumo_mensal):
    gastos = dados[dados['tipo'] == 'despesa'].groupby('categoria')['valor'].sum().reset_index()
    ganhos = dados[dados['tipo'] == 'receita'].groupby('categoria')['valor'].sum().reset_index()

    graficos = (
        px.bar(resumo_mensal, x='mes_nome', y='valor', color='tipo',
               title='Receitas X Despesas por mês'),
        px.pie(gastos, values='valor', names='categoria',
               title='Despesas por Categoria', hole=0.3),
        px.pie(ganhos, values='valor', names='categoria',
               title='Receita por categoria', hole=0.3),
    )
    return [plot(grafico, output_type='div', include_plotlyjs='cdn') for grafico in graficos]


def gerar_contexto_relatorio(mes, ano):
    mes, ano = selecionar_periodo(mes, ano)
    dados = carregar_transacoes()
    resumo_mensal = (
        dados.groupby(['ano', 'mes_num', 'mes_nome', 'tipo'])['valor']
        .sum()
        .reset_index()
    )

    receita_mes = total_por_tipo('receita', mes, ano)
    despesa_mes = total_por_tipo('despesa', mes, ano)
    mes_maior_receita, valor_maior_receita = maior_mes(resumo_mensal, 'receita')
    mes_maior_despesa, valor_maior_despesa = maior_mes(resumo_mensal, 'despesa')
    g_1, g_2, g_3 = gerar_graficos(dados, resumo_mensal)

    anos_disponiveis = (
        Transacao.objects.annotate(ano=ExtractYear('data'))
        .values_list('ano', flat=True).distinct().order_by('-ano')
    )

    return {
        'meses': MESES,
        'mes_selecionado': mes,
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano,
        'receita_mes': receita_mes,
        'despesa_mes': despesa_mes,
        'saldo_mes': receita_mes - despesa_mes,
        'mes_maior_receita': mes_maior_receita,
        'valor_maior_receita': valor_maior_receita,
        'mes_maior_despesa': mes_maior_despesa,
        'valor_maior_despesa': valor_maior_despesa,
        'transacoes': Transacao.objects.all(),
        'g_1': g_1,
        'g_2': g_2,
        'g_3': g_3,
    }