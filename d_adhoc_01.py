import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
import plotly.express as px
#import plotly.offline as py
import folium
from folium import Figure
#from branca.element import Figure
#from IPython.display import HTML
import plotly.graph_objs as go
#import requests
#import io
from flask import Flask, render_template, request

app = Flask(__name__)

url = 'https://github.com/marcilioduarte/sebraemg-public-01-report-example/raw/main/data/empresas_ariel_3.xlsx'

df = pd.read_excel(url, engine='openpyxl')

# Tratamento para a coluna situacao_cadastral
dict_situacao_cadastral = {2: "Ativa", 4: "Inapta"}
df['situacao_cadastral'] = df['situacao_cadastral'].map(dict_situacao_cadastral)

# Tratamento para a coluna foi_atendido
dict_foi_atendido = {0: "Não", 1: "Sim"}
df['foi_atendido'] = df['foi_atendido'].map(dict_foi_atendido)

# Tratamento para a coluna porte_empresa
dict_porte_empresa = {1: "Micro empresa", 3: "EPP", 5: "Demais"}
df['porte_empresa'] = df['porte_empresa'].map(dict_porte_empresa)

# Tratamento de coluna de data
df['data_inicio_atividade'] = pd.to_datetime(df['data_inicio_atividade'], format='%Y%m%d')
df['data_inicio_atividade'] = df['data_inicio_atividade'].dt.strftime('%d/%m/%Y')

df['opcao_mei'].fillna('Não identificado', inplace=True)
dict_opcao_mei = {"N": "Não", "S": "Sim", "Não identificado": "Não identificado"}
df['opcao_mei'] = df['opcao_mei'].map(dict_opcao_mei)

def grafico_1(df):
    # Filtrando o DataFrame df para empresas ativas (situacao_cadastral igual a 2)
    df_ativas = df[df['situacao_cadastral'] == 'Ativa']

    # Filtrando o DataFrame df para empresas inaptas (situacao_cadastral igual a 4)
    df_inaptas = df[df['situacao_cadastral'] == 'Inapta']

    # Agrupando e contando a quantidade de empresas ativas por município
    df_municipios_ativas = df_ativas['municipio'].value_counts().reset_index()
    df_municipios_ativas.columns = ['Município', 'Empresas Ativas']

    # Agrupando e contando a quantidade de empresas inaptas por município
    df_municipios_inaptas = df_inaptas['municipio'].value_counts().reset_index()
    df_municipios_inaptas.columns = ['Município', 'Empresas Inaptas']

    # Mesclando os DataFrames criados
    df_municipios = df_municipios_ativas.merge(df_municipios_inaptas, on='Município', how='outer').fillna(0)
    df_municipios['Total de Empresas'] = df_municipios['Empresas Ativas'] + df_municipios['Empresas Inaptas']

    # Calculando as porcentagens de empresas ativas e inaptas
    df_municipios['% Empresas Ativas'] = (df_municipios['Empresas Ativas'] / (df_municipios['Empresas Ativas'] + df_municipios['Empresas Inaptas'])) * 100
    df_municipios['% Empresas Inaptas'] = (df_municipios['Empresas Inaptas'] / (df_municipios['Empresas Ativas'] + df_municipios['Empresas Inaptas'])) * 100

    # Criar um gráfico de barras empilhadas interativo com Plotly Express
    cores = ['#84f4bc', '#f4455a']
    fig = px.bar(df_municipios, x='Município', y=['% Empresas Ativas', '% Empresas Inaptas'],
                labels={'Município': 'Município', 'value': 'Percentual de Empresas'},
                title='Percentual de Empresas Ativas e Inaptas por Município',
                color_discrete_sequence=cores)

    # Atualizar o layout
    fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='#f9f9f9', paper_bgcolor='#f9f9f9', font=dict(color="#000000"))

    # Adicionar rótulos de texto personalizados
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside')

    # Atualizar o hovertemplate para incluir o número total de empresas
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Ativas: %{customdata[2]}<br>Empresas Inaptas: %{customdata[3]}<br>% Empresas Ativas: %{customdata[0]:.2f}%<br>% Empresas Inaptas: %{customdata[1]:.2f}%',
                    customdata=df_municipios[['% Empresas Ativas', '% Empresas Inaptas', 'Empresas Ativas', 'Empresas Inaptas', 'Total de Empresas']].values)

    return fig.to_html(full_html=False)

def grafico_2(df):
    # Filtrando o DataFrame df para empresas atendidas (foi_atendido igual a 1)
    df_atendidas = df[df['foi_atendido'] == 'Sim']

    # Filtrando o DataFrame df para empresas não atendidas (foi_atendido igual a 0)
    df_nao_atendidas = df[df['foi_atendido'] == 'Não']

    # Agrupando e contar a quantidade de empresas atendidas por município
    df_municipios_atendidas = df_atendidas['municipio'].value_counts().reset_index()
    df_municipios_atendidas.columns = ['Município', 'Empresas Atendidas']

    # Agrupando e contar a quantidade de empresas inaptas por município
    df_municipios_nao_atendidas = df_nao_atendidas['municipio'].value_counts().reset_index()
    df_municipios_nao_atendidas.columns = ['Município', 'Empresas Não Atendidas']

    # Mesclando os DataFrames de empresas atendidas e não atendidas por município
    df_municipios = df_municipios_atendidas.merge(df_municipios_nao_atendidas, on='Município', how='outer').fillna(0)
    df_municipios['Total de Empresas'] = df_municipios['Empresas Atendidas'] + df_municipios['Empresas Não Atendidas']

    # Calculando as porcentagens de empresas atendidas e não atendidas
    df_municipios['% Empresas Atendidas'] = (df_municipios['Empresas Atendidas'] / (df_municipios['Empresas Não Atendidas'] + df_municipios['Empresas Atendidas'])) * 100
    df_municipios['% Empresas Não Atendidas'] = (df_municipios['Empresas Não Atendidas'] / (df_municipios['Empresas Não Atendidas'] + df_municipios['Empresas Atendidas'])) * 100


    # Cores personalizadas para empresas atendidas e não atendidas
    cores = ['#005eb8', '#ffabab']

    # Criando um gráfico de barras empilhadas interativo com Plotly Express
    fig = px.bar(df_municipios, x='Município', y=['% Empresas Atendidas', '% Empresas Não Atendidas'],
                labels={'Município': 'Município', 'value': 'Percentual de Empresas'},
                title='Percentual de Empresas Atendidas e Não atendidas por Município',
                color_discrete_sequence=cores)

    # Atualizando o layout para tornar o gráfico mais legível
    fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='#f9f9f9', paper_bgcolor='#f9f9f9', font=dict(color="#000000"))

    # Adicionando rótulos de texto personalizados
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside')

    fig.update_traces(hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Atendidas: %{customdata[2]}<br>Empresas Não Atendidas: %{customdata[3]}<br>% Empresas Atendidas: %{customdata[0]:.2f}%<br>% Empresas Não Atendidas: %{customdata[1]:.2f}%',
                    customdata=df_municipios[['% Empresas Atendidas', '% Empresas Não Atendidas', 'Empresas Atendidas', 'Empresas Não Atendidas', 'Total de Empresas']].values)

    # Exibindo o gráfico interativo
    return fig.to_html(full_html=False)

def grafico_3(df, situacao_cadastral_selecionada):
    
    titulo = 'Percentual de Empresas Ativas Atendidas e Não atendidas por Município'
            # Cores personalizadas para empresas atendidas e não atendidas ATIVAS
    cores = ['#84f4bc', '#ffed69'] if situacao_cadastral_selecionada == 'Ativa' else ['#ffb380', '#f4455a']

    # Filtrando o DataFrame para o município atual
    df_situacao = df[df['situacao_cadastral'] == situacao_cadastral_selecionada]
    # Filtrar o DataFrame df para empresas atendidas (foi_atendido igual a 1)
    df_atendidas = df_situacao[df_situacao['foi_atendido'] == 'Sim']
    # Filtrar o DataFrame df para empresas não atendidas (foi_atendido igual a 0)
    df_nao_atendidas = df_situacao[df_situacao['foi_atendido'] == 'Não']
    # Agrupar e contar a quantidade de empresas atendidas por município
    df_municipios_atendidas = df_atendidas['municipio'].value_counts().reset_index()
    df_municipios_atendidas.columns = ['Município', 'Empresas Atendidas']
    # Agrupar e contar a quantidade de empresas inaptas por município
    df_municipios_nao_atendidas = df_nao_atendidas['municipio'].value_counts().reset_index()
    df_municipios_nao_atendidas.columns = ['Município', 'Empresas Não Atendidas']
    # Mesclar os DataFrames de empresas atendidas e não atendidas por município
    df_municipios = df_municipios_atendidas.merge(df_municipios_nao_atendidas, on='Município', how='outer').fillna(0)
    df_municipios['Total de Empresas'] = df_municipios['Empresas Atendidas'] + df_municipios['Empresas Não Atendidas']
    
    # Calcular as porcentagens de empresas atendidas e não atendidas
    df_municipios['% Empresas Atendidas'] = (df_municipios['Empresas Atendidas'] / (df_municipios['Empresas Não Atendidas'] + df_municipios['Empresas Atendidas'])) * 100
    df_municipios['% Empresas Não Atendidas'] = (df_municipios['Empresas Não Atendidas'] / (df_municipios['Empresas Não Atendidas'] + df_municipios['Empresas Atendidas'])) * 100
    # Criar um gráfico de barras empilhadas interativo com Plotly Express
    fig = px.bar(df_municipios, x='Município', y=['% Empresas Atendidas', '% Empresas Não Atendidas'],
                labels={'Município': 'Município', 'value': 'Percentual de Empresas'},
                title=titulo,
                color_discrete_sequence=cores)
    # Atualizar o layout para tornar o gráfico mais legível
    fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='#f9f9f9', paper_bgcolor='#f9f9f9', font=dict(color="#000000"))
    # Adicionar rótulos de texto personalizados
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside', 
                    hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Atendidas: %{customdata[2]}<br>Empresas Não Atendidas: %{customdata[3]}<br>% Empresas Atendidas: %{customdata[0]:.2f}%<br>% Empresas Não Atendidas: %{customdata[1]:.2f}%',
                    customdata=df_municipios[['% Empresas Atendidas', '% Empresas Não Atendidas', 'Empresas Atendidas', 'Empresas Não Atendidas', 'Total de Empresas']].values)
    
    # Exibir o gráfico interativo
    return fig.to_html(full_html=False)
def grafico_4(df, municipio):

    # Dicionário de cores para a coluna foi_atendido
    cores = {'Não': '#ffabab', 'Sim': '#e4f998'}
    
    # Filtrando o DataFrame para o município atual
    df_municipio = df[df['municipio'] == municipio]
    # Criando um DataFrame para contar a quantidade de empresas por CNAE e situação cadastral
    df_categ = df_municipio.groupby(['ds_cnae', 'foi_atendido'])['cnpj_completo'].count().reset_index()
    df_categ.rename(columns={'cnpj_completo': 'Quantidade de Empresas'}, inplace=True)
    # Adicionando a quantidade total de empresas por CNAE
    df_total_por_cnae = df_categ.groupby('ds_cnae')['Quantidade de Empresas'].sum().reset_index()
    df_total_por_cnae.rename(columns={'Quantidade de Empresas': 'Total por CNAE'}, inplace=True)
    df_categ = df_categ.merge(df_total_por_cnae, on='ds_cnae')
    # Calculando os percentuais
    df_categ['% do Total'] = (df_categ['Quantidade de Empresas'] / df_categ['Total por CNAE']) * 100
    # Criando o gráfico de barras empilhadas
    data = []
    for atendido, color in cores.items():
        df_filtrado = df_categ[df_categ['foi_atendido'] == atendido]
        trace = go.Bar(x=df_filtrado['ds_cnae'], y=df_filtrado['Quantidade de Empresas'],
                    text=df_filtrado['% do Total'].round(2).astype(str) + '%',
                    name=f'Empresas {"" if atendido == "Sim" else "Não "}Atendidas',
                    marker=dict(color=color),
                    hoverinfo='text',
                    hovertext=df_filtrado.apply(lambda row: f'CNAE: {row["ds_cnae"]}<br>Total de Empresas: {row["Total por CNAE"]}<br>' +
                                                    f'Empresas {"Atendidas" if atendido == 1 else "Não Atendidas"}: {row["Quantidade de Empresas"]}<br>' +
                                                    f'% Empresas {"Atendidas" if atendido == 1 else "Não Atendidas"}: {row["% do Total"]:.2f}%', axis=1))
        data.append(trace)
    layout = go.Layout(title=f'Segregação de Empresas Atendidas e Não Atendidas por CNAE em {municipio}',
                    xaxis=dict(title='CNAE'),
                    yaxis=dict(title='Nº de Empresas'),
                    barmode='stack',
                    plot_bgcolor='#f9f9f9', 
                    paper_bgcolor='#f9f9f9', 
                    font=dict(color="#000000"),
                    height=800)  # Definindo width e height
    fig = go.Figure(data=data, layout=layout)
    fig.update_xaxes(categoryorder='total descending')
    
    # Definindo o texto no hover
    fig.update_traces(textposition='outside')
    return fig.to_html(full_html=False)

def preparar_variaveis_comuns():
    return {
        'municipios': sorted(df['municipio'].unique().tolist()),
        'situacao_cadastral_opcoes': sorted(df['situacao_cadastral'].unique().tolist()),
        'foi_atendido_opcoes': sorted(df['foi_atendido'].unique().tolist()),
        'porte_empresa_opcoes': sorted(df['porte_empresa'].unique().tolist()),
        'opcao_mei_opcoes': sorted(df['opcao_mei'].unique().tolist()),
        'cnae_opcoes': sorted(df['ds_cnae'].unique().tolist())
    }

### Gerando APP

@app.route('/')
def relatorio():
    variaveis_comuns = preparar_variaveis_comuns()
    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df, situacao_cadastral_selecionada='Ativa')
    
    # Escolha um município padrão ou o primeiro da lista para exibir inicialmente
    municipio_padrao = df['municipio'].unique()[0]
    grafico4_html = grafico_4(df, municipio_padrao)
    
    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html,
                           grafico2_html=grafico2_html,
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html,
                           mapa_html=None,
                           **variaveis_comuns)

@app.route('/segregacao-cnae', methods=['GET', 'POST'])
def grafico_municipio():
    variaveis_comuns = preparar_variaveis_comuns()
    
    if request.method == 'POST':
        municipio_selecionado = request.form.get('municipio')
        grafico4_html = grafico_4(df, municipio_selecionado)
    else:
        municipio_padrao = df['municipio'].unique()[0]
        grafico4_html = grafico_4(df, municipio_padrao)

    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df, situacao_cadastral_selecionada='Ativa')
    
    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html, 
                           grafico2_html=grafico2_html, 
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html,
                           mapa_html=None,
                           **variaveis_comuns)

@app.route('/grafico-situacao-cadastral', methods=['POST'])
def grafico_situacao_cadastral():
    variaveis_comuns = preparar_variaveis_comuns()
    situacao_cadastral_selecionada = request.form.get('situacao_cadastral')

    # Gerar todos os gráficos e o mapa novamente
    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df, situacao_cadastral_selecionada)

     # Escolha um município padrão ou o primeiro da lista para exibir inicialmente
    municipio_padrao = df['municipio'].unique()[0]
    grafico4_html = grafico_4(df, municipio_padrao)
 
    return render_template('relatorio.html', 
                          grafico1_html=grafico1_html, 
                          grafico2_html=grafico2_html, 
                          grafico3_html=grafico3_html,
                          grafico4_html=grafico4_html, 
                          mapa_html=None,
                          **variaveis_comuns)

@app.route('/mapa', methods=['GET', 'POST'])
def index():
    variaveis_comuns = preparar_variaveis_comuns()

    # Geração dos primeiros 3 gráficos
    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df, situacao_cadastral_selecionada='Ativa')

    # Gráfico 4 e Mapa - Inicialização
    municipio_padrao = df['municipio'].unique()[0]
    grafico4_html = grafico_4(df, municipio_padrao)
    mapa_html = None  # Inicializar o mapa como None ou com um mapa padrão
    mostrar_modal = False
    if request.method == 'POST':
        # Atualiza o mapa com base nas seleções de filtros
        situacao_cadastral = request.form.getlist('situacao_cadastral')
        foi_atendido = request.form.getlist('foi_atendido')
        porte_empresa = request.form.getlist('porte_empresa')
        opcao_mei = request.form.getlist('opcao_mei')
        cnae = request.form.getlist('cnae')
        municipio = request.form.getlist('municipio')

        if all([situacao_cadastral, foi_atendido, porte_empresa, opcao_mei, municipio, cnae]):
            df_filtrado = df[(df['situacao_cadastral'].isin(situacao_cadastral)) & 
                             (df['foi_atendido'].isin(foi_atendido)) & 
                             (df['municipio'].isin(municipio)) & 
                             (df['porte_empresa'].isin(porte_empresa)) & 
                             (df['opcao_mei'].isin(opcao_mei)) &
                             (df['ds_cnae'].isin(cnae))]

            mapa = folium.Map(location=[-18.5122, -44.5550], zoom_start=7)
            for _, empresa in df_filtrado.iterrows():
                popup_text=f"CNPJ: {empresa['cnpj_completo']}<br><br>" \
                     f"Razão Social: {empresa['razao_social']}<br><br>" \
                     f"Nome Fantasia: {empresa['nome_fantasia']}<br><br>" \
                     f"Empresa atendida? {empresa['foi_atendido']}<br><br>" \
                     f"Quantidade de atendimentos: {empresa['quantidade_atendimentos']}<br><br>"\
                     f"Código CNAE: {empresa['cnae_fiscal_principal']}<br><br>" \
                     f"Descrição CNAE: {empresa['ds_cnae']}<br><br>" \
                     f"Porte: {empresa['porte_empresa']}<br><br>" \
                     f"Opção pelo MEI: {empresa['opcao_mei']}<br><br>" \
                     f"Opção pelo Simples: {empresa['opcao_simples']}<br><br>" \
                     f"Matriz ou Filial: {empresa['identificador_matriz_filial']}<br><br>" \
                     f"Data de Início de Atividade: {empresa['data_inicio_atividade']}<br><br>" \
                     f"Endereço: {empresa['endereco_completo']}<br><br>"
                folium.Marker(
                    location=[empresa['latitude'], empresa['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(icon='briefcase', color='black')
                ).add_to(mapa)
            mapa_html = mapa._repr_html_()
            mostrar_modal = not all([situacao_cadastral, foi_atendido, porte_empresa, opcao_mei, municipio, cnae])
        else:
            # Se não, exibe mensagem de erro
            mostrar_modal = True
    else:
        mapa_html = None

    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html, 
                           grafico2_html=grafico2_html, 
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html, 
                           mapa_html=mapa_html,
                           mostrar_modal=mostrar_modal,
                           **variaveis_comuns
                           )

if __name__ == '__main__':
    app.run(debug=True)

