from datetime import date

from django.db.models import Sum

from core.models import Transacao


def total_por_tipo(tipo, mes=None, ano=None):
    transacoes = Transacao.objects.filter(categoria__tipo=tipo)
    if mes is not None and ano is not None:
        transacoes = transacoes.filter(data__month=mes, data__year=ano)
    return transacoes.aggregate(total=Sum('valor'))['total'] or 0


def resumo_financeiro():
    hoje = date.today()
    receita_mes = total_por_tipo('receita', hoje.month, hoje.year)
    despesa_mes = total_por_tipo('despesa', hoje.month, hoje.year)
    saldo_total = total_por_tipo('receita') - total_por_tipo('despesa')

    return {
        'receita_mes': receita_mes,
        'despesa_mes': despesa_mes,
        'saldo_total': saldo_total,
    }