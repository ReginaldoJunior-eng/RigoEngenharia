import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
import re
import requests

# --- FUNÇÃO PARA BUSCAR CEP ---
def buscar_cep(cep: str):
    cep = re.sub(r'\D', '', cep)
    if len(cep) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            return None
    return None

# --- FUNÇÃO DE VALIDAÇÃO DE CPF ---
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

# Configuração visual do formulário
st.set_page_config(page_title="Rigo Engenharia - Vistorias", layout="wide")

st.title("🏗️ Rigo Engenharia")
st.subheader("Gerador de Laudo de Recebimento de Imóvel")

# --- BLOCO 1: DADOS DO SOLICITANTE (ESTRUTURA MANTIDA) ---
with st.expander("Dados do Cliente e Imóvel", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Solicitante", value="")
        cpf_input = st.text_input("CPF (apenas números ou com pontos/traço)", value="")
        
        cpf_valido = validar_cpf(cpf_input)
        if cpf_input and not cpf_valido:
            st.error("⚠️ CPF Inválido!")
        elif cpf_input and cpf_valido:
            st.success("✅ CPF Válido")
            
    with col2:
        apto = st.text_input("Apartamento", value="")
        torre = st.text_input("Torre", value="")
    
    data_vis = st.text_input("Data e Hora da Vistoria", value="")

# --- BLOCO 2: FOTOS E ENDEREÇO DA FACHADA ---
st.divider()
st.header("📸 Registros Fotográficos")

st.write("#### 1. Foto da Fachada")
foto_capa = st.file_uploader("Upload da foto principal (Capa)", type=['jpg', 'jpeg', 'png'], key="fachada")

# LÓGICA DO ENDEREÇO VINCULADA À FOTO DA FACHADA
endereco_formatado = ""
if foto_capa:
    st.info("📍 Informe a localização da fachada:")
    col_cep, col_num = st.columns([2, 1])
    
    with col_cep:
        cep_input = st.text_input("Digite o CEP", max_chars=9, placeholder="00000-000")
    with col_num:
        numero_imovel = st.text_input("Número", placeholder="123")

    if len(cep_input.replace("-", "")) >= 8:
        dados_cep = buscar_cep(cep_input)
        if dados_cep and "erro" not in dados_cep:
            logradouro = dados_cep.get("logradouro", "")
            bairro = dados_cep.get("bairro", "")
            localidade = dados_cep.get("localidade", "")
            uf = dados_cep.get("uf", "")
            cep_limpo = dados_cep.get("cep", "")
            
            # Monta a legenda conforme seu modelo: R.da Mooca, 1678 – Mooca São Paulo - SP, 03104-000
            endereco_formatado = f"{logradouro}, {numero_imovel} – {bairro} {localidade} - {uf}, {cep_limpo}"
            st.success(f"Endereço: {endereco_formatado}")
        elif dados_cep and "erro" in dados_cep:
            st.error("CEP não encontrado. Verifique os números.")

st.write("#### 2. Fotos dos Vícios")
fotos_vicios = st.file_uploader("Arraste todas as fotos dos vícios encontrados", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

lista_para_o_word = []
if fotos_vicios:
    st.info(f"Foram carregadas {len(fotos_vicios)} fotos.")
    for i, arq_foto in enumerate(fotos_vicios):
        col_img, col_txt = st.columns([1, 4])
        with col_img:
            st.image(arq_foto, width=110)
        with col_txt:
            legenda = st.text_input(f"Legenda da Figura {i+1}", key=f"leg_{i}")
            lista_para_o_word.append({"foto": arq_foto, "legenda": legenda})

# --- BLOCO 3: GERAÇÃO DO ARQUIVO ---
st.divider()

if st.button("🚀 GERAR LAUDO COMPLETO", use_container_width=True):
    if not cpf_valido:
        st.error("Corrija o CPF antes de gerar.")
    elif not foto_capa:
        st.error("A foto da fachada é obrigatória.")
    elif not endereco_formatado:
        st.error("Por favor, preencha o CEP e o Número para a legenda da fachada.")
    else:
        try:
            nome_arquivo_modelo = "LT_RIGO_001_2026-MODELO.docx" 
            doc = DocxTemplate(nome_arquivo_modelo)
            
            fotos_preparadas = []
            for item in lista_para_o_word:
                fotos_preparadas.append({
                    "foto": InlineImage(doc, item["foto"], width=Mm(110)),
                    "legenda": item["legenda"]
                })
            
            dados = {
                "nome": nome,
                "cpf": cpf_input,
                "apartamento": apto,
                "torre": torre,
                "data_vistoria": data_vis,
                "Endereco": endereco_formatado, # Preenche a tag {{ Endereco }} que você criou
                "foto_fachada": InlineImage(doc, foto_capa, width=Mm(110)),
                "registros": fotos_preparadas
            }
            
            doc.render(dados)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success("✅ Laudo gerado!")
            st.download_button(
                label="📥 Baixar Laudo Word",
                data=buffer,
                file_name=f"Laudo_Apto_{apto}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Erro: {e}")