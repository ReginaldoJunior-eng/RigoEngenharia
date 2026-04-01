import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
import re
import requests

# --- FUNÇÕES AUXILIARES ---
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

# Configuração visual
st.set_page_config(page_title="Rigo Engenharia - Vistorias", layout="wide")
st.title("🏗️ Rigo Engenharia")
st.subheader("Gerador de Laudo de Vistoria Técnica")

# --- BLOCO 1: DADOS DO SOLICITANTE ---
with st.expander("Dados do Cliente e Imóvel", expanded=True):
    # Linha 1: Nome e Número do Laudo
    col_n, col_num_laudo = st.columns([3, 1])
    with col_n:
        nome = st.text_input("Nome do Solicitante")
    with col_num_laudo:
        num_laudo = st.text_input("Número do Laudo", placeholder="001")

    # Linha 2: CPF, Apartamento e Torre (Otimizado)
    col_cpf, col_apto, col_torre = st.columns(3)
    with col_cpf:
        cpf_input = st.text_input("CPF (apenas números)")
        cpf_valido = validar_cpf(cpf_input)
        if cpf_input and not cpf_valido:
            st.error("⚠️ CPF Inválido!")
    with col_apto:
        apto = st.text_input("Apartamento")
    with col_torre:
        torre = st.text_input("Torre")
    
    st.divider()
    data_vis_form = st.text_input("Data e Hora da Vistoria (ex: 10/03/2026 às 14h)")

# --- BLOCO 2: FOTOS E ENDEREÇO ---
st.divider()
st.header("📸 Registros Fotográficos")

st.write("#### 1. Foto da Fachada")
foto_capa = st.file_uploader("Upload da foto principal (Capa)", type=['jpg', 'jpeg', 'png'], key="fachada")

endereco_formatado = ""
if foto_capa:
    col_cep, col_num = st.columns([2, 1])
    with col_cep:
        cep_input = st.text_input("Digite o CEP", max_chars=9)
    with col_num:
        numero_imovel = st.text_input("Número")

    if len(cep_input.replace("-", "")) >= 8:
        dados_cep = buscar_cep(cep_input)
        if dados_cep and "erro" not in dados_cep:
            endereco_formatado = f"{dados_cep.get('logradouro')}, {numero_imovel} – {dados_cep.get('bairro')} {dados_cep.get('localidade')} - {dados_cep.get('uf')}, {dados_cep.get('cep')}"
            st.success(f"Endereço: {endereco_formatado}")

st.write("#### 2. Fotos dos Vícios")
fotos_vicios = st.file_uploader("Arraste as fotos dos vícios", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

lista_para_o_word = []
legendas_preenchidas = True

if fotos_vicios:
    for i, arq_foto in enumerate(fotos_vicios):
        col_img, col_txt = st.columns([1, 4])
        with col_img:
            st.image(arq_foto, width=110)
        with col_txt:
            legenda = st.text_input(f"Legenda da Figura {i+1}", key=f"leg_{i}")
            if not legenda:
                legendas_preenchidas = False
            lista_para_o_word.append({"foto": arq_foto, "legenda": legenda})

# --- BLOCO 3: DATA DE EMISSÃO E GERAÇÃO ---
st.divider()
st.header("📅 Emissão do Laudo")
col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
with col_d1:
    dia_laudo = st.text_input("Dia", placeholder="10")
with col_d2:
    mes_laudo_extenso = st.text_input("Mês (Extenso)", placeholder="março")
with col_d3:
    ano_laudo = st.text_input("Ano", value="2026")

st.divider()

# Validação total
campos_base = all([nome, num_laudo, cpf_valido, apto, torre, data_vis_form, dia_laudo, mes_laudo_extenso, ano_laudo, foto_capa, endereco_formatado])
pode_gerar = campos_base and fotos_vicios and legendas_preenchidas

if st.button("🚀 GERAR LAUDO COMPLETO", use_container_width=True):
    if not campos_base:
        st.warning("⚠️ Preencha todos os dados, endereço e datas.")
    elif not fotos_vicios:
        st.warning("⚠️ Você precisa enviar pelo menos uma foto de vício.")
    elif not legendas_preenchidas:
        st.warning("⚠️ Todas as fotos de vícios precisam de uma legenda.")
    else:
        try:
            nome_arquivo_modelo = "LT_RIGO_001_2026-MODELO.docx" 
            doc = DocxTemplate(nome_arquivo_modelo)
            
            fotos_preparadas = [{"foto": InlineImage(doc, item["foto"], width=Mm(110)), "legenda": item["legenda"]} for item in lista_para_o_word]
            
            dados = {
                "nome": nome,
                "cpf": cpf_input,
                "apartamento": apto,
                "torre": torre,
                "data_da_Vis": data_vis_form,
                "dia_laudo": dia_laudo,
                "mes_laudo_extenso": mes_laudo_extenso.lower(),
                "ano": ano_laudo,
                "Endereco": endereco_formatado,
                "foto_fachada": InlineImage(doc, foto_capa, width=Mm(110)),
                "registros": fotos_preparadas
            }
            
            doc.render(dados)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Nomeação solicitada: LT_NUMERO_NOME.docx
            nome_limpo = nome.strip().upper().replace(" ", "_")
            num_limpo = num_laudo.strip().upper()
            nome_final_doc = f"LT_{num_limpo}_{nome_limpo}.docx"
            
            st.success(f"✅ Laudo gerado com sucesso!")
            st.download_button(
                label=f"📥 Baixar Laudo {nome_final_doc}",
                data=buffer,
                file_name=nome_final_doc,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")