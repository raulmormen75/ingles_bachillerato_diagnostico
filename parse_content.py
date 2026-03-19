#!/usr/bin/env python3
"""
Parse 'Contenido de clase diagnóstico.txt' and generate a self-contained HTML educational platform.
"""
import re
import json
import html as html_module
import unicodedata

INPUT_FILE = r"d:\Mi unidad\IFR\Inglés\Bachillerato\Contenido de clase diagnóstico.txt"
OUTPUT_FILE = r"d:\Mi unidad\IFR\Inglés\Bachillerato\index.html"
SHIELD_URL = "https://i.postimg.cc/G8VMfXhR/274744310_104329305530428_353308199971240379_n.jpg"
DEFAULT_TITLE = "IFR · Inglés diagnóstico para bachillerato"
DEFAULT_DESCRIPTION = "Material académico IFR para inglés diagnóstico de bachillerato con lectura bilingüe, ejemplos guiados y ejercicios de apoyo."

def read_source():
    """Read the source file with proper encoding."""
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            with open(INPUT_FILE, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError("Could not read source file")

def split_topics(text):
    """Split text into topic sections by '# N.' headers."""
    # Split by topic headers
    pattern = r'^# (\d+)\.\s+(.+?)$'
    parts = re.split(pattern, text, flags=re.MULTILINE)
    
    topics = []
    # parts[0] is before first match, then groups of 3: (number, title, content)
    i = 1
    while i < len(parts):
        num = int(parts[i])
        title = parts[i+1].strip()
        content = parts[i+2] if i+2 < len(parts) else ""
        topics.append({
            'id': num,
            'title': title,
            'raw': content
        })
        i += 3
    
    return topics

def extract_icon(title):
    """Extract emoji icon from title."""
    emojis = re.findall(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]', title)
    return emojis[0] if emojis else '📚'

def clean_title(title):
    """Remove emojis from title but keep the text."""
    return re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\s]+$', '', title).strip()

def split_sections(raw_content):
    """Split topic raw content into numbered sections."""
    pattern = r'^## (\d+\.\d+)\s+(.+?)$'
    parts = re.split(pattern, raw_content, flags=re.MULTILINE)
    
    sections = []
    i = 1
    while i < len(parts):
        sec_num = parts[i]
        sec_title = parts[i+1].strip()
        sec_content = parts[i+2] if i+2 < len(parts) else ""
        sections.append({
            'number': sec_num,
            'title': sec_title,
            'content': sec_content.strip()
        })
        i += 3
    
    return sections

def classify_section(title):
    """Classify a section by its title into content types."""
    title_lower = title.lower()
    if 'explanation' in title_lower or 'explicación' in title_lower:
        return 'explanation'
    elif 'what this topic is for' in title_lower or 'para qué sirve' in title_lower:
        return 'purpose'
    elif 'exercise' in title_lower or 'ejercicio' in title_lower:
        return 'exercises'
    elif 'teacher' in title_lower or 'profesor' in title_lower:
        return 'teacher'
    elif 'guided example' in title_lower or 'ejemplo' in title_lower:
        return 'examples'
    elif 'common mistake' in title_lower or 'errores comunes' in title_lower or 'common pronunciation' in title_lower:
        return 'mistakes'
    elif 'how english speakers' in title_lower or 'cómo lo usan' in title_lower:
        return 'usage'
    else:
        return 'structure'

def content_to_html_blocks(content):
    """Convert raw markdown-like content into HTML blocks."""
    lines = content.split('\n')
    html_parts = []
    in_example = False
    
    for line in lines:
        line = line.rstrip('\r')
        stripped = line.strip()
        
        # Skip separator lines
        if stripped == '---':
            html_parts.append('<hr class="section-divider">')
            continue
        
        if not stripped:
            continue
        
        # Subsection headers
        if stripped.startswith('### '):
            header_text = stripped[4:]
            html_parts.append(f'<h4 class="subsection-header">{html_module.escape(header_text)}</h4>')
            continue
        
        # Content line - detect type by flags
        escaped = html_module.escape(stripped)
        
        # Pronunciation line
        if stripped.startswith('Pronunciación:'):
            pron_text = stripped[14:].strip()
            html_parts.append(f'<div class="pronunciation-line">🔊 <em>{html_module.escape(pron_text)}</em></div>')
            continue
        
        # English line (US flag) - flag is 2 code points (regional indicators)
        if stripped.startswith('🇺🇸'):
            text = re.sub(r'^🇺🇸\s*', '', stripped).strip()
            # Check if it's a lettered option
            if re.match(r'^[a-d]\)', text):
                html_parts.append(f'<div class="option-line en-text">{html_module.escape(text)}</div>')
            else:
                html_parts.append(f'<div class="content-line en-text"><span class="lang-flag lang-flag-us" aria-hidden="true"></span> {html_module.escape(text)}</div>')
            continue
        
        # Spanish line (MX flag) - flag is 2 code points (regional indicators)
        if stripped.startswith('🇲🇽'):
            text = re.sub(r'^🇲🇽\s*', '', stripped).strip()
            if re.match(r'^[a-d]\)', text):
                html_parts.append(f'<div class="option-line es-text">{html_module.escape(text)}</div>')
            else:
                html_parts.append(f'<div class="content-line es-text"><span class="lang-flag lang-flag-mx" aria-hidden="true"></span> {html_module.escape(text)}</div>')
            continue
        
        # General text
        html_parts.append(f'<p>{escaped}</p>')
    
    return '\n'.join(html_parts)

def section_to_card(section, topic_id):
    """Convert a section object to an HTML card."""
    sec_type = classify_section(section['title'])
    
    type_labels = {
        'explanation': ('Explicación', 'explanation-card', '📖'),
        'purpose': ('Para qué sirve', 'purpose-card', '🎯'),
        'structure': ('Estructura', 'structure-card', '🧩'),
        'usage': ('Uso real', 'usage-card', '🌍'),
        'examples': ('Ejemplos guiados', 'examples-card', '✅'),
        'mistakes': ('Errores comunes', 'mistakes-card', '⚠️'),
        'exercises': ('Ejercicios', 'exercises-card', '📝'),
        'teacher': ('Diagnóstico docente', 'teacher-card', '🔎'),
    }
    
    label, css_class, icon = type_labels.get(sec_type, ('Contenido', 'content-card', '📄'))
    inner_html = content_to_html_blocks(section['content'])
    title_html = html_module.escape(section['title'])
    
    # For examples section, add audio buttons to English lines
    if sec_type == 'examples':
        inner_html = add_audio_buttons(inner_html)
    
    return f'''
    <div class="content-card {css_class}" id="topic-{topic_id}-{section['number'].replace('.', '-')}">
        <div class="card-label"><span class="card-icon">{icon}</span> {label}</div>
        <h3 class="card-title">{title_html}</h3>
        <div class="card-body">
            {inner_html}
        </div>
    </div>
    '''

def add_audio_buttons(html_content):
    """Add audio TTS buttons to example English text lines in the examples section."""
    # Find example headers and their following English lines
    lines = html_content.split('\n')
    result = []
    in_example_block = False
    
    for line in lines:
        result.append(line)
        # Add audio buttons after English content lines in examples (not explanation lines)
        if 'class="content-line en-text"' in line and 'class="lang-flag lang-flag-us"' in line:
            # Extract the text for TTS
            match = re.search(r'</span>\s*(.+?)</div>', line)
            if match:
                text = match.group(1).strip()
                # Don't add audio to meta-explanations (lines that describe the example)
                if not any(kw in text.lower() for kw in ['this example', 'this sentence', 'this model', 'notice', 'in the first', 'in the second', 'students must']):
                    safe_text = html_module.escape(text).replace("'", "\\'").replace('"', '&quot;')
                    result.append(f'''
                    <div class="audio-controls">
                        <button class="audio-btn audio-normal" onclick="speakText('{safe_text}', 1.0, this)" title="Escuchar normal">
                            <span class="audio-icon">▶</span> Normal
                        </button>
                        <button class="audio-btn audio-slow" onclick="speakText('{safe_text}', 0.5, this)" title="Escuchar lento 0.5x">
                            <span class="audio-icon">🐢</span> Lento 0.5×
                        </button>
                    </div>
                    ''')
    
    return '\n'.join(result)

def build_topic_html(topic, sections):
    """Build the full HTML for a single topic."""
    title = clean_title(topic['title'])
    icon = extract_icon(topic['title'])
    topic_id = topic['id']
    
    cards_html = '\n'.join(section_to_card(s, topic_id) for s in sections)
    
    return f'''
    <div class="topic-page" id="topic-{topic_id}" style="display:none;">
        <div class="topic-header">
            <div class="topic-icon">{icon}</div>
            <div class="topic-header-text">
                <span class="topic-number">Tema {topic_id}</span>
                <h2 class="topic-title">{html_module.escape(title)}</h2>
            </div>
        </div>
        <div class="topic-content">
            {cards_html}
        </div>
        <div class="topic-nav-bottom">
            {'<button class="nav-btn prev-btn" onclick="navigateTopic(' + str(topic_id - 1) + ')">← Tema anterior</button>' if topic_id > 1 else '<span></span>'}
            <button class="nav-btn index-btn" onclick="showHome()">📋 Índice</button>
            {'<button class="nav-btn next-btn" onclick="navigateTopic(' + str(topic_id + 1) + ')">Tema siguiente →</button>' if topic_id < 17 else '<span></span>'}
        </div>
    </div>
    '''

def build_home_html(topics):
    """Build the home/index page."""
    cards = []
    for t in topics:
        title = clean_title(t['title'])
        icon = extract_icon(t['title'])
        tid = t['id']
        cards.append(f'''
        <div class="home-card" onclick="navigateTopic({tid})">
            <div class="home-card-icon">{icon}</div>
            <div class="home-card-number">Tema {tid}</div>
            <div class="home-card-title">{html_module.escape(title)}</div>
        </div>
        ''')
    
    return '\n'.join(cards)

def build_sidebar_html(topics):
    """Build the sidebar navigation."""
    items = []
    for t in topics:
        title = clean_title(t['title'])
        icon = extract_icon(t['title'])
        tid = t['id']
        # Truncate long titles
        short_title = title.split('/')[0].strip() if '/' in title else title
        if len(short_title) > 35:
            short_title = short_title[:32] + '…'
        items.append(f'''
        <li class="sidebar-item" id="sidebar-item-{tid}" onclick="navigateTopic({tid})">
            <span class="sidebar-icon">{icon}</span>
            <span class="sidebar-number">{tid}.</span>
            <span class="sidebar-text">{html_module.escape(short_title)}</span>
        </li>
        ''')
    
    return '\n'.join(items)

def generate_full_html(topics_data):
    """Generate the complete HTML file."""
    
    # Process each topic
    topic_pages = []
    for topic in topics_data:
        sections = split_sections(topic['raw'])
        topic_pages.append(build_topic_html(topic, sections))
    
    home_cards = build_home_html(topics_data)
    sidebar_items = build_sidebar_html(topics_data)
    all_topic_pages = '\n'.join(topic_pages)
    
    # Build search index data
    search_data = []
    for t in topics_data:
        title = clean_title(t['title'])
        search_data.append({
            'id': t['id'],
            'title': title,
            'keywords': title.lower()
        })
    search_json = json.dumps(search_data, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IFR — Material de Clase: Inglés Diagnóstico Bachillerato</title>
    <meta name="description" content="Plataforma educativa IFR para material de clase y consulta de inglés diagnóstico para bachillerato. 17 temas desde saludos básicos hasta Zero Conditional.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ===== CSS RESET & ROOT ===== */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        :root {{
            --ifr-primary: #1C1E5A;
            --ifr-dark: #14143A;
            --ifr-medium: #2B2F8F;
            --ifr-green: #2CE51E;
            --ifr-green-soft: #22b816;
            --ifr-white: #FFFFFF;
            --ifr-light-bg: #F0F2FF;
            --ifr-body-bg: #E8EAF6;
            
            /* Section-specific colors */
            --color-explanation: #1C1E5A;
            --color-explanation-bg: #E8EAF6;
            --color-purpose: #00695C;
            --color-purpose-bg: #E0F2F1;
            --color-structure: #1565C0;
            --color-structure-bg: #E3F2FD;
            --color-usage: #4527A0;
            --color-usage-bg: #EDE7F6;
            --color-examples: #2E7D32;
            --color-examples-bg: #E8F5E9;
            --color-mistakes: #BF360C;
            --color-mistakes-bg: #FBE9E7;
            --color-exercises: #E65100;
            --color-exercises-bg: #FFF3E0;
            --color-teacher: #6A1B9A;
            --color-teacher-bg: #F3E5F5;
            
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 30px rgba(0,0,0,0.12);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --sidebar-width: 280px;
            --header-height: 64px;
        }}
        
        html {{ scroll-behavior: smooth; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--ifr-body-bg);
            color: #1a1a2e;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* ===== TOP HEADER ===== */
        .top-header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: linear-gradient(135deg, var(--ifr-dark) 0%, var(--ifr-primary) 50%, var(--ifr-medium) 100%);
            color: var(--ifr-white);
            display: flex;
            align-items: center;
            padding: 0 24px;
            z-index: 1000;
            box-shadow: var(--shadow-lg);
        }}
        
        .header-hamburger {{
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            margin-right: 12px;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        .header-hamburger:hover {{ background: rgba(255,255,255,0.15); }}
        
        .header-logo {{
            font-weight: 800;
            font-size: 20px;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-logo .logo-accent {{
            background: var(--ifr-green);
            color: var(--ifr-dark);
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 700;
        }}
        
        .header-search {{
            margin-left: auto;
            position: relative;
        }}
        .header-search input {{
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 24px;
            padding: 8px 16px 8px 38px;
            color: white;
            font-size: 14px;
            width: 260px;
            outline: none;
            transition: all 0.3s;
            font-family: 'Inter', sans-serif;
        }}
        .header-search input::placeholder {{ color: rgba(255,255,255,0.6); }}
        .header-search input:focus {{
            background: rgba(255,255,255,0.25);
            border-color: var(--ifr-green);
            width: 320px;
        }}
        .header-search .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255,255,255,0.6);
            font-size: 14px;
        }}
        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            margin-top: 8px;
            background: white;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            max-height: 320px;
            overflow-y: auto;
            display: none;
            z-index: 1001;
        }}
        .search-results.show {{ display: block; }}
        .search-result-item {{
            padding: 12px 16px;
            cursor: pointer;
            color: var(--ifr-dark);
            font-size: 14px;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.15s;
        }}
        .search-result-item:hover {{ background: var(--ifr-light-bg); }}
        .search-result-item:last-child {{ border-bottom: none; }}
        .search-result-num {{
            font-weight: 700;
            color: var(--ifr-medium);
            margin-right: 8px;
        }}
        
        /* ===== SIDEBAR ===== */
        .sidebar {{
            position: fixed;
            top: var(--header-height);
            left: 0;
            width: var(--sidebar-width);
            height: calc(100vh - var(--header-height));
            background: var(--ifr-white);
            border-right: 1px solid #e0e0e0;
            overflow-y: auto;
            z-index: 900;
            transition: transform 0.3s ease;
        }}
        
        .sidebar-title {{
            padding: 20px 20px 12px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #999;
        }}
        
        .sidebar-list {{
            list-style: none;
            padding: 0 8px 24px;
        }}
        
        .sidebar-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            color: #555;
            transition: all 0.2s;
            margin-bottom: 2px;
        }}
        .sidebar-item:hover {{
            background: var(--ifr-light-bg);
            color: var(--ifr-primary);
        }}
        .sidebar-item.active {{
            background: linear-gradient(135deg, var(--ifr-primary), var(--ifr-medium));
            color: white;
            font-weight: 600;
        }}
        .sidebar-icon {{ font-size: 16px; flex-shrink: 0; }}
        .sidebar-number {{ font-weight: 700; min-width: 20px; }}
        .sidebar-text {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        
        .sidebar-progress {{
            padding: 16px 20px;
            border-bottom: 1px solid #eee;
        }}
        .progress-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
            margin-bottom: 8px;
        }}
        .progress-bar {{
            height: 6px;
            background: #e8e8e8;
            border-radius: 3px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--ifr-green), var(--ifr-green-soft));
            border-radius: 3px;
            transition: width 0.5s ease;
            width: 0%;
        }}
        .progress-text {{
            font-size: 11px;
            color: #999;
            margin-top: 6px;
        }}
        
        /* ===== MAIN CONTENT ===== */
        .main-content {{
            margin-left: var(--sidebar-width);
            margin-top: var(--header-height);
            padding: 32px;
            min-height: calc(100vh - var(--header-height));
        }}
        
        /* ===== HOME PAGE ===== */
        .home-page {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        
        .home-hero {{
            text-align: center;
            padding: 48px 24px;
            background: linear-gradient(135deg, var(--ifr-dark) 0%, var(--ifr-primary) 40%, var(--ifr-medium) 100%);
            border-radius: var(--radius-lg);
            color: white;
            margin-bottom: 36px;
            box-shadow: var(--shadow-lg);
        }}
        .home-hero h1 {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 12px;
        }}
        .home-hero .hero-accent {{
            color: var(--ifr-green);
        }}
        .home-hero p {{
            font-size: 16px;
            opacity: 0.85;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.7;
        }}
        
        .home-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
            gap: 16px;
        }}
        
        .home-card {{
            background: white;
            border-radius: var(--radius-md);
            padding: 24px 20px;
            cursor: pointer;
            transition: all 0.25s ease;
            box-shadow: var(--shadow-sm);
            border: 2px solid transparent;
            text-align: center;
        }}
        .home-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--ifr-green);
        }}
        .home-card-icon {{
            font-size: 36px;
            margin-bottom: 12px;
        }}
        .home-card-number {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--ifr-medium);
            margin-bottom: 6px;
        }}
        .home-card-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--ifr-dark);
            line-height: 1.4;
        }}
        
        /* ===== TOPIC PAGE ===== */
        .topic-page {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .topic-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 32px;
            padding: 32px;
            background: linear-gradient(135deg, var(--ifr-dark), var(--ifr-primary));
            border-radius: var(--radius-lg);
            color: white;
            box-shadow: var(--shadow-lg);
        }}
        .topic-icon {{
            font-size: 52px;
            flex-shrink: 0;
        }}
        .topic-number {{
            display: block;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.7;
            margin-bottom: 4px;
        }}
        .topic-title {{
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.3px;
            line-height: 1.3;
        }}
        
        /* ===== CONTENT CARDS ===== */
        .content-card {{
            background: white;
            border-radius: var(--radius-md);
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
            overflow: hidden;
            border-left: 5px solid;
            transition: box-shadow 0.2s;
        }}
        .content-card:hover {{ box-shadow: var(--shadow-md); }}
        
        .card-label {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: white;
            border-radius: 0 0 var(--radius-sm) 0;
        }}
        .card-icon {{ font-size: 13px; }}
        .card-title {{
            padding: 16px 24px 8px;
            font-size: 18px;
            font-weight: 700;
        }}
        .card-body {{
            padding: 8px 24px 24px;
        }}
        
        /* Card type styles */
        .explanation-card {{ border-color: var(--color-explanation); }}
        .explanation-card .card-label {{ background: var(--color-explanation); }}
        .explanation-card .card-title {{ color: var(--color-explanation); }}
        
        .purpose-card {{ border-color: var(--color-purpose); }}
        .purpose-card .card-label {{ background: var(--color-purpose); }}
        .purpose-card .card-title {{ color: var(--color-purpose); }}
        
        .structure-card {{ border-color: var(--color-structure); }}
        .structure-card .card-label {{ background: var(--color-structure); }}
        .structure-card .card-title {{ color: var(--color-structure); }}
        
        .usage-card {{ border-color: var(--color-usage); }}
        .usage-card .card-label {{ background: var(--color-usage); }}
        .usage-card .card-title {{ color: var(--color-usage); }}
        
        .examples-card {{ border-color: var(--color-examples); }}
        .examples-card .card-label {{ background: var(--color-examples); }}
        .examples-card .card-title {{ color: var(--color-examples); }}
        
        .mistakes-card {{ border-color: var(--color-mistakes); }}
        .mistakes-card .card-label {{ background: var(--color-mistakes); }}
        .mistakes-card .card-title {{ color: var(--color-mistakes); }}
        
        .exercises-card {{ border-color: var(--color-exercises); }}
        .exercises-card .card-label {{ background: var(--color-exercises); }}
        .exercises-card .card-title {{ color: var(--color-exercises); }}
        
        .teacher-card {{ border-color: var(--color-teacher); }}
        .teacher-card .card-label {{ background: var(--color-teacher); }}
        .teacher-card .card-title {{ color: var(--color-teacher); }}
        
        .content-card .card-body .content-card {{ border-left-width: 3px; }}
        
        /* ===== CONTENT LINES ===== */
        .content-line {{
            padding: 6px 0;
            font-size: 15px;
            line-height: 1.7;
        }}
        .en-text {{ color: #1a237e; }}
        .es-text {{ color: #37474f; }}
        .lang-flag {{
            display: inline-block;
            width: 18px;
            height: 12px;
            margin-right: 8px;
            border-radius: 3px;
            vertical-align: -2px;
            overflow: hidden;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            box-shadow: 0 0 0 1px rgba(28, 30, 90, 0.14), 0 0 10px rgba(44, 229, 30, 0.12);
        }}
        .lang-flag-us {{ background-image: url('flag-us.svg'); }}
        .lang-flag-mx {{ background-image: url('flag-mx.svg'); }}
        
        .pronunciation-line {{
            padding: 4px 12px;
            margin: 4px 0 8px;
            background: #fafafa;
            border-radius: 6px;
            font-size: 13px;
            color: #666;
            border: 1px solid #f0f0f0;
        }}
        
        .option-line {{
            padding: 4px 16px;
            font-size: 14px;
        }}
        
        .subsection-header {{
            font-size: 16px;
            font-weight: 700;
            margin: 20px 0 10px;
            padding-bottom: 6px;
            border-bottom: 2px solid #e8e8e8;
            color: #333;
        }}
        
        .section-divider {{
            border: none;
            border-top: 1px solid #eee;
            margin: 16px 0;
        }}
        
        /* ===== AUDIO BUTTONS ===== */
        .audio-controls {{
            display: inline-flex;
            gap: 8px;
            margin: 6px 0 12px 28px;
        }}
        
        .audio-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border: none;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
        }}
        .audio-normal {{
            background: var(--color-examples-bg);
            color: var(--color-examples);
            border: 1px solid rgba(46,125,50,0.2);
        }}
        .audio-normal:hover {{
            background: var(--color-examples);
            color: white;
        }}
        .audio-slow {{
            background: #FFF3E0;
            color: #E65100;
            border: 1px solid rgba(230,81,0,0.2);
        }}
        .audio-slow:hover {{
            background: #E65100;
            color: white;
        }}
        .audio-btn.speaking {{
            animation: pulse 1s infinite;
        }}
        .audio-btn.error {{
            background: #FFEBEE;
            color: #C62828;
        }}
        .audio-icon {{ font-size: 14px; }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.6; }}
        }}
        
        /* ===== TOPIC NAV BOTTOM ===== */
        .topic-nav-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 32px;
            padding: 24px 0;
            border-top: 2px solid #e0e0e0;
        }}
        
        .nav-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: var(--radius-sm);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
        }}
        .prev-btn, .next-btn {{
            background: var(--ifr-primary);
            color: white;
        }}
        .prev-btn:hover, .next-btn:hover {{
            background: var(--ifr-medium);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        .index-btn {{
            background: var(--ifr-light-bg);
            color: var(--ifr-primary);
            border: 2px solid var(--ifr-primary);
        }}
        .index-btn:hover {{
            background: var(--ifr-primary);
            color: white;
        }}
        
        /* ===== QUICK FILTER BUTTONS ===== */
        .quick-filters {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 32px;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #ddd;
            border-radius: 24px;
            background: white;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'Inter', sans-serif;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .filter-btn:hover, .filter-btn.active {{
            border-color: var(--ifr-green);
            background: var(--ifr-green);
            color: var(--ifr-dark);
        }}
        
        /* ===== SCROLL TO TOP ===== */
        .scroll-top {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: var(--ifr-primary);
            color: white;
            border: none;
            font-size: 20px;
            cursor: pointer;
            box-shadow: var(--shadow-md);
            display: none;
            z-index: 500;
            transition: all 0.2s;
        }}
        .scroll-top:hover {{
            background: var(--ifr-medium);
            transform: translateY(-3px);
        }}
        .scroll-top.show {{ display: block; }}
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {{
            .sidebar {{ transform: translateX(-100%); }}
            .sidebar.open {{ transform: translateX(0); box-shadow: var(--shadow-lg); }}
            .main-content {{ margin-left: 0; padding: 16px; }}
            .header-hamburger {{ display: block; }}
            .header-search input {{ width: 160px; }}
            .header-search input:focus {{ width: 200px; }}
            .topic-header {{ padding: 20px; flex-direction: column; text-align: center; gap: 12px; }}
            .topic-title {{ font-size: 20px; }}
            .card-body {{ padding: 8px 16px 16px; }}
            .card-title {{ padding: 12px 16px 6px; font-size: 16px; }}
            .home-hero h1 {{ font-size: 24px; }}
            .home-grid {{ grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }}
            .topic-nav-bottom {{ flex-direction: column; gap: 10px; }}
            .audio-controls {{ margin-left: 0; }}
            .sidebar-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 899; }}
            .sidebar-overlay.show {{ display: block; }}
        }}
        
        /* Smooth transitions */
        .fade-in {{ animation: fadeIn 0.3s ease-in; }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <!-- TOP HEADER -->
    <header class="top-header">
        <button class="header-hamburger" onclick="toggleSidebar()" aria-label="Menú">☰</button>
        <div class="header-logo">
            <span>IFR</span>
            <span class="logo-accent">Inglés</span>
            <span style="opacity:0.7; font-weight:400; font-size:14px;">Material de Clase</span>
        </div>
        <div class="header-search">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" placeholder="Buscar tema o contenido…" oninput="handleSearch(this.value)" onfocus="handleSearch(this.value)" autocomplete="off">
            <div class="search-results" id="searchResults"></div>
        </div>
    </header>
    
    <!-- SIDEBAR OVERLAY (mobile) -->
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>
    
    <!-- SIDEBAR -->
    <nav class="sidebar" id="sidebar">
        <div class="sidebar-progress">
            <div class="progress-label">Progreso</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">0 / 17 temas visitados</div>
        </div>
        <div class="sidebar-title">Temas</div>
        <ul class="sidebar-list">
            {sidebar_items}
        </ul>
    </nav>
    
    <!-- MAIN CONTENT -->
    <main class="main-content" id="mainContent">
        <!-- HOME PAGE -->
        <div class="home-page" id="homePage">
            <div class="home-hero">
                <h1>Material de Clase — <span class="hero-accent">Inglés Diagnóstico</span></h1>
                <p>Plataforma de consulta y apoyo docente para bachillerato. 17 temas organizados desde saludos y expresiones básicas hasta Zero Conditional.</p>
            </div>
            
            <div class="quick-filters">
                <button class="filter-btn" onclick="filterTopics('all')">📋 Todos</button>
                <button class="filter-btn" onclick="filterTopics('grammar')">🧩 Gramática</button>
                <button class="filter-btn" onclick="filterTopics('vocab')">📚 Vocabulario</button>
                <button class="filter-btn" onclick="filterTopics('verbs')">⏰ Verbos</button>
            </div>
            
            <div class="home-grid" id="homeGrid">
                {home_cards}
            </div>
        </div>
        
        <!-- TOPIC PAGES -->
        {all_topic_pages}
    </main>
    
    <!-- SCROLL TO TOP -->
    <button class="scroll-top" id="scrollTop" onclick="scrollToTop()">↑</button>
    
    <script>
        // ===== STATE =====
        let currentTopic = null;
        const visitedTopics = new Set();
        const searchData = {search_json};
        
        // ===== NAVIGATION =====
        function navigateTopic(id) {{
            if (id < 1 || id > 17) return;
            
            // Hide all
            document.getElementById('homePage').style.display = 'none';
            document.querySelectorAll('.topic-page').forEach(p => p.style.display = 'none');
            
            // Show target
            const target = document.getElementById('topic-' + id);
            if (target) {{
                target.style.display = 'block';
                target.classList.add('fade-in');
                setTimeout(() => target.classList.remove('fade-in'), 300);
            }}
            
            // Update sidebar
            document.querySelectorAll('.sidebar-item').forEach(item => item.classList.remove('active'));
            const sidebarItem = document.getElementById('sidebar-item-' + id);
            if (sidebarItem) {{
                sidebarItem.classList.add('active');
                sidebarItem.scrollIntoView({{ block: 'nearest' }});
            }}
            
            currentTopic = id;
            visitedTopics.add(id);
            updateProgress();
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {{
                closeSidebar();
            }}
            
            // Scroll to top
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function showHome() {{
            document.querySelectorAll('.topic-page').forEach(p => p.style.display = 'none');
            document.getElementById('homePage').style.display = 'block';
            document.querySelectorAll('.sidebar-item').forEach(item => item.classList.remove('active'));
            currentTopic = null;
            if (window.innerWidth <= 768) closeSidebar();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function updateProgress() {{
            const pct = Math.round((visitedTopics.size / 17) * 100);
            document.getElementById('progressFill').style.width = pct + '%';
            document.getElementById('progressText').textContent = visitedTopics.size + ' / 17 temas visitados';
        }}
        
        // ===== SIDEBAR =====
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
        }}
        
        function closeSidebar() {{
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('sidebarOverlay').classList.remove('show');
        }}
        
        // ===== SEARCH =====
        function handleSearch(query) {{
            const results = document.getElementById('searchResults');
            if (!query || query.length < 2) {{
                results.classList.remove('show');
                return;
            }}
            
            const q = query.toLowerCase();
            const matches = searchData.filter(t => t.keywords.includes(q) || t.title.toLowerCase().includes(q));
            
            if (matches.length === 0) {{
                results.innerHTML = '<div class="search-result-item" style="color:#999">No se encontraron resultados</div>';
            }} else {{
                results.innerHTML = matches.map(m => 
                    `<div class="search-result-item" onclick="navigateTopic(${{m.id}}); document.getElementById('searchResults').classList.remove('show'); document.getElementById('searchInput').value='';">` +
                    `<span class="search-result-num">Tema ${{m.id}}</span>${{m.title}}</div>`
                ).join('');
            }}
            results.classList.add('show');
        }}
        
        // Close search on click outside
        document.addEventListener('click', e => {{
            if (!e.target.closest('.header-search')) {{
                document.getElementById('searchResults').classList.remove('show');
            }}
        }});
        
        // ===== FILTER =====
        function filterTopics(cat) {{
            const cards = document.querySelectorAll('.home-card');
            const grammar = [5,6,8,9,10,11];
            const vocab = [1,2,3,4,7];
            const verbs = [10,11,12,13,14,15,16,17];
            
            cards.forEach((card, i) => {{
                const id = i + 1;
                let show = true;
                if (cat === 'grammar') show = grammar.includes(id);
                else if (cat === 'vocab') show = vocab.includes(id);
                else if (cat === 'verbs') show = verbs.includes(id);
                card.style.display = show ? '' : 'none';
            }});
            
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }}
        
        // ===== AUDIO / TTS =====
        let currentUtterance = null;
        
        function speakText(text, rate, btn) {{
            // Cancel any current speech
            if (window.speechSynthesis.speaking) {{
                window.speechSynthesis.cancel();
            }}
            
            // Reset all buttons
            document.querySelectorAll('.audio-btn').forEach(b => {{
                b.classList.remove('speaking', 'error');
            }});
            
            if (!window.speechSynthesis) {{
                btn.classList.add('error');
                btn.innerHTML = '<span class="audio-icon">❌</span> No disponible';
                setTimeout(() => {{
                    btn.classList.remove('error');
                    btn.innerHTML = rate === 1 ? '<span class="audio-icon">▶</span> Normal' : '<span class="audio-icon">🐢</span> Lento 0.5×';
                }}, 2000);
                return;
            }}
            
            // Decode HTML entities
            const div = document.createElement('div');
            div.innerHTML = text;
            const cleanText = div.textContent || div.innerText;
            
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.lang = 'en-US';
            utterance.rate = rate;
            utterance.pitch = 1.0;
            
            // Try to find a US English female voice
            const voices = window.speechSynthesis.getVoices();
            const femaleVoice = voices.find(v => 
                v.lang.startsWith('en') && 
                (v.name.toLowerCase().includes('female') || 
                 v.name.toLowerCase().includes('samantha') ||
                 v.name.toLowerCase().includes('zira') ||
                 v.name.toLowerCase().includes('karen') ||
                 v.name.toLowerCase().includes('victoria') ||
                 v.name.toLowerCase().includes('google us english'))
            ) || voices.find(v => v.lang.startsWith('en-US')) || voices.find(v => v.lang.startsWith('en'));
            
            if (femaleVoice) utterance.voice = femaleVoice;
            
            btn.classList.add('speaking');
            
            utterance.onend = () => {{
                btn.classList.remove('speaking');
            }};
            
            utterance.onerror = (e) => {{
                btn.classList.remove('speaking');
                if (e.error !== 'canceled') {{
                    btn.classList.add('error');
                    setTimeout(() => btn.classList.remove('error'), 2000);
                }}
            }};
            
            window.speechSynthesis.speak(utterance);
        }}
        
        // Load voices
        if (window.speechSynthesis) {{
            speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
            speechSynthesis.getVoices();
        }}
        
        // ===== SCROLL TO TOP =====
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        window.addEventListener('scroll', () => {{
            const btn = document.getElementById('scrollTop');
            if (window.scrollY > 400) {{
                btn.classList.add('show');
            }} else {{
                btn.classList.remove('show');
            }}
        }});
        
        // ===== KEYBOARD SHORTCUTS =====
        document.addEventListener('keydown', e => {{
            if (e.target.tagName === 'INPUT') return;
            if (e.key === 'ArrowLeft' && currentTopic && currentTopic > 1) {{
                navigateTopic(currentTopic - 1);
            }} else if (e.key === 'ArrowRight' && currentTopic && currentTopic < 17) {{
                navigateTopic(currentTopic + 1);
            }} else if (e.key === 'Escape') {{
                showHome();
            }}
        }});
        
        // ===== INIT =====
        updateProgress();
    </script>
</body>
</html>'''
    
    return html


def main():
    print("Reading source file...")
    text = read_source()
    print(f"Source file read: {len(text)} characters")
    
    print("Splitting into topics...")
    topics = split_topics(text)
    print(f"Found {len(topics)} topics")
    
    for t in topics:
        sections = split_sections(t['raw'])
        title = clean_title(t['title'])
        print(f"  Topic {t['id']}: {title} ({len(sections)} sections)")
    
    print("Generating HTML...")
    html = generate_full_html(topics)
    
    print(f"Writing output ({len(html)} chars)...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Done! Output: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
