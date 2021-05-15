class JSGci:
    def __init__(self):
        self.gci_file = open('gci.txt', 'w', encoding='UTF-8')

    def emite(self, operador, operando_a=None, operando_b=None, resultado=None):
        self.gci_file.write('({operador}, {operando_a}, {operando_b}, {resultado})\n'.format(
            operador=operador,
            operando_a='' if operando_a is None else operando_a.simbolo,
            operando_b='' if operando_b is None else operando_b.simbolo,
            resultado='' if resultado is None else resultado.simbolo))


class Operando:
    def __init__(self, cod_operando, lugar, simbolo):
        self.cod_operando = cod_operando
        self.lugar = lugar
        self.simbolo = simbolo
