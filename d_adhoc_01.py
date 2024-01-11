import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.offline as py
import folium
from folium import Figure
from branca.element import Figure
from IPython.display import HTML
import plotly.graph_objs as go
import requests
import io
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

url = 'https://github.com/marcilioduarte/work-sebraemg-public/raw/main/data/empresas_ariel_3.xlsx'

df = pd.read_excel(url, engine='openpyxl')

def grafico_1(df):
    # Filtrando o DataFrame df para empresas ativas (situacao_cadastral igual a 2)
    df_ativas = df[df['situacao_cadastral'] == 2]

    # Filtrando o DataFrame df para empresas inaptas (situacao_cadastral igual a 4)
    df_inaptas = df[df['situacao_cadastral'] == 4]

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
    fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='rgba(0,0,0,0)')

    # Adicionar rótulos de texto personalizados
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside')

    # Atualizar o hovertemplate para incluir o número total de empresas
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Ativas: %{customdata[2]}<br>Empresas Inaptas: %{customdata[3]}<br>% Empresas Ativas: %{customdata[0]:.2f}%<br>% Empresas Inaptas: %{customdata[1]:.2f}%',
                    customdata=df_municipios[['% Empresas Ativas', '% Empresas Inaptas', 'Empresas Ativas', 'Empresas Inaptas', 'Total de Empresas']].values)

    return fig.to_html(full_html=False)

def grafico_2(df):
    # Filtrando o DataFrame df para empresas atendidas (foi_atendido igual a 1)
    df_atendidas = df[df['foi_atendido'] == 1]

    # Filtrando o DataFrame df para empresas não atendidas (foi_atendido igual a 0)
    df_nao_atendidas = df[df['foi_atendido'] == 0]

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
    fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='rgba(0,0,0,0)')

    # Adicionando rótulos de texto personalizados
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside')

    fig.update_traces(hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Atendidas: %{customdata[2]}<br>Empresas Não Atendidas: %{customdata[3]}<br>% Empresas Atendidas: %{customdata[0]:.2f}%<br>% Empresas Não Atendidas: %{customdata[1]:.2f}%',
                    customdata=df_municipios[['% Empresas Atendidas', '% Empresas Não Atendidas', 'Empresas Atendidas', 'Empresas Não Atendidas', 'Total de Empresas']].values)

    # Exibindo o gráfico interativo
    return fig.to_html(full_html=False)

def grafico_3(df):
    # Lista de municípios
    situacao_cadastral = [2, 4]

    # Loop para criar um gráfico para cada município
    for situacao in situacao_cadastral:
        if situacao == 2:
            titulo = 'Percentual de Empresas Ativas Atendidas e Não atendidas por Município'
            # Cores personalizadas para empresas atendidas e não atendidas ATIVAS
            cores = ['#84f4bc', '#ffed69']
        elif situacao == 4:
            titulo = 'Percentual de Empresas Inaptas Atendidas e Não atendidas por Município'
            # Cores personalizadas para empresas atendidas e não atendidas ATIVAS
            cores = ['#ffb380', '#f4455a']

        # Filtrando o DataFrame para o município atual
        df_situacao = df[df['situacao_cadastral'] == situacao]
        # Filtrar o DataFrame df para empresas atendidas (foi_atendido igual a 1)
        df_atendidas = df_situacao[df_situacao['foi_atendido'] == 1]

        # Filtrar o DataFrame df para empresas não atendidas (foi_atendido igual a 0)
        df_nao_atendidas = df_situacao[df_situacao['foi_atendido'] == 0]

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
        fig.update_layout(xaxis_title=None, yaxis_title='Percentual de Empresas', plot_bgcolor='rgba(0,0,0,0)')

        # Adicionar rótulos de texto personalizados
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside', 
                        hovertemplate='<b>%{x}</b><br>Total de Empresas: %{customdata[4]}<br>Empresas Atendidas: %{customdata[2]}<br>Empresas Não Atendidas: %{customdata[3]}<br>% Empresas Atendidas: %{customdata[0]:.2f}%<br>% Empresas Não Atendidas: %{customdata[1]:.2f}%',
                        customdata=df_municipios[['% Empresas Atendidas', '% Empresas Não Atendidas', 'Empresas Atendidas', 'Empresas Não Atendidas', 'Total de Empresas']].values)
        
        # Exibir o gráfico interativo
        return fig.to_html(full_html=False)

def grafico_4(df, municipio):

    # Dicionário de cores para a coluna foi_atendido
    cores = {0: '#ffabab', 1: '#e4f998'}
    
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
                    name=f'Empresas {"" if atendido == 1 else "Não "}Atendidas',
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
                    plot_bgcolor='rgba(0,0,0,0)',
                    width=1200, height=800)  # Definindo width e height
    fig = go.Figure(data=data, layout=layout)
    fig.update_xaxes(categoryorder='total descending')
    
    # Definindo o texto no hover
    fig.update_traces(textposition='outside')
    return fig.to_html(full_html=False)



    
### Gerando APP

@app.route('/')
def relatorio():
    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df)
    
    # Escolha um município padrão ou o primeiro da lista para exibir inicialmente
    municipio_padrao = df['municipio'].unique()[0]
    grafico4_html = grafico_4(df, municipio_padrao)
    
    municipios = df['municipio'].unique().tolist()
    situacao_cadastral_opcoes = df['situacao_cadastral'].unique().tolist()
    foi_atendido_opcoes = df['foi_atendido'].unique().tolist()
    porte_empresa_opcoes = df['porte_empresa'].unique().tolist()
    opcao_mei_opcoes = df['opcao_mei'].unique().tolist()
    cnae_opcoes = df['ds_cnae'].unique().tolist()
    
    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html, 
                           grafico2_html=grafico2_html, 
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html, 
                           municipios=municipios,
                           situacao_cadastral=situacao_cadastral_opcoes,
                           foi_atendido=foi_atendido_opcoes,
                           porte_empresa=porte_empresa_opcoes,
                           opcao_mei=opcao_mei_opcoes,
                           cnae=cnae_opcoes)

@app.route('/segregacao-cnae', methods=['GET', 'POST'])
def grafico_municipio():
    municipios = df['municipio'].unique().tolist()
    situacao_cadastral_opcoes = df['situacao_cadastral'].unique().tolist()
    foi_atendido_opcoes = df['foi_atendido'].unique().tolist()
    porte_empresa_opcoes = df['porte_empresa'].unique().tolist()
    opcao_mei_opcoes = df['opcao_mei'].unique().tolist()
    cnae_opcoes = df['ds_cnae'].unique().tolist()
    
    if request.method == 'POST':
        municipio_selecionado = request.form.get('municipio')
        grafico4_html = grafico_4(df, municipio_selecionado)
    else:
        municipio_padrao = df['municipio'].unique()[0]
        grafico4_html = grafico_4(df, municipio_padrao)

    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df)
    
    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html, 
                           grafico2_html=grafico2_html, 
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html, 
                           municipios=municipios,
                           situacao_cadastral=situacao_cadastral_opcoes,
                           foi_atendido=foi_atendido_opcoes,
                           porte_empresa=porte_empresa_opcoes,
                           opcao_mei=opcao_mei_opcoes,
                           cnae=cnae_opcoes)

@app.route('/mapa', methods=['GET', 'POST'])
def index():
    # Inicialize variáveis comuns
    municipios = df['municipio'].unique().tolist()
    situacao_cadastral_opcoes = df['situacao_cadastral'].unique().tolist()
    foi_atendido_opcoes = df['foi_atendido'].unique().tolist()
    porte_empresa_opcoes = df['porte_empresa'].unique().tolist()
    opcao_mei_opcoes = df['opcao_mei'].unique().tolist()
    cnae_opcoes = df['ds_cnae'].unique().tolist()

    # Geração dos primeiros 3 gráficos
    grafico1_html = grafico_1(df)
    grafico2_html = grafico_2(df)
    grafico3_html = grafico_3(df)

    # Gráfico 4 e Mapa - Inicialização
    municipio_padrao = municipios[0]
    grafico4_html = grafico_4(df, municipio_padrao)
    mapa_html = None  # Inicializar o mapa como None ou com um mapa padrão

    if request.method == 'POST':
        # Atualiza o mapa com base nas seleções de filtros
        situacao_cadastral = request.form.get('situacao_cadastral')
        foi_atendido = request.form.get('foi_atendido')
        porte_empresa = request.form.get('porte_empresa')
        opcao_mei = request.form.get('opcao_mei')
        cnae = request.form.get('cnae')
        municipio = request.form.get('municipio')

        if all([situacao_cadastral, foi_atendido, porte_empresa, opcao_mei, municipio, cnae]):
            df_filtrado = df[(df['situacao_cadastral'] == int(situacao_cadastral)) & 
                             (df['foi_atendido'] == int(foi_atendido)) & 
                             (df['municipio'] == municipio) & 
                             (df['porte_empresa'] == int(porte_empresa)) & 
                             (df['opcao_mei'] == opcao_mei) &
                             (df['ds_cnae'] == cnae)]

            mapa = folium.Map(location=[-18.5122, -44.5550], zoom_start=7)
            for _, row in df_filtrado.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"{row['razao_social']}<br>{row['endereco_completo']}"
                ).add_to(mapa)
            mapa_html = mapa._repr_html_()
        else:
            # Se não, exibe um mapa padrão
            mapa_html = None
    else:
        mapa_html = None

    return render_template('relatorio.html', 
                           grafico1_html=grafico1_html, 
                           grafico2_html=grafico2_html, 
                           grafico3_html=grafico3_html,
                           grafico4_html=grafico4_html, 
                           municipios=municipios,
                           mapa_html=mapa_html,
                           situacao_cadastral=situacao_cadastral_opcoes,
                           foi_atendido=foi_atendido_opcoes,
                           porte_empresa=porte_empresa_opcoes,
                           opcao_mei=opcao_mei_opcoes,
                           cnae=cnae_opcoes)

if __name__ == '__main__':
    app.run(debug=True)

