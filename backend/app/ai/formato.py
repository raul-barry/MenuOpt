"""Normaliza las respuestas visibles del asistente a texto plano legible."""
import re


_EMOJI_RE = re.compile(
    "["
    "\\U0001F1E6-\\U0001F1FF"
    "\\U0001F300-\\U0001FAFF"
    "\\u2600-\\u27BF"
    "\\uFE0F\\u200D\\u20E3"
    "]"
)
_EMOTICON_RE = re.compile(r"(?<!\w)(?::|;|=|8|x|X)(?:[-^']?)[)(DPp/\\]|<3(?!\w)")
_MOJIBAKE_MAP = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã¼": "ü", "Ã": "Á", "Ã‰": "É", "Ã": "Í",
    "Ã“": "Ó", "Ãš": "Ú", "Ã‘": "Ñ", "Â¿": "¿", "Â¡": "¡",
    "ÃƒÂ¡": "á", "ÃƒÂ©": "é", "ÃƒÂ­": "í", "ÃƒÂ³": "ó",
    "ÃƒÂº": "ú", "ÃƒÂ±": "ñ", "Ã‚Â¿": "¿", "Ã‚Â¡": "¡",
}


def normalizar_respuesta(texto: str) -> str:
    """Quita adornos Markdown y emojis sin alterar el contenido de la respuesta."""
    if not texto:
        return ""

    # Corrige secuencias UTF-8 que llegaron decodificadas como Latin-1/Windows-1252.
    for origen, destino in _MOJIBAKE_MAP.items():
        texto = texto.replace(origen, destino)

    lineas = []
    for linea in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        linea = re.sub(r"^\s{0,3}#{1,6}\s*", "", linea)
        linea = re.sub(r"^\s*>\s?", "", linea)
        linea = re.sub(r"^\s*[*+]\s+", "- ", linea)
        linea = re.sub(r"^\s*-{3,}\s*$", "", linea)
        lineas.append(linea)

    texto = "\n".join(lineas)
    texto = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", texto)
    texto = texto.replace("```", "").replace("`", "")
    texto = texto.replace("**", "").replace("__", "")
    texto = re.sub(r"(?<!\w)[*_](?=\S)|(?<=\S)[*_](?!\w)", "", texto)
    texto = _EMOJI_RE.sub("", texto)
    texto = _EMOTICON_RE.sub("", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r" *\n *", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()
