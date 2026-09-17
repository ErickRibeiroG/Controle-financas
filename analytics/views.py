from django.shortcuts import render

from .reports import gerar_contexto_relatorio


def dados(request):
    contexto = gerar_contexto_relatorio(
        request.GET.get('mes'),
        request.GET.get('ano'),
    )
    return render(request, 'analytics/dados.html', contexto)