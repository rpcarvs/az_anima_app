import os

import requests
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw


@st.cache_data
def request_indexed_smiles(smiles):
    url = "https://smilesapi.politepond-2510b4f8.francecentral.azurecontainerapps.io:443/transform-smiles"
    token = os.getenv("SMILES_TOKEN", "")
    headers = {"SMILES_API_KEY": token}
    data = {"smiles": smiles}

    resp = requests.post(url, json=data, headers=headers, timeout=300)
    return resp.json().get("smiles", "")


@st.cache_data
def request_predictions(indexed_smiles):
    url = "https://animakernel.politepond-2510b4f8.francecentral.azurecontainerapps.io:443/predict"
    token = os.getenv("KERNEL_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"smiles": indexed_smiles}

    return requests.post(url, json=data, headers=headers, timeout=300).json()


@st.cache_data
def run_model(smiles):
    # get indexed smiles
    indexed_smiles = request_indexed_smiles(smiles)
    if indexed_smiles:
        return request_predictions(indexed_smiles)
    st.write("Ops! It seems you have an invalid SMILES")
    return None


def show_output(molecule):
    # getting the kernel up and predictions
    if predictions := run_model(molecule):
        li_voltage = predictions.get("voltages")
        oxidation = predictions.get("ox/red")[0]
        reduction = predictions.get("ox/red")[1]

        with st.container(border=True):
            st.write(f"**Molecule:** {molecule}")
            st.write(
                f"""**Lithium insertion potential:** 
                $${{\\color{{green}}{round(float(li_voltage), 3)}}} 
                \\textrm{{ V \\textit{{vs.}} Li/Li}}^+$$""",
            )
            st.write(
                f"**Molecule oxidation potential:** $${{\\color{{red}}{round(float(oxidation), 3)}}} \\textrm{{ V (ref to vacuum)}}$$",
            )
            st.write(
                f"**Molecule reduction potential:** $${{\\color{{blue}}{round(float(reduction), 3)}}} \\textrm{{ V (ref to vacuum)}}$$",
            )

            m = Chem.MolFromSmiles(molecule)
            fig = Draw.MolToImage(m)
            # plt.axis("off")
            st.image(fig)
