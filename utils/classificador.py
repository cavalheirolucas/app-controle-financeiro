import os
from openai import OpenAI
import json
from utils.supabase_client import get_client


CATEGORIAS = [
    "transporte",
    "alimentação",
    "saúde",
    "lazer",
    "moradia",
    "educação",
    "salário",
    "investimento",
    "outros"
]

# regras por palavra-chave — cobre os casos mais comuns sem custo
REGRAS = {
    "transporte": [
        "uber", "99pop", "cabify", "combustivel", "posto", "metrô",
        "ônibus", "estacionamento", "pedágio", "sem parar", "bpk",
        "auto posto", "shell", "ipiranga", "br distribuidora",
    ],
    "alimentação": [
        "ifood", "rappi", "restaurante", "mercado", "padaria",
        "supermercado", "lanche", "pizza", "burger", "açougue",
        "hortifruti", "pão de açúcar", "carrefour", "extra", "atacadão",
        "assaí", "sams club", "walmart", "subway", "mcdonalds", "burger king","panificadora",
    ],
    "saúde": [
        "farmácia", "drogaria", "drogasil", "ultrafarma", "pacheco",
        "médico", "hospital", "laboratório", "plano de saúde", "unimed",
        "amil", "bradesco saude", "hapvida", "clinica",
    ],
    "lazer": [
        "cinema", "netflix", "spotify", "steam", "show", "teatro",
        "ingresso", "disney", "youtube", "amazon prime", "hbo", "globoplay",
        "paramount", "apple tv", "deezer",
    ],
    "moradia": [
        "aluguel", "condomínio", "luz", "energia", "água", "saneamento",
        "internet", "claro", "vivo", "tim", "oi", "gás", "enel",
        "cemig", "copel", "sabesp", "cedae",
    ],
    "educação": [
        "curso", "udemy", "alura", "livro", "escola", "faculdade",
        "mensalidade", "material escolar", "datacamp", "coursera",
        "dio", "rocketseat",
    ],
    "salário": [
        "salário", "pagamento", "holerite", "folha", "prolabore",
        "remuneracao", "vencimento",
    ],
    "investimento": [
        "investimento", "cdb", "tesouro", "ações", "fundo", "corretora",
        "xp", "rico", "inter invest", "nuinvest", "btg", "itaú corretora",
    ],
}




def _classificar_regras(descricao):
    for categoria, palavras in REGRAS.items():
        if any(palavra.lower() in descricao.lower() for palavra in palavras):
            return categoria
        

def _classificar_ia(descricao):
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
    
    resultado = {}
    prompt = f""" 
            Classifier each description with one category
            Categories: {CATEGORIAS}
            Descriptions: {descricao}

            Answer with only one category!
        
        """ 


    completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
            {"role": "system", "content": "Return a valide json"},
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    resultado = json.loads(
    completion.choices[0].message.content
)

    return resultado



def classificar_lote(descricoes):
    supabase = get_client()
    resultado = {}
    sem_regra = []

    for descricao in descricoes:
        categoria = _classificar_regras(descricao)
        if categoria:
            resultado[descricao] = categoria
        else:
            sem_regra.append(descricao)

    if not sem_regra:
        return resultado
    
    sem_cache = []

    for descricao in sem_regra:

        palavras = descricao.split()
        palavra_chave = max(palavras, key=len)

        response = supabase.table("classificacoes_financeiras").select("categoria").ilike("descricao", f"%{palavra_chave}%").execute()


        if response.data:
            resultado[descricao] = response.data[0]["categoria"]
        else:
            sem_cache.append(descricao) 

    if not sem_cache:
        return resultado
    

    result = _classificar_ia(sem_cache)
    sem_ia = []
    for descricao in sem_cache:
        if descricao in result:
            resultado[descricao] = result[descricao]
        else:
            sem_ia.append(descricao) 


    
    for descricao in sem_ia:
        resultado[descricao] = ""
        
    return resultado
