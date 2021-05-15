import tempfile
from collections import OrderedDict


class JSGco:

    def __init__(self, gestor_ts):
        self.gestor_ts = gestor_ts
        self.es_codigo_main = True
        self.funciones_file = tempfile.TemporaryFile(encoding='UTF-8')
        self.main_file = tempfile.TemporaryFile(encoding='UTF-8')
        self.cadena_count = 0
        self.gestor_cadena = OrderedDict()
        self.bucle_count = 0
        self.gestor_bucle = OrderedDict()
        self._cast_cuarteto = {
            '+': self.operacion,
            '-': self.operacion,
            'and': self.operacion,
            'or': self.operacion,
            ':=': self.asignacion,
            ':=cad': self.asinacion_cadena,
            'goto==': self.salto,
            'goto!=': self.salto,
            'param': self.pasar_parametro,
            'param(cad)': self.pasar_parametro_cadena,
            'call': self.llamar_funcion,
            'return': self.devolver_valor,
            'return(cad)': self.devolver_valor_cadena,
            'alert(entero)': self.alert_entero,
            'alert(cadena)': self.alert_cadena,
            'input(entero)': self.input_entero,
            'input(cadena)': self.input_cadena
        }

    def finalizar(self):
        gco_file = open('codigo.ens', 'w', encoding='UTF-8')
        # inicializar etiquetas del programa
        gco_file.writelines(self.funciones_file.readlines())
        gco_file.writelines(self.main_file.readlines())

        self.funciones_file.close()
        self.main_file.close()
        gco_file.close()

    def etiqueta_cadena(self, cadena):
        if cadena not in self.gestor_cadena:
            self.cadena_count += 1
            self.gestor_cadena[cadena] = f"cadena{self.cadena_count}"
        return self.gestor_cadena[cadena]

    def etiqueta_bucle(self):
        self.bucle_count += 1
        return self.bucle_count

    def generar_codigo_objeto(self, operador, operando_a=None, operando_b=None, resultado=None):
        cuarteto = self._cast_cuarteto[operador]
        if self.es_codigo_main:
            self.main_file.write(cuarteto(operador, operando_a=operando_a, operando_b=operando_b, resultado=resultado))
        else:
            self.funciones_file.write(
                cuarteto(operador, operando_a=operando_a, operando_b=operando_b, resultado=resultado))

    def operacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def asignacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def asinacion_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def salto(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def pasar_parametro(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def pasar_parametro_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def llamar_funcion(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def devolver_valor(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def devolver_valor_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def alert_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def alert_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def input_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass

    def input_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        pass
