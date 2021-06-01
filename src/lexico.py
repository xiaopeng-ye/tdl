import pandas as pd
from error import GestorError
from table import GestorTablaSimbolo
from util import resource_path
from gci import Operando


class JSLexer:

    def __init__(self, gci, gestor_ts, gestor_err):
        self.code_file = None
        self.linea = None
        self.gci = gci
        self.gestor_ts = gestor_ts
        self.gestor_err = gestor_err
        self.tabla = pd.read_csv(resource_path('config/lexico_tabla.csv'), index_col=0, dtype=str)
        self._cast_columns_name = {'_': 4, ' ': 6, '\n': 38, '\t': 6, "'": 8, '\\': 10, '+': 12, '-': 14, '/': 16,
                                   '=': 18, '!': 20, '&': 22, '|': 24, ';': 26, ',': 28, '(': 30, ')': 32, '{': 34,
                                   '}': 36}

    def next_char(self):
        char = self.code_file.read(1)
        if not char:
            self.code_file.close()
        elif char == '\n':
            self.linea += 1
        return char

    def cast_position(self, char):
        if char.isalpha():
            return 0
        elif char.isdigit():
            return 2
        elif char in self._cast_columns_name:
            return self._cast_columns_name[char]
        else:
            return 40

    def tokenize(self, path):
        self.code_file = open(path, 'r', encoding='UTF-8')
        self.linea = 1
        char = self.next_char()
        while char:
            estado = 0
            while estado < 12 and char:
                pos = self.cast_position(char)
                transicion = self.tabla.iloc[estado, pos]
                accion = self.tabla.iloc[estado, pos + 1]
                if pd.isnull(transicion):
                    self.gestor_err.imprime('Léxico', self.gestor_err.error_lexico[int(accion)] + (f" '{char}'" if int(
                        accion) == 101 else ''), self.linea)
                    char = None
                    break
                estado = int(transicion)

                if accion == 'A':
                    char = self.next_char()
                elif accion == 'B':
                    lexema = char
                    char = self.next_char()
                elif accion == 'C':
                    lexema += char
                    char = self.next_char()
                elif accion == 'D':
                    if lexema in {'alert', 'boolean', 'for', 'function', 'if', 'input', 'let', 'number', 'return',
                                  'string', 'true', 'false'}:
                        yield Token(lexema.upper(), '', self.linea)
                    else:
                        # if self.gestor_ts.busca_ts_activa(lexema) is None:
                        #     indice = self.gestor_ts.inserta_ts_activa(lexema)
                        # else:
                        #     indice = self.gestor_ts.busca_ts(lexema)

                        if self.gestor_ts.zona_decl:
                            if self.gestor_ts.busca_ts_activa(lexema) is None:
                                indice = self.gestor_ts.inserta_ts_activa(lexema)
                            else:
                                self.gestor_err.imprime('Semántico', 'Ya existe el identificador a declarar',
                                                        self.linea)
                        else:
                            indice = self.gestor_ts.busca_ts(lexema)
                            if indice is None:
                                indice = self.gestor_ts.inserta_ts_global(lexema)
                                self.gestor_ts.aniadir_var_atributos_ts_global(indice, 'entero', 1)
                                id_simbolo = self.gestor_ts.buscar_simbolo_ts(indice)
                                self.gci.emite_global_no_init(Operando(1, id_simbolo['despl'], id_simbolo.lexema))
                        yield Token('IDENTIFICADOR', indice, self.linea)

                elif accion == 'E':
                    valor = char
                    char = self.next_char()
                elif accion == 'F':
                    valor += char
                    char = self.next_char()
                elif accion == 'G':
                    valor = int(valor)
                    if 32767 >= valor >= 0:
                        yield Token('ENTERO', valor, self.linea)
                    else:
                        self.gestor_err.imprime('Léxico', self.gestor_err.error_lexico[108], self.linea)
                        char = None
                elif accion == 'H':
                    lexema = ''
                    contador = 0
                    char = self.next_char()
                elif accion == 'J':
                    lexema += char
                    contador += 1
                    char = self.next_char()
                elif accion == 'K':
                    if contador <= 64:
                        yield Token('CADENA', f"'{lexema}'", self.linea)
                        char = self.next_char()
                    else:
                        self.gestor_err.imprime('Léxico', self.gestor_err.error_lexico[109], self.linea)
                        char = None
                elif accion == 'L':
                    lexema += char
                    char = self.next_char()
                elif accion == 'M':
                    yield Token('ARITSUMA', '', self.linea)
                elif accion == 'N':
                    yield Token('ARITRESTA', '', self.linea)
                    char = self.next_char()
                elif accion == 'O':
                    yield Token('ARITINCRE', '', self.linea)
                    char = self.next_char()
                elif accion == 'P':
                    yield Token('RELIGUAL', '', self.linea)
                    char = self.next_char()
                elif accion == 'Q':
                    yield Token('RELDISTINTO', '', self.linea)
                    char = self.next_char()
                elif accion == 'R':
                    yield Token('ASIGNACION', '', self.linea)
                elif accion == 'S':
                    yield Token('LOGAND', '', self.linea)
                    char = self.next_char()
                elif accion == 'T':
                    yield Token('LOGOR', '', self.linea)
                    char = self.next_char()
                elif accion == 'U':
                    yield Token('PUNTOCOMA', '', self.linea)
                    char = self.next_char()
                elif accion == 'V':
                    yield Token('COMA', '', self.linea)
                    char = self.next_char()
                elif accion == 'W':
                    yield Token('PARENTESISIZQ', '', self.linea)
                    char = self.next_char()
                elif accion == 'X':
                    yield Token('PARENTESISDER', '', self.linea)
                    char = self.next_char()
                elif accion == 'Y':
                    yield Token('LLAVEIZQ', '', self.linea)
                    char = self.next_char()
                elif accion == 'Z':
                    yield Token('LLAVEDER', '', self.linea)
                    char = self.next_char()


class Token:

    def __init__(self, tipo, atributo, linea):
        self.tipo = tipo
        self.atributo = atributo
        self.linea = linea

    def __str__(self):
        return f'<{self.tipo},{self.atributo}>'


if __name__ == '__main__':
    ts = GestorTablaSimbolo()
    err = GestorError()
    lexer = JSLexer(ts, err)
    for token in lexer.tokenize('../codigo.js'):
        print(token, 'linea', token.linea)
    ts.imprime()
