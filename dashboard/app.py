# -*- coding: utf-8 -*-
"""Dashboard interactif AfriMarket — Streamlit + Plotly."""
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="AfriMarket — Dashboard", page_icon="📊", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "df_features.csv")
COLORS = ["#2C5F8A", "#E07A3E", "#4C9F70", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C8C"]

TAUX_MARGE = {"Électronique": 0.15, "Mode": 0.45, "Beauté": 0.50, "Maison": 0.35}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date_commande"], encoding="utf-8")
    return df


df = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTRES
# ----------------------------------------------------------------------------
st.sidebar.title("AfriMarket")
st.sidebar.caption("Dashboard interactif — analyse strategique")
st.sidebar.markdown("---")

date_min, date_max = df["date_commande"].min(), df["date_commande"].max()
date_range = st.sidebar.date_input(
    "Periode", value=(date_min.date(), date_max.date()),
    min_value=date_min.date(), max_value=date_max.date(),
)

villes = st.sidebar.multiselect("Ville", sorted(df["ville"].unique()), default=sorted(df["ville"].unique()))
categories = st.sidebar.multiselect("Categorie", sorted(df["categorie"].unique()), default=sorted(df["categorie"].unique()))
canaux = st.sidebar.multiselect("Canal marketing", sorted(df["canal_marketing"].unique()), default=sorted(df["canal_marketing"].unique()))
statuts = st.sidebar.multiselect("Statut commande", sorted(df["statut_commande"].unique()), default=sorted(df["statut_commande"].unique()))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = date_min.date(), date_max.date()

mask = (
    (df["date_commande"].dt.date >= start)
    & (df["date_commande"].dt.date <= end)
    & (df["ville"].isin(villes))
    & (df["categorie"].isin(categories))
    & (df["canal_marketing"].isin(canaux))
    & (df["statut_commande"].isin(statuts))
)
dff = df[mask].copy()
dff_valid = dff[dff["statut_commande"] != "Annulée"].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Commandes filtrees", f"{len(dff):,}")

# ----------------------------------------------------------------------------
# HEADER + KPIs
# ----------------------------------------------------------------------------
st.title("📊 AfriMarket — Analyse strategique e-commerce")
st.caption("Juillet 2025 – Decembre 2025 · Donnees nettoyees et enrichies (df_features)")

if dff.empty:
    st.warning("Aucune donnee ne correspond aux filtres selectionnes.")
    st.stop()

ca_total = dff_valid["chiffre_affaires"].sum()
profit_total = dff_valid["profit_net"].sum()
panier_moyen = dff_valid["chiffre_affaires"].mean() if len(dff_valid) else 0
taux_annulation = (dff["statut_commande"] == "Annulée").mean() * 100
taux_retour = (dff["statut_commande"] == "Retournée").mean() * 100
nb_clients = dff["id_client"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("CA total", f"{ca_total/1000:,.0f}k $")
k2.metric("Profit net estime", f"{profit_total/1000:,.0f}k $")
k3.metric("Panier moyen", f"{panier_moyen:,.0f} $")
k4.metric("Taux d'annulation", f"{taux_annulation:.1f} %")
k5.metric("Taux de retour", f"{taux_retour:.1f} %")
k6.metric("Clients actifs", f"{nb_clients:,}")

st.markdown("---")

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab_overview, tab_cat, tab_geo, tab_mkt, tab_clients, tab_reco = st.tabs(
    ["Vue d'ensemble", "Categories", "Geographie", "Marketing", "Clients", "Recommandations"]
)

# --- VUE D'ENSEMBLE ---
with tab_overview:
    st.subheader("Evolution mensuelle du chiffre d'affaires")
    evo = dff_valid.groupby("mois")["chiffre_affaires"].sum().reset_index()
    fig = px.line(evo, x="mois", y="chiffre_affaires", markers=True,
                  labels={"chiffre_affaires": "CA ($)", "mois": "Mois"},
                  color_discrete_sequence=[COLORS[0]])
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("CA par categorie")
        cat_ca = dff_valid.groupby("categorie")["chiffre_affaires"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat_ca, x="categorie", y="chiffre_affaires", color="categorie",
                     color_discrete_sequence=COLORS, labels={"chiffre_affaires": "CA ($)", "categorie": ""})
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.subheader("CA par ville")
        ville_ca = dff_valid.groupby("ville")["chiffre_affaires"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(ville_ca, x="ville", y="chiffre_affaires", color="ville",
                     color_discrete_sequence=COLORS, labels={"chiffre_affaires": "CA ($)", "ville": ""})
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Repartition statut des commandes")
    statut_counts = dff["statut_commande"].value_counts().reset_index()
    statut_counts.columns = ["statut_commande", "count"]
    fig = px.pie(statut_counts, names="statut_commande", values="count", color_discrete_sequence=COLORS, hole=0.4)
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width='stretch')

# --- CATEGORIES ---
with tab_cat:
    st.subheader("Performance par categorie")
    cat_stats = dff_valid.groupby("categorie").agg(
        CA=("chiffre_affaires", "sum"), Marge=("marge_brute", "sum"),
        Profit=("profit_net", "sum"), Commandes=("id_commande", "count"),
    ).round(2)
    cat_stats["CA_%"] = (cat_stats["CA"] / cat_stats["CA"].sum() * 100).round(1)
    cat_stats["Taux_retour_%"] = (dff.groupby("categorie")["indicateur_retour"].mean() * 100).round(2)
    st.dataframe(cat_stats.sort_values("CA", ascending=False), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Marge brute vs profit net")
        m = cat_stats.reset_index().melt(id_vars="categorie", value_vars=["Marge", "Profit"], var_name="type", value_name="montant")
        fig = px.bar(m, x="categorie", y="montant", color="type", barmode="group",
                     color_discrete_sequence=[COLORS[0], COLORS[1]], labels={"montant": "$", "categorie": ""})
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.subheader("Taux de retour par categorie")
        rc = cat_stats["Taux_retour_%"].sort_values(ascending=False).reset_index()
        fig = px.bar(rc, x="categorie", y="Taux_retour_%", color="categorie",
                     color_discrete_sequence=COLORS, labels={"categorie": "", "Taux_retour_%": "Taux de retour (%)"})
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Evolution mensuelle du CA par categorie")
    evo_cat = dff_valid.groupby(["mois", "categorie"])["chiffre_affaires"].sum().reset_index()
    fig = px.line(evo_cat, x="mois", y="chiffre_affaires", color="categorie", markers=True,
                  color_discrete_sequence=COLORS, labels={"chiffre_affaires": "CA ($)", "mois": "Mois"})
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width='stretch')

    st.info("💡 **Insight** : Électronique domine le CA mais cumule marge la plus faible et taux de "
            "retour le plus eleve — categorie a optimiser en priorite. Mode et Beaute offrent la "
            "meilleure rentabilite marginale pour la croissance.")

# --- GEOGRAPHIE ---
with tab_geo:
    st.subheader("Performance par ville")
    ville_stats = dff_valid.groupby("ville").agg(
        CA=("chiffre_affaires", "sum"), Profit=("profit_net", "sum"), Commandes=("id_commande", "count"),
    ).round(2)
    ville_stats["Taux_annulation_%"] = (dff.groupby("ville")["indicateur_annulation"].mean() * 100).round(2)
    st.dataframe(ville_stats.sort_values("CA", ascending=False), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Taux d'annulation par ville")
        av = ville_stats["Taux_annulation_%"].sort_values(ascending=False).reset_index()
        fig = px.bar(av, x="ville", y="Taux_annulation_%", color="ville",
                     color_discrete_sequence=COLORS, labels={"ville": "", "Taux_annulation_%": "Taux d'annulation (%)"})
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.subheader("Repartition du CA (categorie x ville)")
        tree_data = dff_valid.groupby(["categorie", "ville"])["chiffre_affaires"].sum().reset_index()
        fig = px.treemap(tree_data, path=["categorie", "ville"], values="chiffre_affaires",
                          color="chiffre_affaires", color_continuous_scale="Blues")
        st.plotly_chart(fig, width='stretch')

    st.subheader("Heatmap du CA mensuel par ville")
    heat = dff_valid.groupby(["ville", "mois"])["chiffre_affaires"].sum().reset_index()
    fig = px.density_heatmap(heat, x="mois", y="ville", z="chiffre_affaires", color_continuous_scale="YlOrRd",
                              labels={"chiffre_affaires": "CA ($)"})
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width='stretch')

    st.info("💡 **Insight** : Douala affiche la plus forte croissance mais aussi le plus fort taux "
            "d'annulation (~13%) — un probleme operationnel local est probablement a resoudre avant "
            "d'y augmenter l'investissement.")

# --- MARKETING ---
with tab_mkt:
    st.subheader("Performance par canal marketing")
    mkt_stats = dff_valid.groupby("canal_marketing").agg(
        CA=("chiffre_affaires", "sum"), Cout_marketing=("cout_marketing", "sum"), Commandes=("id_commande", "count"),
    ).round(2)
    mkt_stats["ROI"] = ((mkt_stats["CA"] - mkt_stats["Cout_marketing"]) / mkt_stats["Cout_marketing"]).round(2)
    client_canal = dff.groupby(["id_client", "canal_marketing"])["id_commande"].count().reset_index()
    retention = client_canal.groupby("canal_marketing")["id_commande"].apply(lambda x: (x > 1).mean() * 100).round(2)
    mkt_stats["Retention_%"] = retention
    st.dataframe(mkt_stats.sort_values("ROI", ascending=False), width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ROI par canal")
        roi = mkt_stats["ROI"].sort_values(ascending=False).reset_index()
        fig = px.bar(roi, x="canal_marketing", y="ROI", color="canal_marketing",
                     color_discrete_sequence=COLORS, labels={"canal_marketing": ""})
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.subheader("CA genere vs cout marketing")
        m = mkt_stats.reset_index().melt(id_vars="canal_marketing", value_vars=["CA", "Cout_marketing"], var_name="type", value_name="montant")
        fig = px.bar(m, x="canal_marketing", y="montant", color="type", barmode="group",
                     color_discrete_sequence=[COLORS[0], COLORS[3]], labels={"canal_marketing": "", "montant": "$"})
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width='stretch')

    st.info("💡 **Insight** : Email a le meilleur ROI mais le plus petit budget — a scaler en priorite. "
            "Influenceur cumule le ROI et la retention les plus faibles — candidat a la reduction budgetaire.")

# --- CLIENTS ---
with tab_clients:
    nb_clients_total = dff["id_client"].nunique()
    commandes_par_client = dff.groupby("id_client")["id_commande"].count()
    pct_recurrents = (commandes_par_client > 1).mean() * 100

    c1, c2 = st.columns(2)
    c1.metric("Nombre de clients", f"{nb_clients_total:,}")
    c2.metric("% clients recurrents", f"{pct_recurrents:.1f} %")

    st.subheader("Courbe de Pareto — concentration du CA par client")
    clv = dff_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False).reset_index(drop=True)
    if len(clv):
        clv_cum_pct = clv.cumsum() / clv.sum() * 100
        pct_clients = np.arange(1, len(clv) + 1) / len(clv) * 100
        pareto_df = pd.DataFrame({"pct_clients": pct_clients, "pct_ca_cumule": clv_cum_pct.values})
        fig = px.line(pareto_df, x="pct_clients", y="pct_ca_cumule",
                      labels={"pct_clients": "% des clients", "pct_ca_cumule": "% du CA cumule"},
                      color_discrete_sequence=[COLORS[0]])
        fig.add_hline(y=80, line_dash="dash", line_color=COLORS[3])
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Segmentation par frequence d'achat")
        def segment(n):
            if n == 1: return "Nouveau (1 commande)"
            elif n <= 5: return "Occasionnel (2-5)"
            else: return "Fidele (6+)"
        seg = commandes_par_client.apply(segment).value_counts().reset_index()
        seg.columns = ["segment", "count"]
        fig = px.pie(seg, names="segment", values="count", color_discrete_sequence=COLORS, hole=0.4)
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width='stretch')
    with c2:
        st.subheader("Top 10 clients (CA cumule)")
        top10 = dff_valid.groupby("id_client")["chiffre_affaires"].sum().sort_values(ascending=False).head(10).reset_index()
        top10.columns = ["id_client", "CA"]
        fig = px.bar(top10, x="id_client", y="CA", color="CA", color_continuous_scale="Blues")
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width='stretch')

    st.info("💡 **Insight** : 32% des clients generent 80% du CA. Le segment 'nouveaux clients' "
            "(1 seule commande) est le plus grand levier de retention a activer.")

# --- RECOMMANDATIONS ---
with tab_reco:
    st.subheader("5 recommandations strategiques")
    st.markdown("""
    1. **Reduire le taux de retour sur l'Électronique** (13.8%) — audit qualite produit/fournisseur.
    2. **Corriger le probleme operationnel a Douala** avant d'augmenter l'investissement (taux d'annulation 12.9%).
    3. **Reallouer le budget marketing** : renforcer Email (ROI 231x), reduire Influenceur (ROI 21.6x).
    4. **Reactiver les clients a commande unique** (26% de la base) via campagne Email ciblee sur Mode/Beaute.
    5. **Prioriser la croissance sur Mode et Beaute** (marges 45-50%, faible taux de retour) plutot que sur l'Electronique.
    """)
    st.subheader("Conclusion business")
    st.markdown("""
    AfriMarket degage un CA solide mais une rentabilite bridee par sa dependance a l'Électronique.
    La priorite immediate est de **proteger le profit net** (retours electronique, operations a Douala,
    reallocation marketing) tout en activant un levier de croissance rentable : la reactivation
    de la base clients existante, deja fidele a 74%.
    """)

st.markdown("---")
with st.expander("🔎 Donnees detaillees (filtrees)"):
    st.dataframe(dff, width='stretch')
    st.download_button("Telecharger les donnees filtrees (CSV)", dff.to_csv(index=False).encode("utf-8"),
                        "afrimarket_filtre.csv", "text/csv")
