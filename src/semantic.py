from collections import deque


class JSSemantic:

    def __init__(self, lexico, gestor_ts, gestor_err):
        self.lexico = lexico
        self.gestor_ts = gestor_ts
        self.gestor_err = gestor_err
        self.pila_aux = deque()

    def regla_P1(self):  # P -> F P
        self.pila_aux.pop()
        self.pila_aux.pop()

    def regla_P2(self):  # P -> S P y P -> B P
        self.pila_aux.pop()
        sb = self.pila_aux.pop()
        if sb.ret != 'vacio':
            self.gestor_err.imprime('Semántico',
                                    "La sentencia 'return' solo es válida dentro de una función",
                                    self.lexico.linea)  # 200

    def regla_F1(self):  # F -> function
        self.gestor_ts.zona_decl = True

    def regla_F2(self):  # F -> function H ID
        id_ = self.pila_aux[-1]
        self.gestor_ts.crea_tabla(id_.pos)

    def regla_F3(self):  # F -> function H ID ( A )
        a = self.pila_aux[-2]
        id_ = self.pila_aux[-4]
        h = self.pila_aux[-5]
        self.gestor_ts.aniadir_func_atributos_ts(id_.pos, a.tipo, h.tipo)
        self.gestor_ts.zona_decl = False

    def regla_F4(self):  # F -> function H ID ( A ) { C
        c = self.pila_aux[-1]
        h = self.pila_aux[-7]
        function = self.pila_aux[-8]
        f = self.pila_aux[-9]

        if c.ret == h.tipo:
            f.tipo = 'ok'
        else:
            f.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de retorno de la función no coincide con el valor del 'return'",
                                    function.linea)  # 201
        self.gestor_ts.libera_tabla()

    def regla_F5(self):  # F -> function H ID ( A ) { C }
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()

    def regla_C1(self):  # C -> B C1 y C -> S C1
        c1 = self.pila_aux.pop()
        b = self.pila_aux.pop()
        c = self.pila_aux[-1]

        if b.tipo == 'ok' and (c1.tipo == 'ok' or c1.tipo == 'vacio'):
            c.tipo = 'ok'
        elif b.tipo == 'ok':
            c.tipo = c1.tipo
        elif c1.tipo == 'ok':
            c.tipo = b.tipo
        else:
            c.tipo = 'error'

        if b.ret == c1.ret:
            c.ret = b.ret
        elif b.ret == 'vacio':
            c.ret = c1.ret
        elif c1.ret == 'vacio':
            c.ret = b.ret
        else:
            c.ret = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de retorno de la función no coincide con el valor del 'return'",
                                    self.lexico.linea)  # 201

    def regla_C2(self):  # C -> lambda
        c = self.pila_aux[-1]
        c.tipo = 'vacio'
        c.ret = 'vacio'

    def regla_E1(self):  # E -> R Y
        y = self.pila_aux.pop()
        r = self.pila_aux.pop()
        e = self.pila_aux[-1]

        if (r.tipo == y.tipo == 'logico') or y.tipo == 'vacio':
            e.tipo = r.tipo
        else:
            e.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de los operandos del operador '||' no coincide", self.lexico.linea)  # 202

    def regla_Y(self):  # Y -> || R Y1
        y1 = self.pila_aux.pop()
        r = self.pila_aux.pop()
        operador = self.pila_aux.pop()
        y = self.pila_aux[-1]

        if r.tipo == 'logico' and (y1.tipo == 'logico' or y1.tipo == 'vacio'):
            y.tipo = 'logico'
        else:
            y.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "Se esperaba un tipo lógico de los operandos del operador '||'",
                                    operador.linea)  # 203

    def regla_R(self):  # R -> U I
        i = self.pila_aux.pop()
        u = self.pila_aux.pop()
        r = self.pila_aux[-1]

        if (u.tipo == i.tipo == 'logico') or i.tipo == 'vacio':
            r.tipo = u.tipo
        else:
            r.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de los operandos del operador '&&' no coincide", self.lexico.linea)  # 204

    def regla_I(self):  # I -> && U I1
        i1 = self.pila_aux.pop()
        u = self.pila_aux.pop()
        and_ = self.pila_aux.pop()
        i = self.pila_aux[-1]

        if u.tipo == 'logico' and (i1.tipo == 'logico' or i1.tipo == 'vacio'):
            i.tipo = u.tipo
        else:
            i.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "Se esperaba un tipo lógico de los operandos del operador '&&'", and_.linea)  # 205

    def regla_U(self):  # U -> V O
        o = self.pila_aux.pop()
        v = self.pila_aux.pop()
        u = self.pila_aux[-1]

        if v.tipo == o.tipo:
            u.tipo = 'logico'
        elif o.tipo == 'vacio':
            u.tipo = v.tipo
        else:
            u.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de los operandos del operador de relación no coincide",
                                    self.lexico.linea)  # 206

    def regla_O(self):  # O -> != V O y O -> == V O
        o1 = self.pila_aux.pop()
        v = self.pila_aux.pop()
        comparacion = self.pila_aux.pop()
        o = self.pila_aux[-1]

        if v.tipo == 'entero' and (o1.tipo == 'entero' or o1.tipo == 'vacio'):
            o.tipo = 'entero'
        else:
            o.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    'Se esperaba un tipo entero de los operandos del operador de relación',
                                    comparacion.linea)  # 207

    def regla_V(self):  # V -> W J
        j = self.pila_aux.pop()
        w = self.pila_aux.pop()
        v = self.pila_aux[-1]

        if (w.tipo == j.tipo == 'entero') or j.tipo == 'vacio':
            v.tipo = w.tipo
        else:
            v.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    "El tipo de los operandos del operador aritmético deben ser enteros",
                                    self.lexico.linea)  # 208

    def regla_J(self):  # J -> + W J1  y J -> - W J1
        j1 = self.pila_aux.pop()
        w = self.pila_aux.pop()
        operador = self.pila_aux.pop()
        j = self.pila_aux[-1]

        if w.tipo == 'entero' and (j1.tipo == 'entero' or j1.tipo == 'vacio'):
            j.tipo = 'entero'
        else:
            j.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    'Se esperaba un tipo entero de los operandos del operador aritmético',
                                    operador.linea)  # 209

    def regla_W1(self):  # W -> ++ ID
        id_ = self.pila_aux.pop()
        self.pila_aux.pop()
        w = self.pila_aux[-1]
        if self.gestor_ts.buscar_simbolo_ts(id_.pos)['tipo'] == 'entero':
            w.tipo = 'entero'
        else:
            w.tipo = 'error'
            self.gestor_err.imprime('Semántico',
                                    'Solo se puede auto incrementar variables de tipo entero', id_.linea)  # 210

    def regla_W2(self):  # W -> ( E )
        self.pila_aux.pop()
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        w = self.pila_aux[-1]
        w.tipo = e.tipo

    def regla_W3(self):  # W -> ID D
        d = self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        w = self.pila_aux[-1]

        id_simbolo = self.gestor_ts.buscar_simbolo_ts(id_.pos)
        if id_simbolo['tipo'] != 'funcion':
            if d.tipo == 'ok':
                w.tipo = id_simbolo['tipo']
            else:
                w.tipo = 'error'
                self.gestor_err.imprime('Semántico',
                                        f"El identificador '{id_simbolo.lexema}' corresponde a una variable",
                                        id_.linea)  # 213
        else:
            if id_simbolo['tipoParam'] == d.tipo:
                w.tipo = id_simbolo['tipoRetorno']
            elif d.tipo == 'ok':
                w.tipo = 'error'
                self.gestor_err.imprime('Semántico',
                                        f"El identificador '{id_simbolo.lexema}' corresponde a una función",
                                        id_.linea)  # 211
            else:
                w.tipo = 'error'
                self.gestor_err.imprime('Semántico', 'Los tipos de los parámetros no coinciden', id_.linea)  # 212

    def regla_W4(self):  # W-> entero
        self.pila_aux.pop()
        w = self.pila_aux[-1]
        w.tipo = 'entero'

    def regla_W5(self):  # W-> cadena
        self.pila_aux.pop()
        w = self.pila_aux[-1]
        w.tipo = 'cadena'

    def regla_W6(self):  # W -> true | W -> false
        self.pila_aux.pop()
        w = self.pila_aux[-1]
        w.tipo = 'logico'

    def regla_D(self):  # D -> (L) igual G2
        self.pila_aux.pop()
        ll = self.pila_aux.pop()
        self.pila_aux.pop()
        d = self.pila_aux[-1]
        d.tipo = ll.tipo

    def regla_D1(self):  # D -> lambda
        d = self.pila_aux[-1]
        d.tipo = 'ok'

    def regla_B1_1(self):  # B -> let
        self.gestor_ts.zona_decl = True

    def regla_B1_2(self):  # B -> let T ID ;
        self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        t = self.pila_aux.pop()
        self.pila_aux.pop()
        b = self.pila_aux[-1]
        self.gestor_ts.aniadir_var_atributos_ts_activa(id_.pos, t.tipo, t.ancho)
        b.tipo = 'ok'
        b.ret = 'vacio'

    def regla_B1_3(self):  # B -> let T ID
        self.gestor_ts.zona_decl = False

    def regla_B2(self):  # B -> if ( E ) S {
        s = self.pila_aux.pop()
        self.pila_aux.pop()
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        if_ = self.pila_aux.pop()
        b = self.pila_aux[-1]

        if e.tipo == 'logico':
            b.tipo = s.tipo
            b.ret = s.ret
        else:
            b.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'Se espera una expresión de tipo lógico', if_.linea)  # 214

    def regla_B3(self):  # B -> for (N;E;M) {C}
        self.pila_aux.pop()
        c = self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        for_ = self.pila_aux.pop()
        b = self.pila_aux[-1]

        if e.tipo == 'logico':
            b.tipo = c.tipo
            b.ret = c.ret
        else:
            b.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'Expresión no válida', for_.linea)  # 215

    def regla_N1(self):  # N -> ID = E
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        n = self.pila_aux[-1]

        if self.gestor_ts.buscar_simbolo_ts(id_.pos)['tipo'] == e.tipo:
            n.tipo = 'ok'
        else:
            n.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'El tipo de valor asignado es incompatible con el tipo de la variable',
                                    id_.linea)  # 216

    def regla_N2(self):  # N -> lambda
        self.pila_aux[-1].tipo = 'ok'

    def regla_M1(self):  # M -> N
        n = self.pila_aux.pop()
        m = self.pila_aux[-1]
        m.tipo = n.tipo

    def regla_M2(self):  # M -> ++ ID
        id_ = self.pila_aux.pop()
        elem = self.pila_aux.pop()
        m = self.pila_aux[-1]

        if self.gestor_ts.buscar_simbolo_ts(id_.pos)['tipo'] == 'entero':
            m.tipo = 'ok'
        else:
            m.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'Solo se puede auto incrementar variables de tipo entero',
                                    elem.linea)  # 210

    def regla_S1(self):  # S -> ID G ;
        self.pila_aux.pop()
        g = self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        s = self.pila_aux[-1]

        id_simbolo = self.gestor_ts.buscar_simbolo_ts(id_.pos)
        if id_simbolo['tipo'] == 'funcion':
            if id_simbolo['tipoParam'] == g.tipo:
                s.tipo = 'ok'
            else:
                s.tipo = 'error'
                self.gestor_err.imprime('Semántico', 'Los tipos de los parámetros no coinciden', id_.linea)  # 212
        elif id_simbolo['tipo'] == g.tipo:
            s.tipo = 'ok'
        else:
            s.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'El tipo de la variable no coincide', id_.linea)  # 217
        s.ret = 'vacio'

    def regla_S2(self):  # S -> ++ ID ;
        self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        self.pila_aux.pop()
        s = self.pila_aux[-1]

        if self.gestor_ts.buscar_simbolo_ts(id_.pos)['tipo'] == 'entero':
            s.tipo = 'ok'
        else:
            s.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'Solo se puede auto incrementar variables de tipo entero',
                                    id_.linea)  # 210
        s.ret = 'vacio'

    def regla_G1(self):  # G -> = E
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        g = self.pila_aux[-1]
        g.tipo = e.tipo

    def regla_G2(self):  # G -> ( L )
        self.pila_aux.pop()
        ll = self.pila_aux.pop()
        self.pila_aux.pop()
        g = self.pila_aux[-1]
        g.tipo = ll.tipo

    def regla_S3(self):  # S -> input ( ID ) ;
        self.pila_aux.pop()
        self.pila_aux.pop()
        id_ = self.pila_aux.pop()
        self.pila_aux.pop()
        self.pila_aux.pop()
        s = self.pila_aux[-1]

        if self.gestor_ts.buscar_simbolo_ts(id_.pos)['tipo'] == 'logico':
            s.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'No se admite una variable de tipo lógico', id_.linea)  # 218
        else:
            s.tipo = 'ok'
        s.ret = 'vacio'

    def regla_S4(self):  # S -> alert ( E ) ;
        self.pila_aux.pop()
        self.pila_aux.pop()
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        alert = self.pila_aux.pop()
        s = self.pila_aux[-1]

        if e.tipo == 'logico':
            s.tipo = 'error'
            self.gestor_err.imprime('Semántico', 'No se admite una expresión de tipo lógico', alert.linea)  # 219
        else:
            s.tipo = 'ok'
        s.ret = 'vacio'

    def regla_S5(self):  # S -> return X ;
        self.pila_aux.pop()
        x = self.pila_aux.pop()
        self.pila_aux.pop()
        s = self.pila_aux[-1]
        s.tipo = 'ok'
        s.ret = x.tipo

    def regla_X(self):  # X -> E
        e = self.pila_aux.pop()
        x = self.pila_aux[-1]
        x.tipo = e.tipo

    def regla_L(self):  # L -> E Q
        q = self.pila_aux.pop()
        e = self.pila_aux.pop()
        ll = self.pila_aux[-1]

        if q.tipo == 'vacio':
            ll.tipo = e.tipo
        else:
            ll.tipo = e.tipo + ' ' + q.tipo

    def regla_Q(self):  # Q -> , E Q1
        q1 = self.pila_aux.pop()
        e = self.pila_aux.pop()
        self.pila_aux.pop()
        q = self.pila_aux[-1]

        if q1.tipo == 'vacio':
            q.tipo = e.tipo
        else:
            q.tipo = e.tipo + ' ' + q1.tipo

    def regla_H(self):  # H -> T
        t = self.pila_aux.pop()
        h = self.pila_aux[-1]
        h.tipo = t.tipo

    def regla_T1(self):  # T -> boolean
        self.pila_aux.pop()
        self.pila_aux[-1].tipo = 'logico'
        self.pila_aux[-1].ancho = 1

    def regla_T2(self):  # T -> string
        self.pila_aux.pop()
        self.pila_aux[-1].tipo = 'cadena'
        self.pila_aux[-1].ancho = 64

    def regla_T3(self):  # T -> number
        self.pila_aux.pop()
        self.pila_aux[-1].tipo = 'entero'
        self.pila_aux[-1].ancho = 1

    def regla_A1(self):  # A -> T ID
        id_ = self.pila_aux[-1]
        t = self.pila_aux[-2]
        self.gestor_ts.aniadir_var_atributos_ts_activa(id_.pos, t.tipo, t.ancho)

    def regla_A2(self):  # A -> T ID K
        k = self.pila_aux.pop()
        self.pila_aux.pop()
        t = self.pila_aux.pop()
        a = self.pila_aux[-1]

        if k.tipo == 'vacio':
            a.tipo = t.tipo
        else:
            a.tipo = t.tipo + ' ' + k.tipo

    def regla_K1(self):  # K -> , T ID
        id_ = self.pila_aux[-1]
        t = self.pila_aux[-2]
        self.gestor_ts.aniadir_var_atributos_ts_activa(id_.pos, t.tipo, t.ancho)

    def regla_K2(self):  # K -> , T ID K1
        k1 = self.pila_aux.pop()
        self.pila_aux.pop()
        t = self.pila_aux.pop()
        self.pila_aux.pop()

        k = self.pila_aux[-1]
        if k1.tipo == 'vacio':
            k.tipo = t.tipo
        else:
            k.tipo = t.tipo + ' ' + k1.tipo

    def regla_lambda(self):  # no_terminal -> lambda
        no_terminal = self.pila_aux[-1]
        no_terminal.tipo = 'vacio'
