from datetime import date

from django.test import TestCase
from django.urls import reverse

from core.models import Categoria, Conta, Transacao

from .reports import selecionar_periodo


class RelatorioTests(TestCase):
    def test_periodo_invalido_usa_mes_e_ano_atuais(self):
        self.assertEqual(selecionar_periodo('abc', 'x'), (date.today().month, date.today().year))
        self.assertEqual(selecionar_periodo('13', '2025')[0], date.today().month)

    def test_relatorio_vazio_e_com_dados(self):
        url = reverse('analytics:dados')
        self.assertEqual(self.client.get(url).status_code, 200)

        categoria = Categoria.objects.create(nome='Salário', tipo='receita')
        conta = Conta.objects.create(nome='Banco')
        Transacao.objects.create(
            descricao='Pagamento', valor=100, data=date.today(),
            categoria=categoria, conta=conta,
        )

        resposta = self.client.get(url, {
            'mes': date.today().month,
            'ano': date.today().year,
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['receita_mes'], 100)
        self.assertEqual(resposta.context['saldo_mes'], 100)