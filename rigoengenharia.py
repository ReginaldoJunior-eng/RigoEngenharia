import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from docx import Document
import io
import re
import requests
from pillow_heif import register_heif_opener
from PIL import Image
from datetime import datetime

# Habilita suporte a HEIC/HEIF (Fotos de iPhone)
register_heif_opener()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Rigo Engenharia - Portal", layout="wide", page_icon="🏗️")

# --- 2. FUNÇÕES AUXILIARES ---
def buscar_cep(cep: str):
    cep = re.sub(r'\D', '', cep)
    if len(cep) == 8:
        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            if response.status_code == 200: return response.json()
        except: return None
    return None

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1: return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]): return False
    return True

def formatar_cpf(cpf: str) -> str:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def processar_imagem(arquivo):
    if arquivo is None:
        return None
    ext = arquivo.name.lower()
    if ext.endswith(('.jpg', '.jpeg', '.png')):
        return arquivo
    try:
        img = Image.open(arquivo)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Erro ao processar imagem {arquivo.name}: {e}")
        return None

def remover_paginas_em_branco_fim(doc):
    """Remove parágrafos vazios ao final do documento para evitar páginas em branco."""
    for paragraph in reversed(doc.paragraphs):
        if not paragraph.text.strip():
            p = paragraph._element
            p.getparent().remove(p)
        else:
            break
    return doc

# --- 3. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main-banner {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=2070");
        background-size: cover; background-position: center; padding: 80px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;
    }
    .service-card {
        height: 350px; border-radius: 15px; background-size: cover; background-position: center; display: flex; align-items: flex-end; padding: 25px; margin-bottom: 20px; position: relative; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.3); transition: transform 0.3s ease;
    }
    .service-card:hover { transform: translateY(-10px); }
    .card-overlay {
        position: absolute; bottom: 0; left: 0; right: 0; top: 0; background: linear-gradient(transparent 40%, rgba(0,0,0,0.95) 90%); display: flex; flex-direction: column; justify-content: flex-end; padding: 25px;
    }
    .service-card h3 { color: #ffffff !important; margin-bottom: 8px; font-size: 22px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); }
    .service-card p { color: #f0f0f0 !important; font-size: 14px; line-height: 1.5; text-shadow: 1px 1px 3px rgba(0,0,0,0.8); }
    section[data-testid="stSidebar"] .stButton button { width: 100%; text-align: left; border: none; background-color: transparent; padding: 10px 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO LATERAL (SIDEBAR) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "inicio"

with st.sidebar:
    st.write("") 
    try: 
        st.image("Reng.png", use_container_width=True)
    except: 
        st.markdown("<h3 style='text-align: center; color: white;'>Rigo Engenharia</h3>", unsafe_allow_html=True)
    
    st.write("") 
    st.title("🌐 Navegação")
    if st.button("🏠 Início"): st.session_state.pagina = "inicio"
    if st.button("👥 Quem Somos"): st.session_state.pagina = "quem_somos"
    if st.button("🛠️ Nossos Serviços"): st.session_state.pagina = "servicos"
    if st.button("🏗️ Projetos Entregues"): st.session_state.pagina = "projetos"
    if st.button("📞 Contato"): st.session_state.pagina = "contato"
    
    st.divider()
    st.title("🔒 Área do Engenheiro")
    with st.expander("Acessar Gerador"):
        senha = st.text_input("Senha de Acesso", type="password")
        if senha == "rigo2026":
            if st.button("🚀 Abrir Gerador", use_container_width=True): st.session_state.pagina = "gerador"
        elif senha != "": st.error("Senha incorreta")

# --- 5. CONTEÚDO DAS PÁGINAS ---

if st.session_state.pagina == "servicos":
    st.markdown('<div class="main-banner"><h1>Nossos Serviços</h1><p>Soluções Técnicas Especializadas</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2); c3, c4 = st.columns(2)
    img_pericia = "https://images.pexels.com/photos/443383/pexels-photo-443383.jpeg?auto=compress&cs=tinysrgb&w=800"
    img_seguranca = "https://images.pexels.com/photos/8961401/pexels-photo-8961401.jpeg?auto=compress&cs=tinysrgb&w=800" 
    img_incendio = "https://www.sp.senac.br/documents/51838645/51838647/o+que+faz+um+bombeiro+civil.webp/410add97-73aa-16a2-de35-1ee2822723c6?version=1.0&t=1733407011536"
    img_patologia = "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg?auto=compress&cs=tinysrgb&w=800"
    with c1: st.markdown(f'<div class="service-card" style="background-image: url(\'{img_pericia}\');"><div class="card-overlay"><h3>Avaliações e Perícias</h3><p>Laudos judiciais, vistorias cautelares de vizinhança e avaliações precisas com rigor técnico.</p></div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="service-card" style="background-image: url(\'{img_seguranca}\');"><div class="card-overlay"><h3>Segurança do Trabalho</h3><p>Consultoria técnica em NRs, gestão de riscos ocupacionais e segurança ativa em canteiros de obras.</p></div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="service-card" style="background-image: url(\'{img_incendio}\');"><div class="card-overlay"><h3>Prevenção de Incêndios</h3><p>Projetos técnicos rigorosos para CLCB/AVCB e inspeção técnica detalhada de sistemas de combate.</p></div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="service-card" style="background-image: url(\'{img_patologia}\');"><div class="card-overlay"><h3>Patologia das Construções</h3><p>Diagnóstico de manifestações patológicas e planos de recuperação para estruturas.</p></div></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "inicio":
    st.markdown('<div class="main-banner"><h1>Rigo Engenharia</h1><p>Excelência técnica em diagnósticos e vistorias</p></div>', unsafe_allow_html=True)
    st.subheader("Bem-vindo ao nosso portal")

elif st.session_state.pagina == "quem_somos":
    st.markdown('<div class="main-banner"><h1>Quem Somos</h1><p>Autoridade Técnica e Compromisso</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.subheader("Rigo Engenharia e Serviços Ltda")
        st.write("Empresa especializada em soluções técnicas de alta precisão, perícias e vistorias cautelares.")
        st.markdown("**CNPJ:** 64.677.231/0001-17")
    with col2:
        st.subheader("Diretoria Técnica")
        st.markdown("### **Eng. Rodrigo Rigo**")
        st.markdown("* **Engenheiro Civil** – CREA/SP 5070787860\n* Pós-Graduado em Eng. de Avaliações e Perícias\n* Pós-Graduado em Eng. de Segurança do Trabalho\n* Pós-Graduado em Eng. de Prevenção de Incêndios\n* Pós-Graduando em Patologia das Construções\n* **Membro Adpat Brasil nº 813**")

elif st.session_state.pagina == "contato":
    st.markdown('<div class="main-banner"><h1>Contato</h1><p>Estamos à disposição</p></div>', unsafe_allow_html=True)
    col_info, col_form = st.columns([1, 1], gap="large")
    with col_info:
        st.subheader("Canais de Atendimento")
        try: st.image("Reng.png", width=180)
        except: pass
        st.markdown("📧 **E-mail:** [eng.rodrigorigo@gmail.com]()")
        st.markdown('<div style="display: flex; gap: 25px; align-items: center; margin-top: 20px;"><a href="https://wa.me/5511959786767" target="_blank"><img src="https://img.icons8.com/color/48/000000/whatsapp--v1.png" width="45"/></a><a href="https://www.instagram.com/eng.rodrigorigo" target="_blank"><img src="https://img.icons8.com/color/48/000000/instagram-new--v1.png" width="45"/></a></div>', unsafe_allow_html=True)
    with col_form:
        st.subheader("Solicite um Orçamento")
        with st.form("f_contato"):
            n = st.text_input("Nome Completo"); e = st.text_input("E-mail")
            servico_escolhido = st.selectbox("Qual sua necessidade?", ["Vistoria Cautelar", "Laudo de Recebimento", "Avaliação de Imóvel", "Projeto de Incêndio", "Perícia", "Outros"])
            msg = st.text_area("Descrição")
            if st.form_submit_button("Enviar Pedido", use_container_width=True): st.success("✅ Recebemos sua solicitação!")

elif st.session_state.pagina == "gerador":
    st.markdown('<div class="main-banner"><h1>🏗️ Painel do Engenheiro</h1><p>Gerador de Laudo Técnico</p></div>', unsafe_allow_html=True)
    
    with st.expander("📋 Dados Base (Obrigatórios)", expanded=True):
        col_n, col_num = st.columns([3, 1])
        nome = col_n.text_input("Nome do Solicitante *")
        num_laudo = col_num.text_input("Nº Laudo *", placeholder="001")
        
        c1, c2, c3 = st.columns(3)
        raw_cpf = c1.text_input("CPF *", placeholder="000.000.000-00")
        cpf_valido = validar_cpf(raw_cpf)
        cpf_final = formatar_cpf(raw_cpf) if cpf_valido else ""
        
        if raw_cpf:
            if cpf_valido: st.success(f"✅ CPF Válido: {cpf_final}")
            else: st.error("❌ CPF Inválido")

        apto = c2.text_input("Apto *"); torre = c3.text_input("Torre *")
        
        col_data, col_hora = st.columns([3, 1])
        data_v = col_data.text_input("Data da Vistoria * (Ex: 02/04/2026)")
        hora_v = col_hora.text_input("Horário *", placeholder="14:00")
        data_final = f"{data_v} às {hora_v}" if (data_v and hora_v) else ""

        st.write("**Data de Emissão do Laudo:**")
        ce1, ce2, ce3 = st.columns(3)
        hoje = datetime.now()
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        dia_laudo = ce1.text_input("Dia", value=hoje.day)
        mes_extenso = ce2.selectbox("Mês", meses, index=hoje.month - 1)
        ano_laudo = ce3.text_input("Ano", value=hoje.year)

    st.header("📸 Registros")
    foto_capa_raw = st.file_uploader("Foto Fachada (Obrigatório) *", type=['jpg', 'jpeg', 'png', 'heic', 'dng'])
    endereco_f = ""
    foto_capa = processar_imagem(foto_capa_raw)
    if foto_capa:
        st.image(foto_capa, caption="Prévia da Fachada", width=400)
        col_cep, col_num_end = st.columns([3, 1])
        ce_in = col_cep.text_input("CEP *")
        num_endereco = col_num_end.text_input("Nº do Endereço *", placeholder="123")
        if len(ce_in) >= 8:
            d = buscar_cep(ce_in)
            if d and "erro" not in d:
                endereco_f = f"{d.get('logradouro')}, nº {num_endereco} - {d.get('bairro')} - CEP: {d.get('cep')}"
                if endereco_f: st.success(f"📍 {endereco_f}")

    st.subheader("Fotos dos Vícios")
    vicios_raw = st.file_uploader("Selecione as fotos *", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'heic', 'dng'])
    
    lista_desordenada = []
    if vicios_raw:
        for i, f in enumerate(vicios_raw):
            col_img, col_ord, col_txt = st.columns([1, 0.5, 2])
            foto_proc = processar_imagem(f)
            if foto_proc:
                with col_img:
                    st.image(foto_proc, use_container_width=True)
                with col_ord:
                    ordem_sel = st.number_input("Ordem", min_value=1, max_value=len(vicios_raw), value=i+1, key=f"ord_{f.name}")
                with col_txt:
                    leg = st.text_input(f"Legenda ({f.name}) *", key=f"leg_{f.name}", placeholder="Descreva o vício...")
                    if leg:
                        lista_desordenada.append({"foto": foto_proc, "legenda": leg, "ordem": ordem_sel})
            st.write("---")

    lista_v_final = sorted(lista_desordenada, key=lambda x: x['ordem'])

    if st.button("🚀 GERAR LAUDO", use_container_width=True):
        if not (nome and num_laudo and cpf_valido and foto_capa and lista_v_final):
            st.error("🚨 Preencha todos os campos obrigatórios e coloque legendas nas fotos.")
        else:
            try:
                # 1. Carrega o Template
                doc_tpl = DocxTemplate("LT_RIGO_001_2026-MODELO.docx")
                
                # 2. Monta o contexto para o docxtpl
                ctx = {
                    "nome": nome, "cpf": cpf_final, "apartamento": apto, "torre": torre,
                    "data_da_Vis": data_final, "Endereco": endereco_f,
                    "dia_laudo": dia_laudo, "mes_laudo_extenso": mes_extenso, "ano": ano_laudo,
                    "foto_fachada": InlineImage(doc_tpl, foto_capa, width=Mm(110)),
                    "registros": [{"foto": InlineImage(doc_tpl, x["foto"], width=Mm(140)), "legenda": x["legenda"]} for x in lista_v_final]
                }
                
                # 3. Renderiza
                doc_tpl.render(ctx)
                
                # 4. Processa para remover páginas em branco
                buffer_temp = io.BytesIO()
                doc_tpl.save(buffer_temp)
                buffer_temp.seek(0)
                
                doc_final_obj = Document(buffer_temp)
                doc_final_obj = remover_paginas_em_branco_fim(doc_final_obj)
                
                # 5. Salva para o usuário
                buffer_saida = io.BytesIO()
                doc_final_obj.save(buffer_saida)
                
                nome_arquivo_saida = f"LT_RIGO_{num_laudo} - {nome}.docx"
                st.download_button("📥 Baixar Laudo", data=buffer_saida.getvalue(), file_name=nome_arquivo_saida)
                
            except Exception as e: 
                st.error(f"Erro ao gerar: {e}")

elif st.session_state.pagina == "projetos":
    st.header("Projetos Entregues")
    st.info("Seção em desenvolvimento.")