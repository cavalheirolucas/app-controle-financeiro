# 💰 App de Controle Financeiro Pessoal

App de controle financeiro pessoal com autenticação por usuário, upload de extratos bancários e fatura de cartão, classificação inteligente de transações e dashboard analítico.

---

## Funcionalidades

- **Autenticação** — cadastro e login por email e senha, com sessão isolada por usuário
- **Upload de extrato** — suporte a CSV de qualquer banco, com mapeamento flexível de colunas
- **Fatura de cartão** — lógica separada para cartão de crédito (valores positivos = despesa)
- **Classificação inteligente** — transações classificadas automaticamente em 4 camadas:
  - Regras por palavra-chave (grátis, instantâneo)
  - Cache no banco (reutiliza classificações anteriores)
  - IA (Usa api do ChatGPT para classificar os casos faltantes)
  - Revisão manual pelo usuário antes de salvar
- **Deduplicação** — evita inserir a mesma transação duas vezes
- **Dashboard** — visualização de saldo, gastos por categoria e evolução mensal
- **Segurança** — cada usuário acessa apenas os próprios dados via Row Level Security (RLS)

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Dashboard / Frontend | Streamlit |
| Banco de dados | Supabase (PostgreSQL) |
| Autenticação | Supabase Auth |
| ORM / Queries | supabase-py |
| Transformação de dados | pandas |
| Classificação dos dados | openai |
| Gráficos | Plotly |
| Gerenciamento de dependências | Poetry |
| Containerização | Docker |
| Deploy | Render |

---

## Arquitetura

```
Usuário
  ↓
Streamlit (frontend + dashboard)
  ↓
Supabase Auth → valida sessão e gera JWT
  ↓
PostgREST → API REST gerada automaticamente do schema SQL
  ↓
PostgreSQL
  ├── transacoes_financeiras  (dados por usuário, isolados via RLS)
  ├── classificacoes          (dicionário compartilhado entre usuários)

```

## Fluxo de classificação

```
Descrição do CSV
      ↓
1. Regra por palavra-chave → grátis e instantâneo
      ↓ (se não encontrar)
2. Cache no banco → reutiliza classificações já feitas
      ↓ (se não encontrar)
3. gpt-5.5 para classificação dos casos faltantes
      ↓ (se não encontrar)
4. Revisão manual pelo usuário no frontend
      ↓
Salvo no banco para uso futuro
```

## Segurança

O Supabase usa **Row Level Security (RLS)** no nível do banco de dados — cada usuário só acessa os próprios dados, independente de como a requisição chegou. O JWT gerado no login é enviado em cada requisição e o PostgreSQL valida `auth.uid() = user_id` antes de retornar qualquer dado.


## Deploy

O app está hospedado no **Render** via Docker.

- A imagem é buildada a partir do `Dockerfile` na raiz do repositório
- Todo `git push` na branch `main` dispara um novo deploy automaticamente
- As variáveis de ambiente (`SUPABASE_URL`, `SUPABASE_TOKEN`, `ANTHROPIC_KEY`) são configuradas diretamente no painel do Render

🔗 **[Acesse o app aqui](## Deploy

O app está hospedado no **Render** via Docker.

- A imagem é buildada a partir do `Dockerfile` na raiz do repositório
- Todo `git push` na branch `main` dispara um novo deploy automaticamente
- As variáveis de ambiente (`SUPABASE_URL`, `SUPABASE_TOKEN`, `ANTHROPIC_KEY`) são configuradas diretamente no painel do Render

🔗 **[Acesse o app aqui](https://seu-app.onrender.com)**