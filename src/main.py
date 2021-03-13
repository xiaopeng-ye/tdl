import sys
from parse import JSParser

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: programa.exe [ruta del código]', file=sys.stderr)
        sys.exit(1)

    try:
        parser = JSParser()
        parser.parse(sys.argv[1])
    except FileNotFoundError as fe:
        print(f'No existe el fichero {fe.filename}', file=sys.stderr)
    except Exception as e:
        print(e, file=sys.stderr)
        print('Error encontrado', file=sys.stderr)
