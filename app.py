from flask import Flask, request, render_template_string
from lark import Lark, exceptions
import html

app = Flask(__name__)

gramatica = r"""
    ?expresion: termino (("+"|"-") termino)*
    ?termino: factor (("*"|"/") factor)*
    ?factor: NUMERO -> numero
           | "(" expresion ")"
    %import common.NUMBER -> NUMERO
    %import common.WS
    %ignore WS
"""

parser = Lark(gramatica, start='expresion')

NOMBRES_TOKENS = {
    'ADD': "un '+' (suma)",
    'SUB': "un '-' (resta)",
    'MUL': "un '*' (multiplicación)",
    'DIV': "un '/' (división)",
    'LPAR': "un '(' (paréntesis de apertura)",
    'RPAR': "un ')' (paréntesis de cierre)",
    'NUMERO': "un NÚMERO",
    'END_OF_INPUT': "el FIN de la expresión",
}

def obtener_mensaje_error(e):
    if isinstance(e, exceptions.UnexpectedToken):
        esperados = [NOMBRES_TOKENS.get(t, t) for t in e.expected]
        encontrado = NOMBRES_TOKENS.get(e.token.type, f"'{e.token}'")
        return f"Error de sintaxis: Se encontró {encontrado} inesperadamente.\nSe esperaba uno de: [ {', '.join(esperados)} ]"
    
    if isinstance(e, exceptions.UnexpectedCharacters):
        return f"Error de sintaxis: Caracter inesperado '{e.char}' en la línea {e.line}, columna {e.column}."
    
    return f"Error desconocido: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    entrada = ""
    resultado_html = "<p><i>Esperando entrada para validación...</i></p>"

    if request.method == 'POST':
        entrada = request.form.get('expresion', '')
        entrada_segura = html.escape(entrada)

        if not entrada.strip():
            resultado_html = """
            <div class="resultado invalido">
                <h3>CADENA INVÁLIDA</h3>
                <pre>Error: La entrada está vacía.</pre>
            </div>
            """
        else:
            try:
                arbol = parser.parse(entrada)
                arbol_str = html.escape(arbol.pretty())
                resultado_html = f"""
                <div class="resultado valido">
                    <h3>CADENA VÁLIDA</h3>
                    <p>La expresión es sintácticamente correcta. Este es su árbol de derivación:</p>
                    <pre>{arbol_str}</pre>
                </div>
                """
            except Exception as e:
                mensaje = html.escape(obtener_mensaje_error(e))
                resultado_html = f"""
                <div class="resultado invalido">
                    <h3>CADENA INVÁLIDA</h3>
                    <p>La expresión no pertenece al lenguaje definido por la gramática:</p>
                    <pre>{mensaje}</pre>
                </div>
                """
        
        return render_template_string(HTML_TEMPLATE, expresion_actual=entrada_segura, resultado_html=resultado_html)

    return render_template_string(HTML_TEMPLATE, expresion_actual="", resultado_html=resultado_html)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proyecto 2: Validador aritmético (ES)</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 20px auto; padding: 25px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); }
        h1 { color: #1a1a1a; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        p { line-height: 1.6; }
        form { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex-grow: 1; padding: 12px; font-size: 1.1em; border: 2px solid #ddd; border-radius: 6px; transition: border-color 0.3s; }
        input[type="text"]:focus { border-color: #007bff; outline: none; }
        button { padding: 12px 20px; font-size: 1.1em; font-weight: bold; color: #fff; background-color: #007bff; border: none; border-radius: 6px; cursor: pointer; transition: background-color 0.3s; }
        button:hover { background-color: #0056b3; }
        .resultado { padding: 15px; border-radius: 6px; margin-top: 20px; }
        .valido { background-color: #e6f8ec; border: 2px solid #5cb85c; color: #1e4620; }
        .invalido { background-color: #fdeeee; border: 2px solid #d9534f; color: #a94442; }
        .resultado h3 { margin-top: 0; }
        pre { background-color: #fdfdfd; border: 1px solid #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Validador de expresiones aritméticas</h1>
        <p>Introduce una expresión (ej. <code>2 * (3 + 4)</code>) para validar su sintaxis usando una Gramática Independiente del Contexto.</p>
        <form method="POST" action="/">
            <input type="text" name="expresion" placeholder="Escribe tu expresión..." value="{{ expresion_actual }}">
            <button type="submit">Validar</button>
        </form>
        {{ resultado_html | safe }}
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    print("Servidor corriendo en http://127.0.0.1:5000")
    app.run(debug=True)