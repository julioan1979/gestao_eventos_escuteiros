# Gestão de Eventos Escutistas

Aplicação Streamlit para gerir pedidos, recebimentos, sangrias de caixa e
configurações administrativas de eventos escutistas com persistência no
Airtable.

## Requisitos

- Python 3.10+
- Conta Airtable com as tabelas descritas no projeto

## Configuração

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure as credenciais Airtable no ficheiro `.streamlit/secrets.toml`:

   ```toml
   [airtable]
   api_key = "SUA_API_KEY"
   base_id = "SUA_BASE_ID"
   ```

   > **Nota:** Não commit o ficheiro com credenciais reais.

3. Execute a aplicação:

   ```bash
   streamlit run app.py
   ```

## Estrutura

- `app.py`: ponto de entrada com autenticação e navegação.
- `data/`: integração com Airtable e utilidades de cache/transformação.
- `pages/`: páginas individuais da aplicação.
- `utils/`: componentes de layout, formulários e estilos partilhados.
