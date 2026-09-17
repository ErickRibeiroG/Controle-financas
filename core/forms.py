from decimal import Decimal

from django import forms

from .models import Categoria, Conta, Transacao


class MoneyField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip().replace('R$', '').replace(' ', '')
            if ',' in value:
                value = value.replace('.', '').replace(',', '.')
        return super().to_python(value)


class TransacaoForm(forms.Form):
    descricao_t = forms.CharField(max_length=100)
    valor = MoneyField(max_digits=10, decimal_places=2)
    data = forms.DateField()
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all())
    nome_conta = forms.ModelChoiceField(queryset=Conta.objects.all())
    observacoes = forms.CharField(required=False)

    def save(self):
        dados = self.cleaned_data
        return Transacao.objects.create(
            descricao=dados['descricao_t'],
            valor=dados['valor'],
            data=dados['data'],
            categoria=dados['categoria'],
            conta=dados['nome_conta'],
            observacao=dados['observacoes'],
        )


class CategoriaForm(forms.Form):
    nome_cat = forms.CharField(max_length=100)
    descricao_cat = forms.CharField(required=False)
    tipo = forms.ChoiceField(choices=Categoria.TIPO_CHOICES)

    def save(self):
        return Categoria.objects.create(
            nome=self.cleaned_data['nome_cat'],
            descricao=self.cleaned_data['descricao_cat'],
            tipo=self.cleaned_data['tipo'],
        )


class ContaForm(forms.Form):
    nome_conta = forms.CharField(max_length=20)
    saldo_inicial = MoneyField(max_digits=10, decimal_places=2, required=False)

    def save(self):
        return Conta.objects.create(
            nome=self.cleaned_data['nome_conta'],
            saldo_inicial=self.cleaned_data['saldo_inicial'] or Decimal('0.00'),
        )

class EdicaoTransacaoForm(forms.Form):
    nova_descricao = forms.CharField(max_length=100)
    nova_data = forms.DateField()
    novo_valor = MoneyField(max_digits=10, decimal_places=2)

    def save(self, transacao):
        transacao.descricao = self.cleaned_data['nova_descricao']
        transacao.data = self.cleaned_data['nova_data']
        transacao.valor = self.cleaned_data['novo_valor']
        transacao.save()
        return transacao


class EdicaoContaForm(forms.Form):
    novo_nome = forms.CharField(max_length=20)
    novo_saldo = MoneyField(max_digits=10, decimal_places=2)

    def save(self, conta):
        conta.nome = self.cleaned_data['novo_nome']
        conta.saldo_inicial = self.cleaned_data['novo_saldo']
        conta.save()
        return conta


class EdicaoCategoriaForm(forms.Form):
    novo_nome = forms.CharField(max_length=100)
    novo_tipo = forms.ChoiceField(choices=Categoria.TIPO_CHOICES)

    def save(self, categoria):
        categoria.nome = self.cleaned_data['novo_nome']
        categoria.tipo = self.cleaned_data['novo_tipo']
        categoria.save()
        return categoria