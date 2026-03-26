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
FAVICON_FILE = "school-shield.jpg"
DEFAULT_TITLE = "IFR · Inglés diagnóstico para bachillerato"
DEFAULT_DESCRIPTION = "Material académico IFR para inglés diagnóstico de bachillerato con lectura bilingüe, ejemplos guiados y ejercicios de apoyo."
TOPIC_LABELS = [
    {"id": 1, "en": "Greetings and Basic Expressions", "es": "Saludos y expresiones básicas"},
    {"id": 2, "en": "The English Alphabet", "es": "El alfabeto en inglés"},
    {"id": 3, "en": "Vowels, Consonants, and Basic Pronunciation", "es": "Vocales, consonantes y pronunciación básica"},
    {"id": 4, "en": "Numbers", "es": "Números"},
    {"id": 5, "en": "Personal Pronouns", "es": "Pronombres personales"},
    {"id": 6, "en": 'Verb "to be" in the Present', "es": "Verbo «to be» en presente"},
    {"id": 7, "en": "Introducing Yourself in English", "es": "Presentarse en inglés"},
    {"id": 8, "en": "Singular and Plural Nouns", "es": "Sustantivos en singular y plural"},
    {"id": 9, "en": "Infinitives and Gerunds", "es": "Infinitivos y gerundios"},
    {"id": 10, "en": "Simple Present", "es": "Presente simple"},
    {"id": 11, "en": 'Auxiliaries "do" and "does"', "es": "Auxiliares «do» y «does»"},
    {"id": 12, "en": 'Simple Past with "to be"', "es": "Pasado simple con «to be»"},
    {"id": 13, "en": "Simple Past with Other Verbs", "es": "Pasado simple con otros verbos"},
    {"id": 14, "en": "Basic Future", "es": "Futuro básico"},
    {"id": 15, "en": "Present Continuous for Future", "es": "Presente continuo para futuro"},
    {"id": 16, "en": "Present vs. Past vs. Future", "es": "Presente vs. pasado vs. futuro"},
    {"id": 17, "en": "Zero Conditional", "es": "Condicional cero"},
]

DESIGN_UPGRADE_CSS = r"""
        /* ===== IFR DESIGN UPGRADE ===== */
        :root {
            --surface-0: #f6f8ff;
            --surface-1: rgba(255, 255, 255, 0.96);
            --surface-2: rgba(244, 247, 255, 0.98);
            --ink-strong: #152033;
            --ink-soft: #5c667d;
            --green-glow-soft: rgba(44, 229, 30, 0.12);
            --green-glow-mid: rgba(44, 229, 30, 0.18);
            --green-glow-strong: rgba(44, 229, 30, 0.3);
        }

        body {
            background:
                radial-gradient(circle at top right, rgba(44, 229, 30, 0.08), transparent 24%),
                radial-gradient(circle at left 15%, rgba(43, 47, 143, 0.12), transparent 22%),
                linear-gradient(180deg, #eef2ff 0%, #f8faff 42%, #eef3fb 100%);
            color: var(--ink-strong);
        }

        .top-header {
            height: 78px;
            padding: 0 22px;
            background:
                linear-gradient(135deg, rgba(20, 20, 58, 0.98) 0%, rgba(28, 30, 90, 0.98) 46%, rgba(43, 47, 143, 0.98) 100%);
            border-bottom: 1px solid rgba(44, 229, 30, 0.14);
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.18);
        }

        .header-hamburger {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.12);
            color: #fff;
        }

        .header-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            text-align: left;
            color: inherit;
            background: transparent;
            border: 0;
            padding: 0;
            appearance: none;
            font: inherit;
        }

        .header-shield {
            width: 48px;
            height: 48px;
            object-fit: contain;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.96);
            padding: 5px;
            box-shadow:
                0 0 0 1px rgba(44, 229, 30, 0.22),
                0 10px 24px rgba(0, 0, 0, 0.18),
                0 0 18px rgba(44, 229, 30, 0.16);
            flex-shrink: 0;
        }

        .search-result-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }

        .search-result-num {
            flex-shrink: 0;
            margin-top: 2px;
            margin-right: 0;
        }

        .search-result-body {
            min-width: 0;
            flex: 1;
        }

        .card-label {
            color: var(--ifr-white);
        }

        .card-label .card-icon {
            color: inherit;
        }

        .sidebar-item {
            align-items: flex-start;
        }

        .sidebar-text {
            display: block;
            min-width: 0;
            flex: 1;
        }

        .topic-name-group {
            display: block;
            min-width: 0;
        }

        .topic-name-line {
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 0;
        }

        .topic-name-line + .topic-name-line {
            margin-top: 4px;
        }

        .topic-name-line .lang-flag {
            margin-right: 0;
            flex-shrink: 0;
        }

        .topic-name-label {
            display: block;
            min-width: 0;
        }

        .sidebar-text .topic-name-line,
        .search-result-body .topic-name-line {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-text .topic-name-label,
        .search-result-body .topic-name-label {
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-text .topic-name-line-es,
        .home-card-title .topic-name-line-es,
        .search-result-body .topic-name-line-es {
            opacity: 0.82;
            font-weight: 500;
        }

        .home-card-title .topic-name-line {
            justify-content: center;
        }

        .topic-title .topic-name-line + .topic-name-line {
            margin-top: 6px;
        }

        .topic-title .topic-name-line-es {
            opacity: 0.9;
            font-size: 0.82em;
            font-weight: 700;
        }

        body,
        .header-search input,
        .filter-btn,
        .nav-btn,
        .audio-btn {
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        h1, h2, h3, h4,
        .home-card-title,
        .topic-title,
        .card-title,
        .header-brand-title {
            font-family: 'Montserrat', 'Nunito', sans-serif;
        }

        .header-brand {
            display: grid;
            gap: 2px;
        }

        .header-brand-kicker {
            font-size: 0.74rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            opacity: 0.76;
        }

        .header-brand-title {
            font-size: 1.05rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .header-brand-subtitle {
            font-size: 0.8rem;
            opacity: 0.82;
        }

        .header-search input {
            width: 280px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.18);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }

        .header-search input::placeholder {
            color: rgba(255, 255, 255, 0.68);
        }

        .header-search input:focus {
            background: rgba(255, 255, 255, 0.18);
            border-color: rgba(44, 229, 30, 0.72);
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.16), 0 0 18px rgba(44, 229, 30, 0.12);
        }

        .search-results {
            border-radius: 18px;
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
            max-height: 320px;
            overflow: auto;
        }

        .search-result-item {
            width: 100%;
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 12px 14px;
        }

        .sidebar {
            top: 78px;
            height: calc(100vh - 78px);
            background: rgba(255, 255, 255, 0.84);
            backdrop-filter: blur(16px);
            border-right: 1px solid rgba(28, 30, 90, 0.12);
            box-shadow: 10px 0 30px rgba(15, 23, 42, 0.04);
        }

        .main-content {
            margin-top: 78px;
            padding-inline: 28px;
            padding-block: 30px;
        }

        .sidebar-progress {
            margin: 16px 14px 14px;
            padding: 14px;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(248, 250, 255, 0.98), rgba(240, 243, 250, 0.98));
            border: 1px solid rgba(28, 30, 90, 0.08);
        }

        .progress-head {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 10px;
        }

        .progress-label {
            color: #2b2f8f;
            letter-spacing: 0.14em;
            margin-bottom: 0;
        }

        .progress-text {
            color: var(--ink-soft);
            margin-top: 0;
        }

        .progress-bar {
            background: rgba(28, 30, 90, 0.08);
        }

        .progress-fill {
            background: linear-gradient(90deg, #2ce51e, #7cf26f);
            box-shadow: 0 0 16px rgba(44, 229, 30, 0.24);
        }

        .sidebar-title {
            margin: 12px 6px 10px;
            color: var(--ink-soft);
        }

        .sidebar-list {
            padding: 0 8px 24px;
        }

        .sidebar-item {
            width: 100%;
            padding: 0.84rem 0.9rem;
            border-radius: 16px;
            transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
        }

        .sidebar-item:hover {
            background: rgba(28, 30, 90, 0.05);
            transform: translateY(-1px);
        }

        .sidebar-item.active {
            background: linear-gradient(135deg, #14143a, #1c1e5a);
            color: #fff;
            box-shadow:
                0 0 0 1px rgba(44, 229, 30, 0.26),
                0 0 22px rgba(44, 229, 30, 0.18),
                0 12px 30px rgba(15, 23, 42, 0.12);
        }

        .sidebar-number {
            min-width: 2.2rem;
            height: 2.2rem;
            border-radius: 999px;
            background: rgba(28, 30, 90, 0.08);
            color: #1c1e5a;
            font-size: 0.8rem;
            font-weight: 800;
            display: grid;
            place-items: center;
        }

        .sidebar-item.active .sidebar-number {
            background: rgba(44, 229, 30, 0.18);
            color: #fff;
        }

        .home-page {
            max-width: 1180px;
        }

        .home-hero {
            position: relative;
            overflow: hidden;
            padding: 34px 32px;
            text-align: left;
            background:
                radial-gradient(circle at top right, rgba(44, 229, 30, 0.16), transparent 26%),
                linear-gradient(135deg, rgba(20, 20, 58, 0.98), rgba(28, 30, 90, 0.96) 52%, rgba(43, 47, 143, 0.94));
            border: 1px solid rgba(44, 229, 30, 0.12);
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.1);
        }

        .home-hero::after {
            content: "";
            position: absolute;
            inset: auto -40px -50px auto;
            width: 180px;
            height: 180px;
            background: radial-gradient(circle, rgba(44, 229, 30, 0.24), transparent 60%);
            pointer-events: none;
        }

        .home-hero h1 {
            margin-bottom: 14px;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.04;
            letter-spacing: -0.04em;
        }

        .home-hero .hero-accent {
            color: #b8ffb2;
            text-shadow: 0 0 16px rgba(44, 229, 30, 0.3);
        }

        .home-hero p {
            max-width: 760px;
            color: rgba(255, 255, 255, 0.84);
        }

        .quick-filters {
            margin: 16px 0 22px;
        }

        .filter-btn {
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(28, 30, 90, 0.12);
            color: var(--ink-soft);
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.05), 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .filter-btn:hover {
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.22), 0 0 16px rgba(44, 229, 30, 0.14);
        }

        .filter-btn.active {
            background: rgba(44, 229, 30, 0.14);
            border-color: rgba(44, 229, 30, 0.56);
            color: #152033;
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.28), 0 0 18px rgba(44, 229, 30, 0.16);
        }

        .home-grid {
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }

        .home-card {
            position: relative;
            display: grid;
            align-content: start;
            min-height: 174px;
            padding: 18px;
            text-align: left;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(28, 30, 90, 0.1);
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.08), 0 1px 2px rgba(15, 23, 42, 0.06);
            gap: 14px;
            transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease, filter 0.24s ease;
        }

        .home-card::before {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: linear-gradient(180deg, rgba(44, 229, 30, 0.06), transparent 28%);
            opacity: 0;
            transition: opacity 0.24s ease;
            pointer-events: none;
        }

        .home-card:hover {
            transform: translateY(-4px);
            border-color: rgba(44, 229, 30, 0.54);
            box-shadow:
                0 0 0 1px rgba(44, 229, 30, 0.22),
                0 0 24px rgba(44, 229, 30, 0.18),
                0 12px 30px rgba(15, 23, 42, 0.08);
            filter: saturate(1.03);
        }

        .home-card:hover::before {
            opacity: 1;
        }

        .home-card-icon {
            font-size: 1.6rem;
            margin-bottom: 0;
        }

        .home-card-number {
            display: inline-flex;
            width: fit-content;
            padding: 0.34rem 0.62rem;
            border-radius: 999px;
            background: rgba(28, 30, 90, 0.08);
            color: #1c1e5a;
            letter-spacing: 0.08em;
        }

        .home-card-title {
            font-size: 1rem;
            line-height: 1.36;
            color: var(--ink-strong);
        }

        .topic-page {
            max-width: 980px;
        }

        .topic-header {
            padding: 24px;
            gap: 20px;
            align-items: center;
            background: rgba(255, 255, 255, 0.98);
            border: 1px solid rgba(28, 30, 90, 0.12);
            border-radius: 24px;
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.1);
            color: var(--ink-strong);
        }

        .topic-header-text {
            display: grid;
            gap: 8px;
        }

        .topic-icon {
            font-size: 2rem;
        }

        .topic-number {
            color: var(--ink-soft);
            opacity: 1;
            margin-bottom: 0;
        }

        .topic-title {
            color: #1c1e5a;
        }

        .topic-content {
            margin-top: 20px;
        }

        .content-card {
            position: relative;
            overflow: hidden;
            --card-accent: #1c1e5a;
            border-radius: 22px;
            border: 1px solid rgba(28, 30, 90, 0.12);
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.08), 0 1px 2px rgba(15, 23, 42, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .content-card::before {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 100%;
            height: 6px;
            background: var(--card-accent);
        }

        .content-card:hover {
            transform: translateY(-2px);
            box-shadow:
                0 0 0 1px rgba(44, 229, 30, 0.18),
                0 0 22px rgba(44, 229, 30, 0.12),
                0 12px 30px rgba(15, 23, 42, 0.08);
        }

        .explanation-card { --card-accent: #1c1e5a; }
        .purpose-card { --card-accent: #2b2f8f; }
        .structure-card { --card-accent: #1565c0; }
        .usage-card { --card-accent: #00695c; }
        .examples-card { --card-accent: #2e7d32; }
        .mistakes-card { --card-accent: #bf360c; }
        .exercises-card { --card-accent: #e65100; }
        .teacher-card { --card-accent: #6a1b9a; }

        .card-label {
            position: relative;
            margin-left: 18px;
            margin-top: 18px;
            border-radius: 999px;
            background: color-mix(in srgb, var(--card-accent) 12%, white);
            color: var(--ifr-white);
        }

        .card-label .card-icon {
            color: inherit;
        }

        .card-title {
            padding-top: 14px;
            color: var(--ink-strong);
        }

        .card-body {
            padding-top: 10px;
        }

        .content-line {
            padding: 8px 0;
        }

        .lang-flag {
            width: 1.4rem;
        }

        .pronunciation-line {
            padding: 0.72rem 0.9rem;
            border-radius: 16px;
            border-left: 4px solid #2ce51e;
            background: rgba(28, 30, 90, 0.03);
            color: var(--ink-soft);
        }

        .option-line {
            padding: 0.6rem 0.9rem;
            border-radius: 14px;
            border: 1px solid rgba(28, 30, 90, 0.08);
            background: rgba(255, 255, 255, 0.96);
            margin: 6px 0;
        }

        .subsection-header {
            margin-top: 24px;
            padding: 10px 12px;
            border-radius: 14px;
            border-bottom: 0;
            background: rgba(28, 30, 90, 0.04);
            color: #1c1e5a;
        }

        .audio-controls {
            gap: 8px;
            margin: 10px 0 12px;
        }

        .audio-btn {
            padding: 0.5rem 0.82rem;
            border-radius: 999px;
            border: 1px solid rgba(28, 30, 90, 0.12);
            background: rgba(255, 255, 255, 0.96);
            color: #1c1e5a;
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
        }

        .audio-normal {
            background: rgba(44, 229, 30, 0.12);
            border-color: rgba(44, 229, 30, 0.32);
            color: #14143a;
        }

        .audio-normal:hover {
            background: #2ce51e;
            color: #14143a;
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.34), 0 0 18px rgba(44, 229, 30, 0.22);
        }

        .audio-slow:hover {
            background: #1c1e5a;
            color: #fff;
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.18), 0 0 18px rgba(44, 229, 30, 0.16);
        }

        .topic-nav-bottom {
            gap: 12px;
            border-top: 1px solid rgba(28, 30, 90, 0.12);
            padding-top: 18px;
            margin-top: 24px;
        }

        .nav-btn {
            border-radius: 999px;
            border: 1px solid rgba(28, 30, 90, 0.14);
            background: rgba(255, 255, 255, 0.96);
            color: #1c1e5a;
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
        }

        .prev-btn,
        .next-btn {
            background: linear-gradient(135deg, #14143a, #1c1e5a);
            color: #fff;
            border-color: transparent;
        }

        .index-btn {
            background: rgba(44, 229, 30, 0.12);
            border-color: rgba(44, 229, 30, 0.3);
            color: #14143a;
        }

        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow:
                0 0 0 1px rgba(44, 229, 30, 0.22),
                0 0 18px rgba(44, 229, 30, 0.16),
                0 10px 24px rgba(15, 23, 42, 0.08);
        }

        .scroll-top {
            width: 46px;
            height: 46px;
            border-radius: 999px;
            background: linear-gradient(135deg, #14143a, #1c1e5a);
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
        }

        .scroll-top:hover {
            box-shadow: 0 0 0 1px rgba(44, 229, 30, 0.18), 0 0 18px rgba(44, 229, 30, 0.16), 0 18px 48px rgba(15, 23, 42, 0.12);
        }

        @media (max-width: 960px) {
            .sidebar {
                box-shadow: 0 18px 48px rgba(15, 23, 42, 0.14);
            }

            .main-content {
                margin-left: 0;
                padding-inline: 16px;
            }

            .header-search input {
                width: 180px;
            }

            .header-search input:focus {
                width: 220px;
            }
        }

        @media (max-width: 768px) {
            .top-header {
                padding-inline: 14px;
            }

            .header-shield {
                width: 42px;
                height: 42px;
            }

            .header-brand-kicker {
                font-size: 0.66rem;
            }

            .header-brand-title {
                font-size: 0.95rem;
            }

            .header-brand-subtitle {
                font-size: 0.72rem;
            }

            .header-search {
                display: none;
            }

            .home-hero {
                padding: 24px;
            }

            .topic-header {
                align-items: start;
                text-align: left;
            }

            .topic-nav-bottom {
                flex-direction: column;
            }

            .nav-btn {
                width: 100%;
            }
        }
"""

def apply_design_upgrade(html):
    """Apply the IFR redesign and UX fixes after generating the base HTML."""
    replacements = [
        (
            "<title>IFR — Material de Clase: Inglés Diagnóstico Bachillerato</title>",
            f"<title>{DEFAULT_TITLE}</title>\n    <meta name=\"description\" content=\"{DEFAULT_DESCRIPTION}\">\n    <meta name=\"theme-color\" content=\"#1C1E5A\">\n    <link rel=\"icon\" type=\"image/jpeg\" href=\"{FAVICON_FILE}\">\n    <link rel=\"apple-touch-icon\" href=\"{FAVICON_FILE}\">"
        ),
        (
            "<meta name=\"description\" content=\"Plataforma educativa IFR para material de clase y consulta de inglés diagnóstico para bachillerato. 17 temas desde saludos básicos hasta Zero Conditional.\">",
            ""
        ),
        (
            """<div class="header-logo">
            <span>IFR</span>
            <span class="logo-accent">Inglés</span>
            <span style="opacity:0.7; font-weight:400; font-size:14px;">Material de Clase</span>
        </div>""",
            f"""<button class="header-logo" onclick="showHome()" aria-label="Volver al inicio">
            <img class="header-shield" src="ifr-shield.svg" alt="Escudo del IFR" data-official-shield="{SHIELD_URL}">
            <span class="header-brand">
                <span class="header-brand-kicker">Instituto Fernando Ramírez</span>
                <span class="header-brand-title">Inglés diagnóstico</span>
                <span class="header-brand-subtitle">Bachillerato</span>
            </span>
        </button>"""
        ),
        (
            '<span class="search-icon">🔍</span>',
            '<span class="search-icon">🔎</span>'
        ),
        (
            'placeholder="Buscar tema o contenido…" oninput="handleSearch(this.value)" onfocus="handleSearch(this.value)" autocomplete="off">',
            'placeholder="Buscar tema o bloque" oninput="handleSearch(this.value)" onfocus="handleSearch(this.value)" autocomplete="off">'
        ),
        (
            """<div class="sidebar-progress">
            <div class="progress-label">Progreso</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">0 / 17 temas visitados</div>
        </div>
        <div class="sidebar-title">Temas</div>""",
            """<div class="sidebar-progress">
            <div class="progress-head">
                <div class="progress-label">Avance</div>
                <div class="progress-text" id="progressText">0 de 17 temas revisados</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        <div class="sidebar-title">Temario</div>"""
        ),
        (
            '<h1>Material de Clase — <span class="hero-accent">Inglés Diagnóstico</span></h1>',
            '<h1>Material de clase <span class="hero-accent">Inglés diagnóstico</span></h1>'
        ),
        (
            'Plataforma de consulta y apoyo docente para bachillerato. 17 temas organizados desde saludos y expresiones básicas hasta Zero Conditional.',
            'Plataforma de consulta y apoyo docente para bachillerato. Los 17 temas se muestran con su nombre en inglés y en español para facilitar la consulta bilingüe.'
        ),
        (
            "document.getElementById('progressText').textContent = visitedTopics.size + ' / 17 temas visitados';",
            "document.getElementById('progressText').textContent = visitedTopics.size + ' de 17 temas revisados';"
        ),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    if DESIGN_UPGRADE_CSS not in html:
        html = html.replace("</style>", DESIGN_UPGRADE_CSS + "\n    </style>", 1)

    html = html.replace(
        "        // ===== SEARCH =====\n        function handleSearch(query) {{\n            const results = document.getElementById('searchResults');\n            if (!query || query.length < 2) {{\n                results.classList.remove('show');\n                return;\n            }}\n            \n            const q = query.toLowerCase();\n            const matches = searchData.filter(t => t.keywords.includes(q) || t.title.toLowerCase().includes(q));",
        """        // ===== SEARCH =====
        function normalizeSearchText(value) {{
            return (value || '')
                .toString()
                .normalize('NFD')
                .replace(/[\\u0300-\\u036f]/g, '')
                .replace(/[«»"']/g, '')
                .toLowerCase();
        }}

        function handleSearch(query) {{
            const results = document.getElementById('searchResults');
            if (!query || query.length < 2) {{
                results.classList.remove('show');
                return;
            }}
            
            const q = normalizeSearchText(query.trim());
            const matches = searchData.filter(t => {{
                const title = normalizeSearchText(t.title);
                const keywords = normalizeSearchText(t.keywords);
                return title.includes(q) || keywords.includes(q);
            }});"""
    )

    html = html.replace(
        "        // ===== INIT =====\n        applyTopicLabels();\n        updateProgress();",
        f"""        // ===== INIT =====
        applyTopicLabels();
        updateProgress();
        (async () => {{
            const shield = document.querySelector('.header-shield');
            if (!shield) return;
            const official = shield.dataset.officialShield;
            if (!official) return;
            try {{
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 3500);
                await fetch(official, {{ mode: 'no-cors', cache: 'no-store', signal: controller.signal }});
                clearTimeout(timeout);
                shield.src = official;
            }} catch (err) {{
                // Keep the local shield when the official file cannot be reached.
            }}
        }})();"""
    )

    return html

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
    # Also for Topic 1 specific sections: Explanation, Purpose, Structure, Usage
    if sec_type == 'examples' or (topic_id == 1 and sec_type in ['explanation', 'purpose', 'structure', 'usage']):
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
    
    topic_labels_json = json.dumps(TOPIC_LABELS, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IFR — Material de Clase: Inglés Diagnóstico Bachillerato</title>
    <meta name="description" content="Plataforma educativa IFR para material de clase y consulta de inglés diagnóstico para bachillerato. 17 temas desde saludos básicos hasta Zero Conditional.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet">
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
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
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
            font-family: 'Nunito', sans-serif;
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
            font-family: 'Nunito', sans-serif;
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
            font-family: 'Nunito', sans-serif;
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
            font-family: 'Nunito', sans-serif;
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
        const topicLabels = {topic_labels_json};
        const topicLabelsById = Object.fromEntries(topicLabels.map(topic => [topic.id, topic]));
        const searchData = topicLabels.map(topic => ({{
            id: topic.id,
            title: `${{topic.en}} / ${{topic.es}}`,
            keywords: `${{topic.en}} ${{topic.es}}`.toLowerCase()
        }}));

        function getTopicNameHTML(topic) {{
            return `
                <span class="topic-name-group">
                    <span class="topic-name-line topic-name-line-en">
                        <span class="lang-flag lang-flag-us" aria-hidden="true"></span>
                        <span class="topic-name-label">${{topic.en}}</span>
                    </span>
                    <span class="topic-name-line topic-name-line-es">
                        <span class="lang-flag lang-flag-mx" aria-hidden="true"></span>
                        <span class="topic-name-label">${{topic.es}}</span>
                    </span>
                </span>
            `;
        }}

        function applyTopicLabels() {{
            document.querySelectorAll('.sidebar-item').forEach((item, index) => {{
                const topic = topicLabels[index];
                const label = item.querySelector('.sidebar-text');
                if (!topic || !label) return;
                label.innerHTML = getTopicNameHTML(topic);
                item.setAttribute('aria-label', `Tema ${{topic.id}}: ${{topic.en}} / ${{topic.es}}`);
            }});

            document.querySelectorAll('.home-card').forEach((card, index) => {{
                const topic = topicLabels[index];
                const title = card.querySelector('.home-card-title');
                if (!topic || !title) return;
                title.innerHTML = getTopicNameHTML(topic);
                card.setAttribute('aria-label', `Tema ${{topic.id}}: ${{topic.en}} / ${{topic.es}}`);
            }});

            document.querySelectorAll('.topic-page').forEach(page => {{
                const id = Number(page.id.replace('topic-', ''));
                const topic = topicLabelsById[id];
                const title = page.querySelector('.topic-title');
                if (!topic || !title) return;
                title.innerHTML = getTopicNameHTML(topic);
            }});
        }}
        
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
                    `<span class="search-result-num">Tema ${{m.id}}</span>` +
                    `<span class="search-result-body">${{getTopicNameHTML(topicLabelsById[m.id])}}</span>` +
                    `</div>`
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
        applyTopicLabels();
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
        safe_title = title.encode('cp1252', errors='replace').decode('cp1252')
        print(f"  Topic {t['id']}: {safe_title} ({len(sections)} sections)")
    
    print("Generating HTML...")
    html = generate_full_html(topics)
    html = apply_design_upgrade(html)
    
    print(f"Writing output ({len(html)} chars)...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Done! Output: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
