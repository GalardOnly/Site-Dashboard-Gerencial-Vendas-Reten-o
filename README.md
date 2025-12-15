# 📊 Site Dashboard Gerencial: Vendas e Retenção (PI3)

Este repositório contém o código-fonte e os dados utilizados no desenvolvimento de um Dashboard Gerencial focado na análise de vendas e retenção de clientes (Churn).

O projeto foi desenvolvido em **Python**, processando bases de dados para gerar insights visuais sobre a performance comercial e indicadores de cancelamento.

## 🚀 Funcionalidades

* **Análise de Vendas:** Visualização de indicadores de performance comercial baseada na `Base De Dados Limpa.csv`.
* **Análise de Churn:** Monitoramento de taxas de retenção e cancelamento de clientes utilizando a `analise_churn_processada.csv`.
* **Interface Interativa:** Dashboard gerado através do script `PI3.py`.

## 📂 Estrutura do Projeto

* `PI3.py`: Arquivo principal da aplicação (Script do Dashboard).
* `Base De Dados Limpa.csv`: Dataset contendo os dados de vendas sanitizados.
* `analise_churn_processada.csv`: Dataset contendo os dados processados para análise de churn.
* `requirements.txt`: Lista de bibliotecas e dependências necessárias para rodar o projeto.
* `.devcontainer/`: Configurações para desenvolvimento em container (Docker/VS Code).

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Bibliotecas:** (Provavelmente pandas, numpy, e a biblioteca de dashboard - *Ex: Streamlit, Dash ou Plotly*)
* **Ambiente:** Suporte a DevContainers.

## 📦 Como Executar o Projeto localmente

Para rodar este projeto na sua máquina, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/GalardOnly/Site-Dashboard-Gerencial-Vendas-Reten-o.git](https://github.com/GalardOnly/Site-Dashboard-Gerencial-Vendas-Reten-o.git)
    cd Site-Dashboard-Gerencial-Vendas-Reten-o
    ```

2.  **Crie um ambiente virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use: venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    *Se o projeto usar Streamlit:*
    ```bash
    streamlit run PI3.py
    ```
    *Ou, se for um script Python padrão:*
    ```bash
    python PI3.py
    ```

## 🤝 Autores

* **GalardOnly** - *Desenvolvimento e Análise*

*Este projeto faz parte do PI3 (Projeto Integrador).*
