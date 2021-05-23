import tempfile
from collections import OrderedDict


class JSGco:

    def __init__(self, gestor_ts):
        self.gestor_ts = gestor_ts
        self.funciones_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
        self.main_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
        self.actual_file = self.main_file
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
            ':=cad': self.asignacion_cadena,
            'goto': self.salto,
            'goto==': self.salto_condicional,
            'goto!=': self.salto_condicional,
            'param': self.pasar_parametro,
            'param(cad)': self.pasar_parametro_cadena,
            'call': self.llamar_funcion,
            'call(cad)': self.llamar_funcion_cadena,
            'return': self.devolver_valor,
            'return(cad)': self.devolver_valor_cadena,
            ':': self.etiqueta,
            'alert(entero)': self.alert_entero,
            'alert(cadena)': self.alert_cadena,
            'input(entero)': self.input_entero,
            'input(cadena)': self.input_cadena
        }
        self._cast_operacion = {'+': 'ADD', '-': 'SUB', 'and': 'AND', 'or': 'OR'}

    def finalizar(self):
        gco_file = open('codigo.ens', 'w', encoding='UTF-8')
        # inicializar etiquetas del programa
        self.funciones_file.seek(0)
        self.main_file.seek(0)
        # cabezera del codigo ensamblador
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ORG 0".ljust(20, " ")))
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE #inicio_de".ljust(20, " ")))
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE #inicio_pila".ljust(20, " ")))
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE #BR /fun_global".ljust(20, " ")))

        gco_file.write("\n;------------Codigos de las funciones------------\n")
        gco_file.writelines(self.funciones_file.readlines())

        gco_file.write("\n;------------Codigos del programa principal------------\n")
        gco_file.write(u"{etiq}{st}\n\n".format(etiq="fun_global:".ljust(20, " "), st=f"NOP".ljust(20, " ")))
        gco_file.writelines(self.main_file.readlines())
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"HALT".ljust(20, " ")))

        gco_file.write("\n;------------Datos globales-----------\n")
        gco_file.write(u"{etiq}{st}\n".format(etiq="inicio_de:".ljust(20, " "),
                                               st=f"RES {self.gestor_ts.tamanio_ra_global()}".ljust(20, " ")))

        gco_file.write("\n;------------Tamanio RA de las funciones----------\n")
        # gco_file.write(u"{etiq}{st}\n".format(etiq="tam_ra_global:".ljust(20, " "),
        #                                        st=f"EQU {self.gestor_ts.tamanio_ra_global()}".ljust(20, " ")))
        for tabla in self.gestor_ts.lista_ts:
            gco_file.write(u"{etiq}{st}\n".format(etiq=f"tam_ra_{tabla.nombre}".ljust(20, " "),
                                                   st=f"EQU {self.gestor_ts.tamanio_ra(tabla)}".ljust(20, " ")))

        gco_file.write("\n;------------Cadenas usadas del programa-----------\n")
        for cadena, etiq in self.gestor_cadena.items():
            gco_file.write(
                u"{etiq}{st}\n".format(etiq=f"{etiq}:".ljust(20, " "), st=f'DATA "{cadena[1:-1]}"'.ljust(20, " ")))

        gco_file.write("\n;------------Inicio de la pila-----------\n")
        gco_file.write(u"{etiq}{st}\n".format(etiq="inicio_pila:".ljust(20, " "), st=f"NOP".ljust(20, " ")))
        gco_file.write(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"END".ljust(20, " ")))

        self.funciones_file.close()
        self.main_file.close()
        gco_file.close()

    @property
    def es_codigo_main(self):
        return self.actual_file is self.funciones_file

    @es_codigo_main.setter
    def es_codigo_main(self, valor):
        if valor:
            self.actual_file = self.main_file
        else:
            self.actual_file = self.funciones_file

    def etiqueta_cadena(self, cadena):
        if cadena not in self.gestor_cadena:
            self.cadena_count += 1
            self.gestor_cadena[cadena] = f"cadena{self.cadena_count}"
        return self.gestor_cadena[cadena]

    def etiqueta_bucle(self):
        self.bucle_count += 1
        return f"bucle{self.bucle_count}"

    def etiqueta_dir_ret(self):
        self.dir_ret_count += 1
        return f"dir_ret{self.dir_ret_count}"

    def generar_codigo_objeto(self, operador, operando_a=None, operando_b=None, resultado=None):
        cuarteto = self._cast_cuarteto[operador]
        self.actual_file.writelines(
            cuarteto(operador, operando_a=operando_a, operando_b=operando_b, resultado=resultado))
        self.actual_file.write('\n')

    def expresion_operando(self, operando):
        lugar = operando.cod_operando
        if lugar == 1:  # variable global
            return f"#{operando.lugar}[.IY]"
        if lugar in (2, 4, 6):  # variable local, parametro por valor, variable temporal
            return f"#{operando.lugar}[.IX]"
        if lugar == 7:  # constante entera
            return f"#{operando.lugar}"
        if lugar == 9:  # constante cadena
            return f"#{self.etiqueta_cadena(operando.lugar)}"
        if lugar == 11:  # etiqueta
            return f"#{operando.lugar}"

    def operacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        b = self.expresion_operando(operando_b)
        destino = self.expresion_operando(resultado)
        return (
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                    st=f"{self._cast_operacion[operador]} {a}, {b}".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, {destino}".ljust(20, " ")))

    def asignacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        destino = self.expresion_operando(resultado)
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE {a}, {destino}".ljust(20, " "))

    def asignacion_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_cadena = self.expresion_operando(operando_a)
        etiq_bucle = self.etiqueta_bucle()
        registro_destino = ".IX" if resultado.cod_operando != 1 else ".IY"
        inst = None

        if operando_a.cod_operando != 9:
            registro_origen = ".IX" if operando_a.cod_operando != 1 else ".IY"
            inst = [u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                            st=f"ADD #{operando_a.lugar}, {registro_origen}".ljust(20, " ")),
                    u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R9".ljust(20, " "))]
        else:
            inst = [u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE {etiq_cadena}, .R9".ljust(20, " "))]

        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                            st=f"ADD #{resultado.lugar}, {registro_destino}".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R8".ljust(20, " ")))
        # bucle copia cadena
        inst.append(
            u"{etiq}{st}\n".format(etiq=f"{etiq_bucle}:".ljust(20, " "), st=f"MOVE [.R9], [.R8]".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R9".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R8".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"CMP #0, [.R9]".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BNZ /{etiq_bucle}".ljust(20, " ")))
        return inst

    def salto(self, operador, operando_a=None, operando_b=None, resultado=None):
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BR /{resultado.lugar}".ljust(20, " ")),

    def salto_condicional(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        b = self.expresion_operando(operando_b)
        op = "BZ" if operador == "goto==" else "BP"

        return (u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"CMP {a}, {b}".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"{op} /{resultado.lugar}".ljust(20, " ")))

    def pasar_parametro(self, operador, operando_a=None, operando_b=None, resultado=None):
        origen = self.expresion_operando(operando_a)
        return (u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"ADD #tam_ra_{self.gestor_ts.actual.nombre}, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ADD #{operando_a.lugar}, .A".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE {origen}, [.A]".ljust(20, " ")))

    def pasar_parametro_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_cadena = self.expresion_operando(operando_a)
        etiq_bucle = self.etiqueta_bucle()
        registro = ".IX" if operando_a.cod_operando != 1 else ".IY"
        return (
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE {etiq_cadena}, .R9".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                    st=f"ADD #{operando_a.lugar}, {registro}".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R8".ljust(20, " ")),
            # bucle copia cadena
            u"{etiq}{st}\n".format(etiq=f"{etiq_bucle}:".ljust(20, " "), st=f"MOVE [.R9], [.R8]".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R9".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R8".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"CMP #0, [.R9]".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BNZ /{etiq_bucle}".ljust(20, " ")),

            u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                    st=f"ADD #tam_ra_{self.gestor_ts.actual.nombre}, .IX".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ADD #{operando_a.lugar}, .A".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .R8, [.A]".ljust(20, " "))
        )

    def llamar_funcion(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_funcion = self.expresion_operando(operando_a)
        etiq_ret = self.etiqueta_dir_ret()
        llamador = self.gestor_ts.actual.nombre
        inst = [u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"MOVE #{etiq_ret}, #tam_ra_{llamador}[.IX]".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"ADD #tam_ra_{llamador}, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"MOVE .A, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BR /{etiq_funcion}".ljust(20, " "))]
        if resultado is not None:
            destino = self.expresion_operando(resultado)
            inst.append(u"{etiq}{st}\n".format(etiq=f"{etiq_ret}:".ljust(20, " "),
                                                st=f"SUB #tam_ra_{llamador}, #1".ljust(20, " ")))

            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ADD .A, .IX".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE [.A], .R9".ljust(20, " ")))
            inst.append(
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"SUB .IX, #tam_ra_{llamador}".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .IX".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .R9, {destino}".ljust(20, " ")))

        else:
            inst.append(u"{etiq}{st}\n".format(etiq=f"{etiq_ret}:".ljust(20, " "),
                                                st=f"SUB .IX, #tam_ra_{llamador}".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .IX".ljust(20, " ")))

        return inst

    def llamar_funcion_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_funcion = self.expresion_operando(operando_a)
        etiq_ret = self.etiqueta_dir_ret()
        llamador = self.gestor_ts.actual.nombre
        etiq_bucle = self.etiqueta_bucle()
        registro = ".IX" if resultado.cod_operando != 1 else ".IY"

        return (u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"MOVE {etiq_ret}:, #tam_ra_{llamador}[.IX]".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"ADD #tam_ra_{llamador}, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"MOVE .A, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BR /{etiq_funcion}".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq=f"{etiq_ret}:".ljust(20, " "),
                                        st=f"SUB #tam_ra_{llamador}, #64".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ADD .A, .IX".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE [.A], .R9".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"SUB .IX, #tam_ra_{llamador}".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .IX".ljust(20, " ")),

                # bucle copia cadena
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                        st=f"ADD #{resultado.lugar}, {registro}".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R8".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq=f"{etiq_bucle}:".ljust(20, " "), st=f"MOVE [.R9], [.R8]".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R9".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R8".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"CMP #0, [.R9]".ljust(20, " ")),
                u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BNZ /{etiq_bucle}".ljust(20, " "))
                )

    def devolver_valor(self, operador, operando_a=None, operando_b=None, resultado=None):
        inst = []
        if operando_a is not None:
            a = self.expresion_operando(operando_a)
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                                st=f"SUB #tam_ra_{self.gestor_ts.actual.nombre}, #1".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ADD .A, IX".ljust(20, " ")))
            inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE {a}, [.A]".ljust(20, " ")))
        inst.append(u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BR [.IX]".ljust(20, " ")))
        return inst

    def devolver_valor_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_bucle = self.etiqueta_bucle()
        registro = ".IX" if operando_a.cod_operando != 1 else ".IY"

        return (
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                    st=f"ADD #{operando_a.lugar}, {registro}".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R9".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "),
                                    st=f"SUB #tam_ra_{self.gestor_ts.actual.nombre}, #64".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"MOVE .A, .R8".ljust(20, " ")),
            # bucle copia cadena
            u"{etiq}{st}\n".format(etiq=f"{etiq_bucle}:".ljust(20, " "), st=f"MOVE [.R9], [.R8]".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R9".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INC .R8".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"CMP #0, [.R9]".ljust(20, " ")),
            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BNZ /{etiq_bucle}".ljust(20, " ")),

            u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"BR [.IX]".ljust(20, " "))
        )

    def etiqueta(self, operador, operando_a=None, operando_b=None, resultado=None):
        return u"{etiq}{st}\n".format(etiq=f"{operando_a.lugar}:".ljust(20, " "), st=f"NOP".ljust(20, " "))

    def alert_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"WRINT {a}".ljust(20, " "))

    def alert_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"WRSTR {a}".ljust(20, " "))

    def input_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"ININT {a}".ljust(20, " "))

    def input_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        return u"{etiq}{st}\n".format(etiq="".ljust(20, " "), st=f"INSTR {a}".ljust(20, " "))
