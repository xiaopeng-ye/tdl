import tempfile
from collections import OrderedDict


def instruccion(operando, contenido, etiq="", comen=""):
    return u"{etiq}{st}{c}\n".format(etiq=etiq.ljust(20, " "), st=f"{operando} {contenido}".ljust(25, " "), c=comen)


def comentario(texto, formato=15):
    return u"{espacio}{st}\n".format(espacio="".ljust(formato, " "), st=texto)


class JSGco:

    def __init__(self, gestor_ts):
        self.gestor_ts = gestor_ts
        self.global_no_init = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
        self.funciones_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
        self.main_file = tempfile.TemporaryFile(mode='w+t', encoding='UTF-8')
        self.actual_file = self.main_file
        self.cadena_count = 0
        self.gestor_cadena = OrderedDict()
        self.bucle_count = 0
        self.fin_bucle_count = 0
        self.dir_ret_count = 0
        self.gestor_dir_ret = OrderedDict()
        self.dir_ret_count = 0
        self._cast_cuarteto = {
            '+': self.operacion,
            '-': self.operacion,
            'and': self.operacion,
            'or': self.operacion,
            ':=': self.asignacion,
            ':=cad': self.asignacion_cadena,
            'goto': self.salto,
            'if==': self.salto_condicional,
            'if!=': self.salto_condicional,
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
        self.global_no_init.seek(0)

        # cabezera del codigo ensamblador
        gco_file.write(instruccion("ORG", "0"))
        gco_file.write(instruccion("MOVE", "#inicio_pila, .IY"))
        gco_file.write(instruccion("MOVE", "#inicio_pila, .IX"))
        gco_file.write(instruccion("BR", "/fun_global"))

        gco_file.write("\n;------------Códigos de las funciones------------\n")
        gco_file.writelines(self.funciones_file.readlines())

        gco_file.write("\n;------------Códigos del programa principal------------\n")
        gco_file.write(instruccion("NOP", "", etiq="fun_global:"))
        gco_file.write(comentario("; Init de las globales no declaradas"))

        gco_file.writelines(self.global_no_init.readlines())
        gco_file.write(comentario("; Fin init de las globales no declaradas\n"))
        gco_file.writelines(self.main_file.readlines())
        gco_file.write(instruccion("HALT", ""))

        gco_file.write("\n;------------Tamaño RA de las funciones----------\n")
        for tabla in self.gestor_ts.lista_ts:
            gco_file.write(u"{etiq}{st}\n".format(etiq=f"tam_ra_{tabla.nombre}:".ljust(20, " "),
                                                  st=f"EQU {self.gestor_ts.tamanio_ra(tabla)}".ljust(20, " ")))

        gco_file.write("\n;------------Cadenas utilizadas del programa-----------\n")
        for cadena, etiq in self.gestor_cadena.items():
            gco_file.write(instruccion('DATA', f'"{cadena[1:-1]}"', etiq=f"{etiq}:"))

        # gco_file.write("\n;------------Datos globales-----------\n")
        # gco_file.write(u"{etiq}{st}\n".format(etiq="inicio_de:".ljust(20, " "),
        #                                       st=f"RES {self.gestor_ts.tamanio_ra_global()}".ljust(20, " ")))

        gco_file.write("\n;------------Inicio de la pila-----------\n")
        gco_file.write(instruccion("NOP", "", etiq="inicio_pila:"))
        gco_file.write(instruccion("END", ""))

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

    def etiqueta_fin_bucle(self):
        self.fin_bucle_count += 1
        return f"fin_bucle{self.fin_bucle_count}"

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
            return f"{operando.lugar}"

    def registro_variable(self, operando):
        if operando.cod_operando == 1:
            return ".IY"
        if operando.cod_operando in (2, 4, 6):
            return ".IX"

    def operacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        reg_a = self.registro_variable(operando_a)
        reg_b = self.registro_variable(operando_b)
        reg_destino = self.registro_variable(resultado)
        if operando_b.cod_operando == 7:
            return (comentario(f"; Operación {operador}", formato=20),
                    instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
                    instruccion("MOVE", ".A, .R7"),
                    instruccion("ADD", f"#{operando_a.lugar}, {reg_a}"),
                    instruccion(f"{self._cast_operacion[operador]}", f"#{operando_b.lugar}, [.A]"),
                    instruccion("MOVE", ".A, [.R7]"))
        else:
            return (comentario(f"; Operación {operador}", formato=20),
                    instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
                    instruccion("MOVE", ".A, .R7"),
                    instruccion("ADD", f"#{operando_b.lugar}, {reg_b}"),
                    instruccion("MOVE", ".A, .R8"),
                    instruccion("ADD", f"#{operando_a.lugar}, {reg_a}"),
                    instruccion(f"{self._cast_operacion[operador]}", "[.A], [.R8]"),
                    instruccion("MOVE", ".A, [.R7]"))

    def asignacion(self, operador, operando_a=None, operando_b=None, resultado=None):
        reg_a = self.registro_variable(operando_a)
        reg_destino = self.registro_variable(resultado)
        if operando_a.cod_operando == 7:
            return (instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
                    instruccion("MOVE", f"#{operando_a.lugar}, [.A]"))
        else:
            return (instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
                    instruccion("MOVE", f".A, .R9"),
                    instruccion("ADD", f"#{operando_a.lugar}, {reg_a}"),
                    instruccion("MOVE", "[.A], [.R9]"))

    def asignacion_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_cadena = self.expresion_operando(operando_a)
        etiq_bucle = self.etiqueta_bucle()
        etiq_fin_bucle = self.etiqueta_fin_bucle()
        registro_destino = ".IX" if resultado.cod_operando != 1 else ".IY"
        inst = [comentario("; Asignación de cadena", formato=20)]
        if operando_a.cod_operando != 9:
            registro_origen = ".IX" if operando_a.cod_operando != 1 else ".IY"
            inst.append(instruccion("ADD", f"#{operando_a.lugar}, {registro_origen}"))
            inst.append(instruccion("MOVE", ".A, .R9", etiq="", comen="; Copia la dir de cadena en R9"))
        else:
            inst.append(instruccion("MOVE", f"{etiq_cadena}, .R9", comen="; Copia la dir de cadena en R9"))

        inst.append(instruccion("ADD", f"#{resultado.lugar}, {registro_destino}"))
        inst.append(instruccion("MOVE", ".A, .R8"))
        # bucle copia cadena
        inst.append(instruccion("CMP", "#0, [.R9]", etiq=f"{etiq_bucle}:"))
        inst.append(instruccion(f"BZ", f"/{etiq_fin_bucle}"))
        inst.append(instruccion("MOVE", "[.R9], [.R8]", comen="; Bucle de copia de cadena"))
        inst.append(instruccion("INC", ".R9"))
        inst.append(instruccion("INC", ".R8"))
        inst.append(instruccion("BR", f"/{etiq_bucle}"))
        inst.append(instruccion("MOVE", "#0, [.R8]", etiq=f"{etiq_fin_bucle}:"))
        return inst

    def salto(self, operador, operando_a=None, operando_b=None, resultado=None):
        return instruccion("BR", f"/{resultado.lugar}"),

    def salto_condicional(self, operador, operando_a=None, operando_b=None, resultado=None):
        a = self.expresion_operando(operando_a)
        b = self.expresion_operando(operando_b)
        op = "BZ" if operador == "if==" else "BNZ"

        return (comentario(f"; Salto condicional {operador}", formato=20),
                instruccion("CMP", f"{a}, {b}"),
                instruccion(f"{op}", f"/{resultado.lugar}"))

    def pasar_parametro(self, operador, operando_a=None, operando_b=None, resultado=None):
        reg_origen = self.registro_variable(operando_a)
        return (comentario("; Pasar parámetro", formato=20),
                instruccion("ADD", f"#tam_ra_{self.gestor_ts.actual.nombre}, .IX"),
                instruccion("ADD", f"#{operando_a.despl_param}, .A"),
                instruccion("MOVE", ".A, .R9"),
                instruccion("ADD", f"#{operando_a.lugar}, {reg_origen}"),
                instruccion("MOVE", f"[.A], [.R9]"))

    def pasar_parametro_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_bucle = self.etiqueta_bucle()
        etiq_fin_bucle = self.etiqueta_fin_bucle()
        reg_a = self.registro_variable(operando_a)
        return (
            comentario("; Pasar parámetro tipo cadena", formato=20),
            instruccion("ADD", f"#{operando_a.lugar}, {reg_a}"),
            instruccion("MOVE", ".A, .R9", comen=f"; Copia la dir de cadena en R9"),
            instruccion("ADD", f"#tam_ra_{self.gestor_ts.actual.nombre}, .IX"),
            instruccion("ADD", f"#{operando_a.despl_param}, .A"),
            instruccion("MOVE", ".A, .R8"),
            # bucle copia cadena
            instruccion("CMP", "#0, [.R9]", etiq=f"{etiq_bucle}:"),
            instruccion(f"BZ", f"/{etiq_fin_bucle}"),
            instruccion("MOVE", "[.R9], [.R8]", comen="; Bucle de copia de cadena"),
            instruccion("INC", ".R9"),
            instruccion("INC", ".R8"),
            instruccion("BR", f"/{etiq_bucle}"),
            instruccion("MOVE", "#0, [.R8]", etiq=f"{etiq_fin_bucle}:"))

    def llamar_funcion(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_funcion = self.expresion_operando(operando_a)
        etiq_ret = self.etiqueta_dir_ret()
        llamador = self.gestor_ts.actual.nombre
        inst = [comentario(f"; Invoca la función {operando_a.simbolo}"),
                instruccion("ADD", f"#tam_ra_{llamador}, .IX"),
                instruccion("MOVE", f"#{etiq_ret}, [.A]"),
                instruccion("MOVE", ".A, .IX"),
                instruccion("BR", f"/{etiq_funcion}")]
        if resultado is not None:
            reg_destino = self.registro_variable(resultado)
            inst.append(instruccion("SUB", f"#tam_ra_{etiq_funcion[4:]}, #1", etiq=f"{etiq_ret}:",
                                    comen=f"; Etiqueta de retorno"))
            inst.append(instruccion("ADD", ".A, .IX"))
            inst.append(instruccion("MOVE", "[.A], .R9", comen=f"; Valor devuelto en R9"))
            inst.append(instruccion("SUB", f".IX, #tam_ra_{llamador}"))
            inst.append(instruccion("MOVE", ".A, .IX"))
            inst.append(instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"))
            inst.append(
                instruccion("MOVE", ".R9, [.A]", comen=f"; Valor devuelto en el dato temporal correspondiente"))

        else:
            inst.append(
                instruccion("SUB", f".IX, #tam_ra_{llamador}", etiq=f"{etiq_ret}:", comen=f"; Etiqueta de retorno"))
            inst.append(instruccion("MOVE", ".A, .IX"))

        return inst

    def llamar_funcion_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_funcion = self.expresion_operando(operando_a)
        etiq_ret = self.etiqueta_dir_ret()
        llamador = self.gestor_ts.actual.nombre
        etiq_bucle = self.etiqueta_bucle()
        etiq_fin_bucle = self.etiqueta_fin_bucle()
        reg_destino = self.registro_variable(resultado)

        return (comentario(f"; Invoca la función {operando_a.simbolo[4:]}"),
                instruccion("ADD", f"#tam_ra_{llamador}, .IX"),
                instruccion("MOVE", f"#{etiq_ret}, [.A]"),
                instruccion("MOVE", ".A, .IX"),
                instruccion("BR", f"/{etiq_funcion}"),
                instruccion("SUB", f"#tam_ra_{etiq_funcion[4:]}, #64", etiq=f"{etiq_ret}:",
                            comen=f"; Etiqueta de retorno"),
                instruccion("ADD", ".A, .IX"),
                instruccion("MOVE", ".A, .R9", comen=f"; Dirección del valor devuelto en R9"),
                instruccion("SUB", f".IX, #tam_ra_{llamador}"),
                instruccion("MOVE", ".A, .IX"),
                instruccion("ADD", f"#{resultado.lugar}, {reg_destino}", comen=f"; Bucle de copia de cadena"),
                instruccion("MOVE", ".A, .R8"),
                # bucle copia cadena
                instruccion("CMP", "#0, [.R9]", etiq=f"{etiq_bucle}:"),
                instruccion(f"BZ", f"/{etiq_fin_bucle}"),
                instruccion("MOVE", "[.R9], [.R8]", comen="; Bucle de copia de cadena"),
                instruccion("INC", ".R9"),
                instruccion("INC", ".R8"),
                instruccion("BR", f"/{etiq_bucle}"),
                instruccion("MOVE", "#0, [.R8]", etiq=f"{etiq_fin_bucle}:"))

    def devolver_valor(self, operador, operando_a=None, operando_b=None, resultado=None):
        inst = []
        if resultado is not None:
            reg_destino = self.registro_variable(resultado)
            inst = [comentario(f"; Return tipo entero o lógico"),
                    instruccion("SUB", f"#tam_ra_{self.gestor_ts.actual.nombre}, #1"),
                    instruccion("ADD", ".A, .IX"),
                    instruccion("MOVE", ".A, .R9"),
                    instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
                    instruccion("MOVE", "[.A], [.R9]")]
        inst.append(instruccion("BR", "[.IX]"))
        return inst

    def devolver_valor_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        etiq_bucle = self.etiqueta_bucle()
        etiq_fin_bucle = self.etiqueta_fin_bucle()
        reg_destino = self.registro_variable(resultado)
        return (
            comentario(f"; Return tipo cadena"),
            instruccion("ADD", f"#{resultado.lugar}, {reg_destino}"),
            instruccion("MOVE", ".A, .R9"),
            instruccion("SUB", f"#tam_ra_{self.gestor_ts.actual.nombre}, #64"),
            instruccion("ADD", ".A, .IX"),
            instruccion("MOVE", ".A, .R8"),
            # bucle copia cadena
            instruccion("CMP", "#0, [.R9]", etiq=f"{etiq_bucle}:"),
            instruccion(f"BZ", f"/{etiq_fin_bucle}"),
            instruccion("MOVE", "[.R9], [.R8]", comen="; Bucle de copia de cadena"),
            instruccion("INC", ".R9"),
            instruccion("INC", ".R8"),
            instruccion("BR", f"/{etiq_bucle}"),
            instruccion("MOVE", "#0, [.R8]", etiq=f"{etiq_fin_bucle}:"),
            instruccion("BR", "[.IX]"))

    def etiqueta(self, operador, operando_a=None, operando_b=None, resultado=None):
        return instruccion("NOP", "", etiq=f"{operando_a.lugar}:")

    def alert_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        registro = self.registro_variable(operando_a)
        return (comentario("; Alert entero"),
                instruccion("ADD", f"#{operando_a.lugar}, {registro}"),
                instruccion("WRINT", "[.A]"))

    def alert_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        registro = self.registro_variable(operando_a)
        return (comentario("; Alert cadena"),
                instruccion("ADD", f"#{operando_a.lugar}, {registro}"),
                instruccion("WRSTR", "[.A]"))

    def input_entero(self, operador, operando_a=None, operando_b=None, resultado=None):
        registro = self.registro_variable(operando_a)
        return (comentario("; Input entero"),
                instruccion("ADD", f"#{operando_a.lugar}, {registro}"),
                instruccion("ININT", "[.A]"))

    def input_cadena(self, operador, operando_a=None, operando_b=None, resultado=None):
        registro = self.registro_variable(operando_a)
        return (comentario("; Input cadena"),
                instruccion("ADD", f"#{operando_a.lugar}, {registro}"),
                instruccion("INSTR", "[.A]"))
