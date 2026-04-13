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

# --- OTIMIZAÇÃO DE MEMÓRIA E SUPORTE IPHONE (HEIF) ---
@st.cache_data(show_spinner="Otimizando imagem...", max_entries=10)
def processar_imagem(arquivo):
    if arquivo is None:
        return None
    try:
        # Abre a imagem (HEIC, JPEG ou PNG)
        with Image.open(arquivo) as img:
            # Converte para RGB (necessário para JPEG e Word)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionamento agressivo para economizar RAM no mobile
            max_size = 1000 
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.LANCZOS)
            
            buffer = io.BytesIO()
            # Salva como JPEG 70% (Equilíbrio perfeito entre peso e nitidez no laudo)
            img.save(buffer, format="JPEG", quality=70, optimize=True)
            buffer.seek(0)
            return buffer
    except Exception as e:
        return None

def remover_paginas_em_branco_fim(doc):
    for paragraph in reversed(doc.paragraphs):
        if not paragraph.text.strip():
            p = paragraph._element
            p.getparent().remove(p)
        else:
            break
    return doc

# --- 3. ESTILIZAÇÃO CSS (INCLUINDO AJUSTE MOBILE) ---
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
    .service-card h3 { color: #ffffff !important; margin-bottom: 8px; font-size: 22px; font-weight: bold; }
    .service-card p { color: #f0f0f0 !important; font-size: 14px; line-height: 1.5; }
    section[data-testid="stSidebar"] .stButton button { width: 100%; text-align: left; border: none; background-color: transparent; padding: 10px 0px; }
    
    div.stButton > button[kind="secondaryFormSubmit"] {
        background-color: transparent !important;
        color: rgba(0,0,0,0.4) !important;
        border: none !important;
        font-size: 22px !important;
        padding: 5px !important;
    }
    
    /* Melhoria visual para mobile */
    @media (max-width: 768px) {
        .main-banner { padding: 40px 20px; }
        .stButton button { height: 45px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO LATERAL ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "inicio"

if 'lista_fotos_cache' not in st.session_state:
    st.session_state.lista_fotos_cache = []

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

    if st.session_state.pagina == "gerador":
        st.divider()
        if st.button("🧹 Limpar Memória (Crash)"):
            st.cache_data.clear()
            st.session_state.lista_fotos_cache = []
            st.rerun()

# --- 5. CONTEÚDO ---
if st.session_state.pagina == "inicio":
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
        st.markdown("* **Engenheiro Civil** – CREA/SP 5070787860\n* Pós-Graduado em Eng. de Avaliações e Perícias\n* Pós-Graduado em Eng. de Segurança do Trabalho\n* Pós-Graduado em Eng. de Prevenção de Incendio\n* Pós-Graduando em Patologia das Construções\n* **Membro Adpat Brasil nº 813**")

elif st.session_state.pagina == "servicos":
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

elif st.session_state.pagina == "contato":
    st.markdown('<div class="main-banner"><h1>Contato</h1><p>Estamos à disposição</p></div>', unsafe_allow_html=True)
    col_info, col_form = st.columns([1, 1], gap="large")
    with col_info:
        st.subheader("Canais de Atendimento")
        st.markdown("📧 **E-mail:** [eng.rodrigorigo@gmail.com]()")
        st.markdown("📞 **WhatsApp:** (11) 95978-6767")
        st.markdown("📸 **Instagram:** @eng.rodrigorigo")
    with col_form:
        with st.form("f_contato"):
            st.text_input("Nome Completo")
            st.text_input("E-mail")
            st.selectbox("Assunto", ["Orçamento", "Dúvida Técnica", "Parceria"])
            st.text_area("Sua Mensagem")
            st.form_submit_button("Enviar Mensagem")

elif st.session_state.pagina == "gerador":
    st.markdown('<div class="main-banner"><h1>🏗️ Painel do Engenheiro</h1><p>Gerador de Laudo Técnico</p></div>', unsafe_allow_html=True)
    
    with st.expander("📋 Dados Base (Obrigatórios)", expanded=True):
        col_n, col_num = st.columns([3, 1])
        nome = col_n.text_input("Nome do Solicitante *")
        num_laudo = col_num.text_input("Nº Laudo *", placeholder="001")
        
        c1, c2, c3 = st.columns(3)
        raw_cpf = c1.text_input("CPF *")
        cpf_valido = validar_cpf(raw_cpf)
        cpf_final = formatar_cpf(raw_cpf) if cpf_valido else ""
        if raw_cpf and not cpf_valido: st.error("❌ CPF Inválido")

        apto = c2.text_input("Apto *")
        torre = c3.text_input("Torre *")
        
        col_data, col_hora = st.columns([3, 1])
        data_v = col_data.text_input("Data da Vistoria * (Ex: 02/04/2026)")
        hora_v = col_hora.text_input("Horário *", placeholder="14:00")
        data_final = f"{data_v} às {hora_v}" if (data_v and hora_v) else ""

        st.write("**Data de Emissão do Laudo:**")
        ce1, ce2, ce3 = st.columns(3)
        from datetime import datetime, timedelta, timezone

        # Ajusta para o fuso horário de Brasília (UTC-3)
        fuso_brasilia = timezone(timedelta(hours=-3))
        hoje = datetime.now(fuso_brasilia)

        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        dia_laudo = ce1.text_input("Dia", value=str(hoje.day).zfill(2))
        mes_extenso = ce2.selectbox("Mês", meses, index=hoje.month - 1)
        ano_laudo = ce3.text_input("Ano", value=hoje.year)

    @st.fragment
    def sessao_fotos():
        st.header("📸 Registros")
        foto_capa_raw = st.file_uploader("Foto Fachada (Obrigatório) *", type=['jpg', 'jpeg', 'png', 'heic'], key="capa")
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
                    st.success(f"📍 {endereco_f}")

        st.divider()
        st.subheader("Fotos dos Vícios")
        vicios_raw = st.file_uploader("Selecione as fotos *", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'heic'], key="vicios")
        
        if vicios_raw:
            if st.button("🔄 Adicionar Fotos ao Lote"):
                for f in vicios_raw:
                    # Verifica se o arquivo já não foi adicionado para não duplicar
                    if not any(x['nome'] == f.name for x in st.session_state.lista_fotos_cache):
                        foto_p = processar_imagem(f)
                        if foto_p:
                            # Criamos um ID único para a KEY não bugar no 'X' de excluir
                            id_vicio = f"{f.name}_{datetime.now().timestamp()}"
                            st.session_state.lista_fotos_cache.append({
                                "id_unico": id_vicio, 
                                "nome": f.name, 
                                "foto": foto_p, 
                                "ambiente": "Entrada", 
                                "legenda": ""
                            })
                st.rerun()

        ambientes_opcoes = ["Entrada", "Cozinha", "Área de serviço", "Varanda", "Sala de estar", "Dormitório 1", "Dormitório 2", "Dormitório 3", "Banheiro Social", "Banheiro Suíte", "Depósito"]

        if st.session_state.lista_fotos_cache:
            with st.form("form_fotos"):
                for idx, item in enumerate(st.session_state.lista_fotos_cache):
                    # Ajuste de colunas para caber legenda no celular
                    col_img, col_info = st.columns([1, 2.5])
                    
                    with col_img: 
                        st.image(item["foto"], use_container_width=True)

                    with col_info: 
                        # Usamos o id_unico na key para o Streamlit não perder a referência da legenda
                        st.session_state.lista_fotos_cache[idx]["ambiente"] = st.selectbox(
                            "Ambiente", 
                            ambientes_opcoes, 
                            index=ambientes_opcoes.index(item["ambiente"]), 
                            key=f"amb_{item['id_unico']}"
                        )
                        
                        st.session_state.lista_fotos_cache[idx]["legenda"] = st.text_input(
                            "Descrição do Vício *", 
                            value=item["legenda"], 
                            key=f"leg_{item['id_unico']}"
                        )
                        
                        if st.form_submit_button("✕ Remover Foto", key=f"del_{item['id_unico']}"):
                            st.session_state.lista_fotos_cache.pop(idx)
                            st.rerun()
                    st.write("---")
                
                c_save, c_del = st.columns(2)
                if c_save.form_submit_button("💾 SALVAR LEGENDAS", use_container_width=True):
                    st.toast("Dados salvos no cache!", icon="✅")
                if c_del.form_submit_button("🗑️ LIMPAR TODAS AS FOTOS", use_container_width=True):
                    st.session_state.lista_fotos_cache = []
                    st.rerun()
        
        lista_v_final = [x for x in st.session_state.lista_fotos_cache if x["legenda"] != ""]
        st.session_state.dados_fotos = {"capa": foto_capa, "lista": lista_v_final, "endereco": endereco_f}

    sessao_fotos()

    if st.button("🚀 GERAR LAUDO", use_container_width=True):
        f_dados = st.session_state.get("dados_fotos", {})
        foto_capa = f_dados.get("capa")
        lista_v_final = f_dados.get("lista", [])
        endereco_f = f_dados.get("endereco", "")

        if not (nome and num_laudo and cpf_final and foto_capa and lista_v_final):
            st.error("🚨 Preencha todos os campos obrigatórios.")
        else:
            try:
                doc_tpl = DocxTemplate("LT_RIGO_001_2026-MODELO.docx")
                ctx = {
                    "nome": nome, "cpf": cpf_final, "apartamento": apto, "torre": torre,
                    "data_da_Vis": data_final, "Endereco": endereco_f,
                    "dia_laudo": dia_laudo, "mes_laudo_extenso": mes_extenso, "ano": ano_laudo,
                    "foto_fachada": InlineImage(doc_tpl, foto_capa, width=Mm(110)),
                    "registros": [
                        {"foto": InlineImage(doc_tpl, x["foto"], width=Mm(140)), "ambiente": x["ambiente"], "legenda": x["legenda"]} 
                        for x in lista_v_final
                    ]
                }
                doc_tpl.render(ctx)
                
                buffer_temp = io.BytesIO()
                doc_tpl.save(buffer_temp)
                buffer_temp.seek(0)
                
                doc_final_obj = Document(buffer_temp)
                doc_final_obj = remover_paginas_em_branco_fim(doc_final_obj)
                
                buffer_saida = io.BytesIO()
                doc_final_obj.save(buffer_saida)
                
                st.success("✅ Laudo gerado com sucesso!")
                st.download_button(
                    label="📥 Baixar Laudo Word",
                    data=buffer_saida.getvalue(),
                    file_name=f"LT_RIGO_{num_laudo}_2026 - {nome}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Erro ao gerar: {e}")

elif st.session_state.pagina == "projetos":
    st.header("🏗️ Projetos Entregues")
    st.info("Seção em desenvolvimento.")