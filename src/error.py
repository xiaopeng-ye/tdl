class GestorError:

    def __init__(self):
        self._error_file = open('error.txt', 'w', encoding='UTF-8')
        self.error_lexico = {100: "No es válido empezar con '_' en un identificador",
                             101: 'Carácter inválido',
                             102: "Después de '\\', se espera una ' o '\\', para establecer la secuencia de escape",
                             103: "Se espera el carácter '&' después de '&'",
                             104: "Se espera el carácter '|' después de '|'",
                             105: "Se espera el carácter '/' después de '/'",
                             106: "Se espera el carácter '=' después de '!'",
                             107: "Ya existe el identificador a declarar",
                             108: "Número incorrecto, debe corresponder a un valor de 16 bits",
                             109: "Cadena con longitud inválido, debe ser menor de 65 caracteres"}

    def imprime(self, analizador, mensaje, linea):
        self._error_file.write(f'Error {analizador}: {mensaje} en la línea {linea}')
        self._error_file.close()
        raise Exception(f'Error {analizador}: {mensaje} en la línea {linea}')
