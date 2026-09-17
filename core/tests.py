from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Conta, Transacao


class PaginaPrincipalTests(TestCase):
    def test_selects_exibem_categorias_e_contas(self):
        categoria = Categoria.objects.create(nome='Salário', tipo='receita')
        conta = Conta.objects.create(nome='Banco', saldo_inicial=0)

        resposta = self.client.get(reverse('home'))

        self.assertContains(resposta, categoria.nome)
        self.assertContains(resposta, conta.nome)

    def test_cadastro_de_conta_aceita_saldo_vazio_e_virgula(self):
        for nome, saldo in [('Sem saldo', ''), ('Com saldo', '1.234,56')]:
            with self.subTest(nome=nome):
                resposta = self.client.post(reverse('home'), {
                    'tipo_form': 'contas',
                    'nome_conta': nome,
                    'saldo_inicial': saldo,
                })
                self.assertRedirects(resposta, reverse('home'))

        self.assertEqual(Conta.objects.get(nome='Sem saldo').saldo_inicial, Decimal('0'))
        self.assertEqual(Conta.objects.get(nome='Com saldo').saldo_inicial, Decimal('1234.56'))

    def test_cadastro_invalido_mostra_erro_sem_gravar(self):
        resposta = self.client.post(reverse('home'), {
            'tipo_form': 'contas',
            'nome_conta': 'Banco',
            'saldo_inicial': 'valor inválido',
        })

        self.assertContains(resposta, 'Revise os dados informados')
        self.assertFalse(Conta.objects.exists())

    def test_cadastro_de_categoria_e_transacao(self):
        resposta = self.client.post(reverse('home'), {
            'tipo_form': 'categoria',
            'nome_cat': 'Salário',
            'descricao_cat': '',
            'tipo': 'receita',
        })
        self.assertRedirects(resposta, reverse('home'))
        conta = Conta.objects.create(nome='Banco')
        categoria = Categoria.objects.get(nome='Salário')

        resposta = self.client.post(reverse('home'), {
            'tipo_form': 'transacao',
            'descricao_t': 'Pagamento',
            'valor': '100,50',
            'data': date.today().isoformat(),
            'categoria': categoria.pk,
            'nome_conta': conta.pk,
            'observacoes': '',
        })
        self.assertRedirects(resposta, reverse('home'))
        self.assertEqual(Transacao.objects.get().valor, Decimal('100.50'))


class ConfiguracoesTests(TestCase):
    def test_conta_com_transacao_nao_e_excluida(self):
        categoria = Categoria.objects.create(nome='Salário', tipo='receita')
        conta = Conta.objects.create(nome='Banco')
        Transacao.objects.create(
            descricao='Pagamento', valor=10, data=date.today(),
            categoria=categoria, conta=conta,
        )

        resposta = self.client.post(reverse('configuracoes'), {
            'tipo_form': 'excluir_conta',
            'conta_id': conta.pk,
        }, follow=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(Conta.objects.filter(pk=conta.pk).exists())
        self.assertContains(resposta, 'não pode ser excluído')

class EdicaoContaTests(TestCase):
    def test_edicao_valida_e_invalida(self):
        conta = Conta.objects.create(nome='Banco', saldo_inicial=10)

        resposta = self.client.post(reverse('configuracoes'), {
            'tipo_form': 'editar_conta',
            'conta_id': conta.pk,
            'novo_nome': 'Banco Novo',
            'novo_saldo': '250,75',
        })
        self.assertRedirects(resposta, reverse('configuracoes'))
        conta.refresh_from_db()
        self.assertEqual(conta.nome, 'Banco Novo')
        self.assertEqual(conta.saldo_inicial, Decimal('250.75'))

        resposta = self.client.post(reverse('configuracoes'), {
            'tipo_form': 'editar_conta',
            'conta_id': conta.pk,
            'novo_nome': 'Inválido',
            'novo_saldo': 'não é número',
        }, follow=True)
        self.assertContains(resposta, 'Revise os dados informados')
        conta.refresh_from_db()
        self.assertEqual(conta.nome, 'Banco Novo')