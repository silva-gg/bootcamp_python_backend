def formatar_mensagem(texto):
    # Remove espaços extras do início e do fim da string
    texto = texto.strip()
    
    if texto == "":
      return texto
    
    palavra = ""
    texto_cleaned = []    
    texto = texto.lower()
    for char in texto:
      if char != " ":
        palavra += char
      elif char == " ":
        texto_cleaned.append(palavra) if palavra != "" else None
        palavra = ""
    texto_cleaned.append(palavra) if palavra != "" else None
    return " ".join(texto_cleaned)

# Lê a mensagem enviada ao robô via input padrão
entrada = input()  # Tipo de dado esperado: str

# Chama a função formatar_mensagem (você irá implementar a lógica)
saida = formatar_mensagem(entrada)

# Exibe a mensagem padronizada
print(saida)