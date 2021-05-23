from error import GestorError
from table import GestorTablaSimbolo
from lexico import JSLexer, Token
from semantic import JSSemantic
from collections import deque
from gco import JSGco
from gci import JSGci
import pandas as pd
import sys

from util import resource_path


class JSParser:

    def __init__(self):
        self.tabla = pd.read_csv(resource_path('config/descendente_tabular.csv'), index_col=0, dtype=str)
        self.producciones = ['vacia']
        self.token_file = None
        self.lexico = None
        with open(resource_path('config/producciones.txt'), 'r') as f:
            for line in f:
                self.producciones.append(line.strip())

        self.terminales = {'alert', 'boolean', 'for', 'function', 'if', 'input', 'let', 'number', 'return', 'string',
                           'true', 'false', 'ID', 'ENTERO', 'CADENA', '=', '+', '-', '++', '==', '!=', '&&',
                           '||', '(', ')', '{', '}', ',', ';'}
        self.no_terminales = {'P', 'B', 'S', 'C', 'E', 'Y', 'X', 'F', 'A', 'K', 'L', 'Q', 'H', 'T',
                              'R', 'I', 'U', 'O', 'V', 'J', 'W', 'D', 'G', 'M', 'N'}
        self.cast_tk = {'IDENTIFICADOR': 'ID', 'ENTERO': 'ENTERO', 'CADENA': 'CADENA', 'ASIGNACION': '=',
                        'ARITSUMA': '+', 'ARITRESTA': '-', 'ARITINCRE': '++', 'RELIGUAL': '==',
                        'RELDISTINTO': '!=', 'LOGAND': '&&',
                        'LOGOR': '||', 'LLAVEIZQ': '{', 'LLAVEDER': '}', 'PARENTESISIZQ': '(',
                        'PARENTESISDER': ')', 'PUNTOCOMA': ';', 'COMA': ',', 'ALERT': 'alert',
                        'BOOLEAN': 'boolean', 'FOR': 'for', 'FUNCTION': 'function',
                        'IF': 'if', 'INPUT': 'input', 'LET': 'let', 'NUMBER': 'number', 'RETURN': 'return',
                        'STRING': 'string', 'TRUE': 'true', 'FALSE': 'false'}

    def sig_tok(self, tks):
        try:
            token = next(tks)
        except StopIteration:
            return Token('$', '', self.lexico.linea)
        self.token_file.write(f'<{token.tipo},{token.atributo}>\n')
        token.tipo = self.cast_tk[token.tipo]
        return token

    def parse(self, path):
        # inicializar todos los componentes
        gestor_ts = GestorTablaSimbolo()
        gestor_err = GestorError()
        gco = JSGco(gestor_ts)
        gci = JSGci(gco)
        self.lexico = JSLexer(gci, gestor_ts, gestor_err)
        tks = self.lexico.tokenize(path)
        self.token_file = open('tokens.txt', 'w')
        lista_reglas = ['Descendente']
        # algoritmo del analizador sintactico
        pila = deque([Simbolo('$'), Simbolo('P')])
        semantico = JSSemantic(self.lexico, gci, gco, gestor_ts, gestor_err, pila)
        token = self.sig_tok(tks)
        x = pila[-1]
        while True:
            # print('pila:', end=' ')
            # for el in pila:
            #     print(el.valor, end=',')
            # print()
            #
            # print('pila_aux:', end=' ')
            # for el in semantico.pila_aux:
            #     print(el.valor, end=',')
            # print()
            # print(x.valor)

            # terminal
            if x.valor in self.terminales:
                # print('ejecuta terminal')
                if x.valor == token.tipo:
                    simbolo = pila.pop()
                    simbolo.linea = token.linea
                    if token.tipo == 'ID':
                        simbolo.pos = token.atributo
                    elif token.tipo in ('ENTERO', 'CADENA'):
                        simbolo.constante = token.atributo
                    semantico.pila_aux.append(simbolo)
                    linea = token.linea
                    token = self.sig_tok(tks)
                else:
                    if x.valor == 'ENTERO':
                        cadena = f"un constante"
                    elif x.valor == 'CADENA':
                        cadena = f"una cadena"
                    elif x.valor == 'ID':
                        cadena = f"una variable"
                    else:
                        cadena = f"'{x.valor}'"
                    gestor_err.imprime('Sintáctico', f"Se espera {cadena}",
                                       token.linea if x.valor != ';' else linea)  # 150

            # no terminal
            elif x.valor in self.no_terminales:
                # print('ejecuta no terminal')
                # print(token.valor)
                regla = self.tabla.loc[x.valor, token.tipo]
                if not pd.isnull(regla):
                    lista_reglas.append(regla)
                    semantico.pila_aux.append(pila.pop())
                    for elemento in reversed((self.producciones[int(regla)].split('->'))[1].strip().split(' ')):
                        if elemento != 'lambda':
                            pila.append(Simbolo(elemento))
                else:
                    if token.tipo == 'ENTERO':
                        cadena = f"el constante {token.atributo}"
                    elif token.tipo == 'CADENA':
                        cadena = f"la cadena {token.atributo}"
                    elif token.tipo == 'ID':
                        cadena = f"la variable '{gestor_ts.buscar_simbolo_ts(token.atributo).lexema}'"
                    else:
                        cadena = f"'{token.tipo}'"
                    gestor_err.imprime('Sintáctico',
                                       f"No se espera {cadena}" if token.tipo != '$' else "Se espera ';'",
                                       token.linea)  # 151

            # accion semantica
            else:
                # print('ejecuta accion semantica')
                pila.pop()
                eval('semantico.' + x.valor + '()')
                # pila.pop()

            x = pila[-1]

            # actualiza la tabla y parse cada iteracion
            gestor_ts.imprime()
            with open('parse.txt', 'w') as f:
                f.write(' '.join(lista_reglas))

            if x.valor == '$':
                break

        if token.tipo == x.valor:
            print('Correcto')

        # cerrar los recursos
        with open('parse.txt', 'w') as f:
            f.write(' '.join(lista_reglas))
        gestor_ts.imprime()
        self.token_file.close()
        # terminar de implementar el codigo objeto
        gco.finalizar()


class Simbolo:
    # __slots__ = ('valor', 'tipo', 'ret', 'ancho', 'pos', 'lexema')

    def __init__(self, valor):
        self.valor = valor


if __name__ == '__main__':
    parser = JSParser()
    parser.parse('../codigo.js')
    # try:
    #     parser = JSParser()
    #     parser.parse('../codigo.js')
    # except Exception as e:
    #     print(e, file=sys.stderr)
    #     print('Error encontrado', file=sys.stderr)
