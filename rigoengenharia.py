import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
import re
import requests

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

# --- 3. ESTILIZAÇÃO CSS (Foco em Imagens de Fundo) ---
st.markdown("""
    <style>
    .main-banner {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=2070");
        background-size: cover;
        background-position: center;
        padding: 80px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Estilo dos Cards apenas com Imagem e Texto */
    .service-card {
        height: 350px;
        border-radius: 15px;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: flex-end;
        padding: 25px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    .service-card:hover {
        transform: translateY(-10px);
    }
    
    /* Overlay para garantir leitura do texto sobre a foto */
    .card-overlay {
        position: absolute;
        bottom: 0; left: 0; right: 0; top: 0;
        background: linear-gradient(transparent 40%, rgba(0,0,0,0.95) 90%);
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 25px;
    }

    .service-card h3 {
        color: #ffffff !important;
        margin-bottom: 8px;
        font-size: 22px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    
    .service-card p {
        color: #f0f0f0 !important;
        font-size: 14px;
        line-height: 1.5;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }

    section[data-testid="stSidebar"] .stButton button {
        width: 100%; text-align: left; border: none; background-color: transparent; padding: 10px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO LATERAL (SIDEBAR) ---
with st.sidebar:
    st.write("") 
    try:
        st.image("Reng.png", use_container_width=True)
    except:
        st.write("---")
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
            if st.button("🚀 Abrir Gerador", use_container_width=True):
                st.session_state.pagina = "gerador"
        elif senha != "":
            st.error("Senha incorreta")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "inicio"

# --- 5. CONTEÚDO DAS PÁGINAS ---

if st.session_state.pagina == "servicos":
    st.markdown('<div class="main-banner"><h1>Nossos Serviços</h1><p>Soluções Técnicas Especializadas</p></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    
    # Imagens focadas em engenharia e segurança
    img_pericia = "https://images.pexels.com/photos/443383/pexels-photo-443383.jpeg?auto=compress&cs=tinysrgb&w=800"
    
    # NOVA IMAGEM: Segurança do Trabalho (Capacete técnico sobre planta de engenharia)
    img_seguranca_nova = "https://images.pexels.com/photos/8961401/pexels-photo-8961401.jpeg?auto=compress&cs=tinysrgb&w=800" 
    
    # NOVA IMAGEM: Prevenção de Incêndios (Bombeiros com equipamentos de combate)
    img_incendio_nova = "https://www.sp.senac.br/documents/51838645/51838647/o+que+faz+um+bombeiro+civil.webp/410add97-73aa-16a2-de35-1ee2822723c6?version=1.0&t=1733407011536"
    
    img_patologia = "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg?auto=compress&cs=tinysrgb&w=800"

    with c1:
        st.markdown(f"""
            <div class="service-card" style="background-image: url('{img_pericia}');">
                <div class="card-overlay">
                    <h3>Avaliações e Perícias</h3>
                    <p>Laudos judiciais, vistorias cautelares de vizinhança e avaliações precisas com rigor técnico.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
            <div class="service-card" style="background-image: url('{img_seguranca_nova}');">
                <div class="card-overlay">
                    <h3>Segurança do Trabalho</h3>
                    <p>Consultoria técnica em Normas Regulamentadoras (NRs), gestão de riscos ocupacionais e segurança ativa em canteiros de obras.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
            <div class="service-card" style="background-image: url('{img_incendio_nova}');">
                <div class="card-overlay">
                    <h3>Prevenção de Incêndios</h3>
                    <p>Projetos técnicos rigorosos para CLCB/AVCB e inspeção técnica detalhada de sistemas de combate a incêndio.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
            <div class="service-card" style="background-image: url('{img_patologia}');">
                <div class="card-overlay">
                    <h3>Patologia das Construções</h3>
                    <p>Diagnóstico de manifestações patológicas e planos de recuperação para estruturas e reformas.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.pagina == "inicio":
    st.markdown('<div class="main-banner"><h1>Rigo Engenharia</h1><p>Excelência técnica em diagnósticos e vistorias</p></div>', unsafe_allow_html=True)
    st.subheader("Bem-vindo ao nosso portal")
    st.write("Selecione uma opção no menu lateral para conhecer nossos serviços ou acessar o painel técnico.")

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
        st.markdown("""
        * **Engenheiro Civil** – CREA/SP 5070787860
        * Pós-Graduado em Eng. de Avaliações e Perícias
        * Pós-Graduado em Eng. de Segurança do Trabalho
        * Pós-Graduado em Eng. de Prevenção de Incêndios
        * Pós-Graduando em Patologia das Construções
        * **Membro Adpat Brasil nº 813**
        """)

elif st.session_state.pagina == "contato":
    st.markdown('<div class="main-banner"><h1>Contato</h1><p>Estamos à disposição</p></div>', unsafe_allow_html=True)
    col_info, col_form = st.columns([1, 1], gap="large")
    with col_info:
        st.subheader("Canais de Atendimento")
        try: st.image("Reng.png", width=180)
        except: pass
        st.markdown("📧 **E-mail:** [contato@rigoengenharia.com.br](mailto:contato@rigoengenharia.com.br)")
        st.markdown("""
            <div style="display: flex; gap: 25px; align-items: center; margin-top: 20px;">
                <a href="https://wa.me/5511959786767" target="_blank"><img src="https://img.icons8.com/color/48/000000/whatsapp--v1.png" width="45"/></a>
                <a href="https://www.instagram.com/eng.rodrigorigo" target="_blank"><img src="https://img.icons8.com/color/48/000000/instagram-new--v1.png" width="45"/></a>
            </div>
            """, unsafe_allow_html=True)
    with col_form:
        st.subheader("Solicite um Orçamento")
        with st.form("f_contato"):
            n = st.text_input("Nome Completo")
            e = st.text_input("E-mail")
            servico_escolhido = st.selectbox("Qual sua necessidade?", ["Vistoria Cautelar", "Laudo de Recebimento", "Avaliação de Imóvel", "Projeto de Incêndio", "Perícia", "Outros"])
            msg = st.text_area("Descrição")
            if st.form_submit_button("Enviar Pedido", use_container_width=True):
                st.success("✅ Recebemos sua solicitação!")

elif st.session_state.pagina == "gerador":
    st.markdown('<div class="main-banner"><h1>🏗️ Painel do Engenheiro</h1><p>Gerador de Laudo Técnico</p></div>', unsafe_allow_html=True)
    with st.expander("📋 Dados Base", expanded=True):
        col_n, col_num = st.columns([3, 1])
        nome = col_n.text_input("Nome do Solicitante")
        num_laudo = col_num.text_input("Nº Laudo", placeholder="001")
        c1, c2, c3 = st.columns(3)
        cpf_in = c1.text_input("CPF")
        apto = c2.text_input("Apto")
        torre = c3.text_input("Torre")
        data_v = st.text_input("Data da Vistoria")

    st.header("📸 Registros")
    foto_capa = st.file_uploader("Foto Fachada", type=['jpg', 'jpeg', 'png'])
    endereco_f = ""
    if foto_capa:
        ce_in = st.text_input("CEP")
        if len(ce_in) >= 8:
            d = buscar_cep(ce_in)
            if d and "erro" not in d:
                endereco_f = f"{d.get('logradouro')}, {d.get('localidade')}"
                st.success(f"📍 {endereco_f}")

    vicios = st.file_uploader("Fotos dos Vícios", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    lista_v = []
    if vicios:
        for i, f in enumerate(vicios):
            leg = st.text_input(f"Legenda Figura {i+1}", key=f"v_{i}")
            lista_v.append({"foto": f, "legenda": leg})

    if st.button("🚀 GERAR LAUDO", use_container_width=True):
        try:
            doc = DocxTemplate("LT_RIGO_001_2026-MODELO.docx")
            ctx = {
                "nome": nome, "cpf": cpf_in, "apartamento": apto, "torre": torre,
                "data_da_Vis": data_v, "Endereco": endereco_f,
                "foto_fachada": InlineImage(doc, foto_capa, width=Mm(110)),
                "registros": [{"foto": InlineImage(doc, x["foto"], width=Mm(110)), "legenda": x["legenda"]} for x in lista_v]
            }
            doc.render(ctx)
            buf = io.BytesIO()
            doc.save(buf)
            st.download_button("📥 Baixar Laudo", data=buf.getvalue(), file_name=f"LT_{num_laudo}.docx")
        except Exception as e: st.error(f"Erro: {e}")

elif st.session_state.pagina == "projetos":
    st.header("Projetos Entregues")
    st.info("Seção em desenvolvimento.")