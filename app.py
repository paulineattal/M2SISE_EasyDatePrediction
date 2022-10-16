from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import gunicorn 

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='EasyDate Michael Scott Team')
server = app.server 

df = pd.read_csv("./datas/trainClean.csv")
df_2 = pd.read_csv("./datas/trainGraph.csv", sep=",")

conditions = [
    (df_2['goal'] == 1) | (df_2['goal'] == 2),
    (df_2['goal'] == 4) | (df_2['goal'] == 3),
    (df_2['goal'] == 5) | (df_2['goal'] == 6)
    ]
values = ['fun', 'serious', 'pass time']
df_2['goal_cat'] = np.select(conditions, values)
conditions = [
    (df_2['age'] > min(df_2["age"])) & (df_2['age'] <= 22),
    (df_2['age'] > 22) & (df_2['age'] <= 30),
    (df_['age'] > 30)
    ]
values = ['young', 'adult', 'old']

df_2['age_cat'] = np.select(conditions, values)
df_2["culture_interest"]=np.where(df_2['culture']>=6, 'yes_culture', 'no_culture')
df_2["indoors_interest"]=np.where(df_2['indoors']>=6, 'yes_indoors', 'no_indoors')
df_2["sport_interest"]=np.where(df_2['sport']>=6, 'yes_sport', 'no_sport')
df_2["social_interest"]=np.where(df_2['social']>=6, 'yes_social', 'no_social')
df_2["most_interest"]=df_2[["culture","indoors","sport","social"]].idxmax(axis=1)
df_2["gender"]=df_2["gender"].replace(0, "women")
df_2["gender"]=df_2["gender"].replace(1, "men")
df_men = df_2[df_2["gender"]=="men"]
df_women = df_2[df_2["gender"]=="women"]

#SideBar
TABPANEL = dbc.Container([
    html.H1("Menu"),
    html.Hr(),
    dbc.Tabs(
        [
            dbc.Tab(label="Accueil", tab_id="Accueil"),
            dbc.Tab(label="Statistique", tab_id="Statistique"),
            dbc.Tab(label="Modélisation", tab_id="Modelisation"),
            dbc.Tab(label="Prédiction", tab_id="Prediction")             
        ],
        id="tabPanel",
        active_tab="Accueil",
    )
])
        
#Contenu
PageContent = dbc.Container([

    #Accueil
    html.Div(id="Accueil-tab", children=
        html.Div(
            html.P("Accueil")
        )
    ),

    #Page Statistique
    html.Div(id="Statistique-tab", children=[
        html.Div([
            dcc.Dropdown(id="xInput", options=[{"label":name,"value":name} for name in df.columns], value="age", className="app-DivFilter--Select_value"),
            dcc.Dropdown(id="yInput", options=[{"label":name,"value":name} for name in df.columns], value="income", className="app-DivFilter--Select_value"),
            dcc.Dropdown(id="colorInput", options=[{"label":name,"value":name} for name in df.columns], value="gender", className="app-DivFilter--Select_value")], 
            className="DivFilter"
        ),
        dcc.Graph(id="GraphStat_1")
    ], className="DivTab"),

    #Page Modélisation
    html.Div(id="Modelisation-tab", children=
        html.Div(
            html.P("Modelisation")
        )
    ),

    #Page prédiction
    html.Div(id="Prediction-tab", children=
        html.Div(
            html.P("Prediction")
        )
    )
])


#Apparence
app.layout = html.Div([TABPANEL, PageContent])

@app.callback([Output("Accueil-tab", "style"), Output("Statistique-tab", "style"), Output("Modelisation-tab", "style"), Output("Prediction-tab", "style")],
              [Input("tabPanel","active_tab")])
def render_tab_content(active_tab):
    on = {"display":"block"}
    off = {"display":"none"}
    if active_tab is not None:
        if active_tab == "Accueil":
            return on, off, off, off
        elif active_tab == "Statistique":
            return off, on, off, off
        elif active_tab == "Modelisation":
            return off, off, on, off
        elif active_tab == "Prediction":
            return off, off, off, on
    return "No tab selected"


@app.callback(Output('GraphStat_1', 'figure'),
    [Input('xInput', 'value'), Input('yInput', 'value'), Input('colorInput', 'value')])
def update_graph(xInput, yInput, colorInput):
    
    dfg = df.groupby(by=[xInput,colorInput])[yInput].mean().reset_index()
    dfg[colorInput] = dfg[colorInput].astype(str)
    fig = px.bar(dfg, x=xInput,
                     y=yInput,
                     color=colorInput,
                     barmode="group")
    fig_men = px.sunburst(df_men, path=['most_interest', 'goal_cat', 'age_cat'],
                  values='income', color='income'
                 )
    fig_women = px.sunburst(df_women, path=['most_interest', 'goal_cat', 'age_cat'],
                  values='income', color='income'
                 )

    return fig, fig_men, fig_women


if __name__ == '__main__':
    app.run_server(debug=True)