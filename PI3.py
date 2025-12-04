import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Tech Insights Dashboard", layout="wide", page_icon="⚡")

# --- DEFINIÇÕES DE NEGÓCIO ---
# Categorias CORE (Produtos principais/caros)
CATS_CORE = ['telefonia', 'consoles_games', 'pcs', 'pc_gamer', 'tablets_impressao_imagem']

# Categorias ACESSÓRIOS (Produtos complementares/venda cruzada)
CATS_ACESSORIOS = ['informatica_acessorios', 'audio', 'eletronicos', 'telefonia_fixa']

ALL_CATS = CATS_CORE + CATS_ACESSORIOS

# --- FUNÇÃO DE CARGA DE DADOS ---
@st.cache_data
def load_data():
    try:
        df_vendas = pd.read_csv("Base De Dados Limpa.csv")
        # Filtra apenas Eletrônicos
        df_vendas = df_vendas[df_vendas['product_category_name'].isin(ALL_CATS)]
        
        # Datas
        df_vendas['order_purchase_timestamp'] = pd.to_datetime(df_vendas['order_purchase_timestamp'])
        df_vendas['mes_ano'] = df_vendas['order_purchase_timestamp'].dt.to_period('M').astype(str)
        
        # Classificação do Produto (Core vs Acessório)
        df_vendas['Tipo_Produto'] = df_vendas['product_category_name'].apply(
            lambda x: 'Core (Principal)' if x in CATS_CORE else 'Acessório (Cross-Sell)'
        )
        
    except FileNotFoundError:
        return None, None

    try:
        df_churn = pd.read_csv("analise_churn_processada.csv")
        # Filtra Churn apenas para clientes presentes na base de eletrônicos
        clientes_tech = df_vendas['customer_unique_id'].unique()
        df_churn = df_churn[df_churn['ID_Cliente'].isin(clientes_tech)]
    except FileNotFoundError:
        return None, None
        
    return df_vendas, df_churn

df_vendas, df_churn = load_data()

# --- SIDEBAR: CONTEXTO ESTRATÉGICO ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3094/3094367.png", width=50)
st.sidebar.title("Tech Insights")
st.sidebar.markdown("**Estratégia do Projeto:**")
st.sidebar.info("""
Este dashboard foca exclusivamente no nicho de **Eletrônicos**.

**Por que este recorte?**
1. **Ticket Médio:** Eletrônicos possuem valor agregado maior, exigindo análise de crédito e parcelamento diferenciada.
2. **Ciclo de Vida:** O Churn em tecnologia é diferente de commodities. A "Recência" alta é esperada (ninguém compra TV todo mês).
""")

st.sidebar.markdown("---")
st.sidebar.header("Filtros Operacionais")
estados = sorted(df_vendas['customer_state'].unique()) if df_vendas is not None else []
estado_selecionado = st.sidebar.multiselect("Filtrar Estado (UF)", estados, default=['SP', 'RJ', 'MG'])

# --- APLICAÇÃO DE FILTROS ---
if df_vendas is not None and not df_vendas.empty:
    if estado_selecionado:
        df_filtered = df_vendas[df_vendas['customer_state'].isin(estado_selecionado)]
    else:
        df_filtered = df_vendas
else:
    df_filtered = pd.DataFrame()

# --- LAYOUT PRINCIPAL ---

if not df_filtered.empty:
    st.title("⚡ Dashboard Gerencial: Vendas & Retenção (Tech)")
    st.markdown("Visão consolidada de performance comercial e saúde da base de clientes.")
    st.markdown("---")

    # 1. KPIs DE ALTO NÍVEL
    col1, col2, col3, col4 = st.columns(4)
    
    total_fat = df_filtered['price'].sum()
    ticket_medio = total_fat / df_filtered['order_id'].nunique()
    churn_rate = (df_churn[df_churn['Churn']=='Sim'].shape[0] / df_churn.shape[0] * 100) if not df_churn.empty else 0
    
    # KPI de Oportunidade
    qtd_core = df_filtered[df_filtered['Tipo_Produto'] == 'Core (Principal)'].shape[0]
    qtd_acessorios = df_filtered[df_filtered['Tipo_Produto'] == 'Acessório (Cross-Sell)'].shape[0]
    ratio_cross = qtd_acessorios / qtd_core if qtd_core > 0 else 0

    col1.metric("Faturamento Total", f"R$ {total_fat:,.2f}")
    col2.metric("Ticket Médio (Tech)", f"R$ {ticket_medio:,.2f}", delta="Alto Valor Agregado", delta_color="normal")
    col3.metric("Taxa de Churn Estimada", f"{churn_rate:.1f}%", help="Baseado em Recência > 140 dias")
    col4.metric("Ratio Acessórios/Core", f"{ratio_cross:.2f}", help="Para cada 1 produto principal, vendemos X acessórios")

    # 2. SEÇÃO DE BUSINESS INTELLIGENCE (A PARTE QUE O GESTOR QUER VER)
    with st.expander("📊 Análise Estratégica & Oportunidades (Clique para expandir)", expanded=True):
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("### 💡 Insights Automáticos")
            if ratio_cross < 1.0:
                st.warning(f"**Alerta de Oportunidade:** Estamos vendendo apenas **{qtd_acessorios}** acessórios para **{qtd_core}** produtos principais (PCs/Consoles).")
                st.markdown("👉 **Ação Sugerida:** Criar bundles (kits). Ex: Quem compra Notebook ganha 20% de desconto no Mouse/Mochila.")
            else:
                st.success("A estratégia de venda cruzada está saudável. Temos mais acessórios saindo do que produtos principais.")
                
            st.markdown("---")
            st.markdown("**Análise de Churn:**")
            st.caption("A alta taxa de churn pode indicar que clientes compram o item durável (TV/PC) e não retornam para comprar periféricos. Recomenda-se campanhas de email mkt pós-venda focadas em acessórios.")

        with c2:
            # Gráfico de Vendas por Tipo (Core vs Acessório)
            fig_bar_type = px.bar(
                df_filtered.groupby('Tipo_Produto')['price'].sum().reset_index(),
                x='price', y='Tipo_Produto', orientation='h', 
                title='Onde está o dinheiro? (Core vs Acessórios)',
                color='Tipo_Produto', color_discrete_map={'Core (Principal)':'#1f77b4', 'Acessório (Cross-Sell)':'#ff7f0e'}
            )
            st.plotly_chart(fig_bar_type, use_container_width=True)

    st.markdown("---")

    # 3. GRÁFICOS OPERACIONAIS
    st.subheader("📈 Performance Operacional")
    
    g1, g2 = st.columns(2)
    
    with g1:
        vendas_mes = df_filtered.groupby('mes_ano')['price'].sum().reset_index()
        fig_line = px.line(vendas_mes, x='mes_ano', y='price', markers=True, title="Tendência de Vendas Mensal")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with g2:
        # Top Categorias
        fig_cat = px.bar(
            df_filtered['product_category_name'].value_counts().head(5).reset_index(),
            x='product_category_name', y='count', title="Top 5 Categorias Mais Vendidas"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # 4. ANÁLISE DE PERFIL DE CLIENTE (RFM)
    if not df_churn.empty:
        st.markdown("---")
        st.subheader("👥 Perfil do Cliente & Risco (RFM)")
        
        r1, r2 = st.columns(2)
        with r1:
            # Dispersão
            fig_scatter = px.scatter(
                df_churn, x='Recencia (dias)', y='Valor Monetario (R$)', color='Churn',
                log_y=True, title="Matriz de Risco: Valor x Tempo sem Comprar",
                color_discrete_map={'Sim':'red', 'Não':'blue'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with r2:
            # Histograma de Recência
            fig_hist = px.histogram(df_churn, x='Recencia (dias)', color='Churn', 
                                  title="Distribuição de Dias sem Comprar", nbins=20,
                                  color_discrete_map={'Sim':'red', 'Não':'blue'})
            st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.error("Arquivos não encontrados ou erro no filtro de dados. Verifique se os CSVs estão na pasta.")
# --- Configuração dos Dados (Simulando o gráfico que você enviou) ---
def carregar_dados_estoque():
    # Estou recriando os valores aproximados do gráfico da imagem
    data = {
        'Categoria': ['Informatica_Ace', 'Telefonia', 'Eletronicos', 'Relogios_Presen', 'Consoles_Games'],
        'Demanda Prevista (IA)': [55, 132, 375, 285, 208],
        'Estoque Atual': [46, 112, 318, 242, 176]
    }
    df = pd.DataFrame(data)
    # Calculando a Ruptura (Diferença) e o Risco
    df['Diferença (Ruptura)'] = df['Demanda Prevista (IA)'] - df['Estoque Atual']
    df['Status'] = df.apply(lambda x: 'CRÍTICO' if x['Estoque Atual'] < x['Demanda Prevista (IA)'] else 'OK', axis=1)
    return df

# --- Função Principal da Tela de Ruptura ---
def show_page_estoque():
    st.title("📈 Inteligência Comercial: Monitor de Ruptura")
    
    # --- 1. A Narrativa (Opção 3) ---
    st.markdown("""
    ### Do Estoque à Fidelização
    Não adianta prever o **Churn** se o cliente não encontra o que comprar. Nossa plataforma unifica a gestão operacional e a retenção de clientes.
    
    * **🚫 O Problema:** A ruptura de estoque frustra o cliente e dispara o risco de cancelamento.
    * **✅ A Solução:** Nosso monitor utiliza **IA** para cruzar estoque atual com demanda prevista.
    """)
    
    st.divider()

    # Carrega os dados
    df_estoque = carregar_dados_estoque()

    # --- 2. Preparação do Gráfico Interativo ---
    # Transformando o dataframe para o formato longo (ideal para gráficos agrupados)
    df_melted = df_estoque.melt(id_vars=['Categoria', 'Diferença (Ruptura)', 'Status'], 
                                value_vars=['Demanda Prevista (IA)', 'Estoque Atual'], 
                                var_name='Métrica', 
                                value_name='Quantidade')

    # Criando o gráfico com Plotly (Interativo)
    fig = px.bar(
        df_melted, 
        x='Categoria', 
        y='Quantidade', 
        color='Métrica',
        barmode='group',
        text_auto=True,
        title='MONITOR DE ALERTA: ESTOQUE VS DEMANDA PREVISTA',
        color_discrete_map={
            'Demanda Prevista (IA)': '#3498db', # Azul similar ao da imagem
            'Estoque Atual': '#c0392b'          # Vermelho similar ao da imagem
        },
        height=500
    )
    
    fig.update_layout(xaxis_title=None, yaxis_title="Unidades")
    
    # Exibindo o Gráfico
    st.plotly_chart(fig, use_container_width=True)

    # --- 3. Insights Automáticos e Ação ---
    st.subheader("⚠️ Alerta de Ação Imediata")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("As categorias abaixo apresentam **Risco de Ruptura**. A demanda prevista pela IA é maior que o estoque físico.")
        # Mostra apenas as colunas relevantes numa tabela limpa
        st.dataframe(
            df_estoque[['Categoria', 'Demanda Prevista (IA)', 'Estoque Atual', 'Diferença (Ruptura)']]
            .style.highlight_max(axis=0, subset=['Diferença (Ruptura)'], color='#ffcccc'),
            hide_index=True,
            use_container_width=True
        )

    with col2:
        # Destaque do maior risco
        maior_risco = df_estoque.loc[df_estoque['Diferença (Ruptura)'].idxmax()]
        st.metric(
            label=f"Maior Risco: {maior_risco['Categoria']}",
            value=f"{maior_risco['Estoque Atual']} Unid.",
            delta=f"-{maior_risco['Diferença (Ruptura)']} faltantes",
            delta_color="inverse"
        )
        st.button("Gerar Pedido de Reposição 🚀", type="primary")

# --- Chamada da função (se for rodar direto para testar) ---
if __name__ == "__main__":
    show_page_estoque()