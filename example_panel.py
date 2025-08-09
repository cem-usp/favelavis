import panel as pn
import param
from panel.layout import Row, Column, Spacer
from panel.widgets import Button

pn.extension()

# Estado compartilhado
class AppState(param.Parameterized):
    favela = param.ObjectSelector(default="São Remo", objects=["São Remo", "Paraisópolis", "Heliópolis"])

state = AppState()


# --- Card flutuante no canto superior direito ---
card_flutuante = pn.Card(
    pn.pane.Markdown("**Ações rápidas**"),
    pn.widgets.Button(name="Atualizar"),
    pn.widgets.Button(name="Exportar"),
    title='Seila', 
    collapsed=True,
    width=200,
    header_background="#555"
)

# --- Área de conteúdo principal + card à direita ---
conteudo_com_card = pn.Row(
    pn.Column(
        pn.pane.Markdown("### Conteúdo principal aqui."),
        height=400,
        sizing_mode="stretch_width"
    ),
    pn.Spacer(width=10),
    pn.Column(
        pn.Spacer(height=10),
        card_flutuante,
        sizing_mode="fixed",
        width=220
    )
)

# Rodapé da tela principal
rodape = pn.Row(
    pn.pane.Markdown("Rodapé com informações, créditos, etc."),
    height=800,
    sizing_mode='stretch_width'
)

# Título reativo no topo (substituindo template.title)
@pn.depends(state.param.favela)
def titulo_dinamico(favela):
    return pn.Column(
        pn.pane.Markdown(f"# {favela} (2017, 2020)", sizing_mode="stretch_width"),
        # pn.pane.Markdown("Comparativo entre os anos para a análise morfológica das edificações."),
        sizing_mode="stretch_width"
    )

# --- Menu lateral com rodapé colado ---
menu_lateral_topo = pn.Column(
    pn.pane.Markdown("## Menu Lateral"),
    pn.Param(state.param, parameters=["favela"]),
    pn.widgets.Button(name="Opção 1"),
    pn.widgets.Button(name="Opção 2"),
)

menu_lateral_rodape = pn.Column(
    pn.Spacer(sizing_mode='stretch_height'),
    pn.pane.Markdown("---"),
    pn.pane.Markdown("**Créditos:**\nFernando Gomes – 2025")
)

menu_lateral = pn.Column(
    menu_lateral_topo,
    menu_lateral_rodape,
    sizing_mode='stretch_height'
)

# Template principal
template = pn.template.FastListTemplate(
    header_background="#444444",
    header_color="white",
    title='FavelaVIS',
    header=titulo_dinamico,  # <-- Usa a função dinâmica no lugar do title fixo
    sidebar=[menu_lateral],
    main=[conteudo_com_card, rodape]
)

template.servable()
