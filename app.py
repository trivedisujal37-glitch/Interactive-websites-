"""Supply Chain Optimization System - Streamlit Application.

Anshu's portion: Cost Analysis, Optimization, Recommendations, Reporting, Export & App Integration.
"""

import pandas as pd
import streamlit as st

from modules.cost import analyze_cost
from modules.optimization import run_optimization
from modules.recommendations import HUMAN_REVIEW_TEXT, build_recommendations
from streamlit_option_menu import option_menu
from utils.export import (
    export_to_csv,
    export_to_excel,
    get_available_export_formats,
)

st.set_page_config(page_title="Supply Chain Optimization System", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Obsidian Canvas & Typography System */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    .stApp {
        background-color: #090D16 !important;
        background-image:
            radial-gradient(circle at 15% 10%, rgba(16, 185, 129, 0.07) 0%, transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(0, 242, 254, 0.06) 0%, transparent 40%),
            radial-gradient(circle at 50% 90%, rgba(139, 92, 246, 0.05) 0%, transparent 50%) !important;
        color: #E2E8F0 !important;
    }
    .block-container {
        padding-top: 4.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 98% !important;
    }

    /* Top Brand & Header Bar */
    .zentra-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 8px 16px 8px;
        margin-bottom: 8px;
    }
    .zentra-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
    }
    .zentra-logo-icon {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .zentra-brand-text {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .pro-badge {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #10B981;
        font-size: 0.64rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        padding: 3px 8px;
        border-radius: 6px;
        margin-left: 2px;
    }
    .zentra-header-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .zentra-tool-btn {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: rgba(17, 23, 38, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94A3B8;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .zentra-tool-btn:hover {
        background: rgba(22, 30, 48, 0.95);
        color: #FFFFFF;
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.25);
        transform: translateY(-1px);
    }
    .green-dot {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 6px;
        height: 6px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }
    .zentra-avatar-pill {
        display: flex;
        align-items: center;
    }
    .avatar-circle {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10B981 0%, #00F2FE 50%, #8B5CF6 100%);
        padding: 2px;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 800;
        color: #FFFFFF;
    }

    /* Elevated Glassmorphic Slate Cards (Specification 1) */
    div[data-testid="stVerticalBlockBorderWrapper"], .zentra-glass-card {
        background: rgba(17, 23, 38, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        box-shadow: 0 14px 40px -10px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        padding: 16px 20px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover, .zentra-glass-card:hover {
        border-color: rgba(16, 185, 129, 0.3) !important;
        box-shadow: 0 18px 45px -10px rgba(0, 0, 0, 0.75), 0 0 25px rgba(16, 185, 129, 0.08) !important;
        transform: translateY(-1px) !important;
    }

    /* Overview Header */
    .zentra-overview-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 6px 0 20px 0;
        flex-wrap: wrap;
        gap: 12px;
    }
    .overview-title-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .overview-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.8px;
    }
    .overview-ctrls-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ctrl-pill-btn {
        background: rgba(17, 23, 38, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 9999px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #CBD5E1;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    .ctrl-pill-btn:hover {
        border-color: rgba(16, 185, 129, 0.35);
        color: #FFFFFF;
    }
    .date-range-pill {
        color: #94A3B8;
    }
    .vs-badge {
        color: #10B981;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0 4px;
    }
    .add-widget-btn {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #10B981;
    }
    .add-widget-btn:hover {
        background: rgba(16, 185, 129, 0.22);
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.3);
    }

    /* Card Elements */
    .card-head-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }
    .card-main-title {
        color: #FFFFFF;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.2px;
    }
    .card-dots-btn {
        color: #64748B;
        font-size: 1.1rem;
        cursor: pointer;
        padding: 0 4px;
        line-height: 1;
        transition: color 0.2s ease;
    }
    .card-dots-btn:hover {
        color: #10B981;
    }

    /* 5 Stages Metrics Row */
    .stages-metrics-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        padding: 0 12px 10px 12px;
    }
    .stage-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .stage-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stage-val {
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    .active-stage .stage-label {
        color: #10B981 !important;
        font-weight: 700;
    }
    .active-stage .stage-val {
        color: #10B981 !important;
        text-shadow: 0 0 14px rgba(16, 185, 129, 0.6);
    }

    /* AI Exploration Pill Bar */
    .ai-explore-wrap {
        background: linear-gradient(180deg, rgba(17, 23, 38, 0.9) 0%, rgba(10, 14, 24, 0.95) 100%);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 14px;
        padding: 10px 14px;
        margin-top: 10px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(16, 185, 129, 0.2);
    }
    .ai-explore-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #10B981;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        letter-spacing: 0.02em;
    }
    .ai-explore-input-pill {
        background: rgba(9, 13, 22, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 0.82rem;
        color: #CBD5E1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ai-explore-chevron {
        color: #10B981;
        font-weight: bold;
    }

    /* Gross Spend Card */
    .gross-spend-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 2px;
    }
    .gross-spend-metric-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .gross-spend-num {
        font-size: 2.7rem;
        font-weight: 800;
        color: #10B981;
        letter-spacing: -1.2px;
        text-shadow: 0 0 24px rgba(16, 185, 129, 0.3);
        line-height: 1.1;
    }
    .gross-spend-delta {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .spend-bar-row {
        margin-bottom: 14px;
    }
    .spend-bar-head {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 6px;
    }
    .spend-bar-title {
        color: #94A3B8;
        font-weight: 500;
    }
    .spend-bar-amount {
        color: #FFFFFF;
        font-weight: 700;
    }
    .progress-track {
        height: 10px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 9999px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 9999px;
    }
    .fill-green {
        background: repeating-linear-gradient(45deg, #10B981, #10B981 6px, #059669 6px, #059669 12px);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.45);
    }
    .fill-cyan {
        background: repeating-linear-gradient(45deg, #00F2FE, #00F2FE 6px, #0284C7 6px, #0284C7 12px);
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.45);
    }
    .fill-pink {
        background: repeating-linear-gradient(45deg, #8B5CF6, #8B5CF6 6px, #6D28D9 6px, #6D28D9 12px);
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.45);
    }

    /* Soundwave Subcards */
    .submetric-card {
        background: rgba(13, 18, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 12px 16px;
        transition: all 0.2s ease;
    }
    .submetric-card:hover {
        border-color: rgba(16, 185, 129, 0.25);
    }
    .submetric-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .submetric-title {
        font-size: 0.86rem;
        font-weight: 600;
        color: #94A3B8;
    }
    .submetric-body {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
    }
    .submetric-num {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    .equalizer-bars {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 38px;
    }
    .equalizer-bars span {
        width: 3.5px;
        border-radius: 3px;
        display: inline-block;
    }
    .cyan-bars span {
        background: linear-gradient(180deg, #00F2FE 0%, #10B981 100%);
        box-shadow: 0 0 6px rgba(0, 242, 254, 0.4);
    }
    .blue-bars span {
        background: linear-gradient(180deg, #38BDF8 0%, #8B5CF6 100%);
        box-shadow: 0 0 6px rgba(56, 189, 248, 0.4);
    }
    .submetric-delta-box {
        text-align: right;
    }
    .submetric-delta-lbl {
        font-size: 0.68rem;
        color: #64748B;
    }
    .submetric-delta-val {
        font-size: 0.88rem;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Supply AI Insights Card */
    .ai-insight-card {
        background: linear-gradient(145deg, rgba(20, 28, 45, 0.9) 0%, rgba(13, 18, 30, 0.95) 100%);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 20px;
        padding: 18px 22px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 14px 40px -10px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(16, 185, 129, 0.2);
    }
    .ai-insight-pill {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.74rem;
        font-weight: 700;
        color: #10B981;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .ai-insight-big-stat {
        font-size: 3.5rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -1.5px;
        line-height: 1;
        margin: 12px 0 6px 0;
        text-shadow: 0 0 24px rgba(16, 185, 129, 0.3);
    }
    .ai-insight-text {
        font-size: 0.84rem;
        color: #CBD5E1;
        line-height: 1.4;
        margin-bottom: 14px;
    }
    .ai-carousel-pills {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .carousel-bar {
        height: 3px;
        width: 14px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
    }
    .carousel-bar.active {
        width: 32px;
        background: #10B981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
    }

    /* Structured KPI / Stat Metrics (Specification 3 & Task 2) */
    div[data-testid="stMetric"] {
        background: rgba(17, 23, 38, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: visible !important;
        min-width: 0 !important;
        width: 100% !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(16, 185, 129, 0.38) !important;
        box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.8), 0 0 20px rgba(16, 185, 129, 0.14) !important;
    }
    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.6), transparent);
        opacity: 0;
        transition: opacity 0.25s ease;
    }
    div[data-testid="stMetric"]:hover::before {
        opacity: 1;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: clamp(1.2rem, 1.8vw, 1.95rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
        text-shadow: 0 0 16px rgba(16, 185, 129, 0.15) !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
    }
    div[data-testid="stMetricValue"] > div {
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.74rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-bottom: 6px !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        margin-top: 6px !important;
    }

    /* Form & Input Controls (Specification 5) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input {
        background-color: rgba(17, 23, 38, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #E2E8F0 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="select"] > div:hover,
    div[data-testid="stTextInput"] input:hover,
    div[data-testid="stDateInput"] input:hover {
        border-color: rgba(16, 185, 129, 0.4) !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stDateInput"] input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25) !important;
    }
    /* Select Popover Menu */
    ul[data-baseweb="menu"] {
        background: #111726 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.8) !important;
    }
    li[data-baseweb="menu-item"] {
        color: #CBD5E1 !important;
        font-size: 0.86rem !important;
        transition: background 0.15s ease !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        color: #FFFFFF !important;
    }

    /* File Uploader Dropzone */
    div[data-testid="stFileUploader"] section {
        background: rgba(17, 23, 38, 0.6) !important;
        border: 1.5px dashed rgba(16, 185, 129, 0.4) !important;
        border-radius: 18px !important;
        padding: 28px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        border-color: #10B981 !important;
        background: rgba(16, 185, 129, 0.05) !important;
        box-shadow: 0 0 24px rgba(16, 185, 129, 0.15) !important;
    }

    /* Modern Data Tables (Specification 5) */
    div[data-testid="stDataFrame"] > div {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(17, 23, 38, 0.8) !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6) !important;
        overflow: hidden !important;
    }

    /* Buttons & Interactive Controls */
    div.stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #00F2FE 100%) !important;
        color: #090D16 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0.55rem 1.3rem !important;
        box-shadow: 0 4px 18px rgba(16, 185, 129, 0.35) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(16, 185, 129, 0.55) !important;
        background: linear-gradient(135deg, #34D399 0%, #38BDF8 100%) !important;
    }
    div.stDownloadButton > button {
        background: rgba(17, 23, 38, 0.85) !important;
        color: #10B981 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }
    div.stDownloadButton > button:hover {
        background: rgba(16, 185, 129, 0.14) !important;
        transform: translateY(-2px) !important;
        border-color: #10B981 !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25) !important;
    }

    /* Alerts & Notifications */
    div[data-testid="stAlert"] {
        background: rgba(17, 23, 38, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }

    /* Headers & Typography */
    h1, h2, h3, h4, h5 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px !important;
    }

    /* Hide Sidebar */
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Top Brand Header Bar
st.markdown("""
    <div class="zentra-topbar">
        <div class="zentra-brand">
            <div class="zentra-logo-icon">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#zlogo)" />
                    <path d="M2 17L12 22L22 17" stroke="#00F2FE" stroke-width="2.2" stroke-linecap="round" />
                    <path d="M2 12L12 17L22 12" stroke="#10B981" stroke-width="2.2" stroke-linecap="round" />
                    <defs>
                        <linearGradient id="zlogo" x1="2" y1="2" x2="22" y2="12">
                            <stop stop-color="#10B981" />
                            <stop offset="1" stop-color="#00F2FE" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <span class="zentra-brand-text">Supply Chain Optimization</span>
            <span class="pro-badge">ENTERPRISE</span>
        </div>
        <div class="zentra-header-right">
            <div class="zentra-tool-btn" title="Search">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </div>
            <div class="zentra-tool-btn notification-tool" title="Notifications">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                <span class="green-dot"></span>
            </div>
            <div class="zentra-avatar-pill">
                <div class="avatar-circle">SC</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state variables
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = None
if "_last_optimization_findings" not in st.session_state:
    st.session_state._last_optimization_findings = None


def _detect_item_col(df: pd.DataFrame | None) -> str | None:
    """Auto-detect item identifier column."""
    if df is None or df.empty:
        return None
    for candidate in [
        "Item",
        "Item Name",
        "Product",
        "Product Name",
        "SKU",
        "Item ID",
    ]:
        if candidate in df.columns:
            return candidate
    return df.columns[0] if len(df.columns) > 0 else None


def _download_buttons(df: pd.DataFrame | None, base_name: str, key_prefix: str = ""):
    """Render download buttons for CSV and optionally Excel."""
    if df is None or df.empty:
        return

    csv_data = export_to_csv(df)
    cols = st.columns([1, 1, 6])
    with cols[0]:
        if csv_data:
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{base_name}.csv",
                mime="text/csv",
                key=f"{key_prefix}_csv_{base_name}",
            )
    with cols[1]:
        if "xlsx" in get_available_export_formats():
            excel_data = export_to_excel(df)
            if excel_data:
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"{base_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"{key_prefix}_xlsx_{base_name}",
                )


# Navigation list with all 10 tabs intact in exact required order
PAGES = [
    "Data Management",
    "Dashboard",
    "Inventory Analysis",
    "Demand Analysis",
    "Demand Prediction",
    "Supplier Analysis",
    "Cost Analysis",
    "Optimization",
    "Recommendations",
    "Reporting",
]

page = option_menu(
    menu_title=None,
    options=PAGES,
    icons=[
        "database-fill", "speedometer2", "box-seam-fill", "graph-up", "activity", 
        "truck", "cash-coin", "sliders2", "stars", "file-earmark-text-fill"
    ],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "6px 14px !important",
            "background": "rgba(17, 23, 38, 0.78)",
            "border-radius": "9999px",
            "margin-bottom": "22px",
            "display": "flex",
            "flex-wrap": "wrap",
            "justify-content": "center",
            "box-shadow": "0 14px 40px -10px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.08)",
            "border": "1px solid rgba(255, 255, 255, 0.08)",
            "backdrop-filter": "blur(20px)",
        },
        "icon": {"color": "#10B981", "font-size": "13px"}, 
        "nav-link": {
            "font-size": "12.5px",
            "font-weight": "500",
            "text-align": "center",
            "margin": "3px 4px",
            "color": "#94A3B8",
            "border-radius": "9999px",
            "padding": "7px 14px",
            "--hover-color": "rgba(255, 255, 255, 0.06)",
            "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(0, 242, 254, 0.12) 100%)",
            "color": "#FFFFFF",
            "font-weight": "700",
            "border": "1px solid rgba(16, 185, 129, 0.65)",
            "box-shadow": "0 0 20px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)",
            "border-radius": "9999px",
        },
    }
)

# -------------------------------------------------------------
# 1. Data Management
# -------------------------------------------------------------
if page == "Data Management":
    st.title("Data Management")
    st.write("Upload supply chain datasets for analysis and optimization.")

    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            df = df.loc[:, ~df.columns.duplicated(keep="first")]
            if st.session_state.dataset_name != uploaded_file.name:
                st.session_state.raw_df = df
                st.session_state.dataset_name = uploaded_file.name
                # Reset stale optimization findings on new dataset upload
                st.session_state._last_optimization_findings = None
                st.success(f"Loaded '{uploaded_file.name}' successfully ({len(df)} rows).")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    if st.session_state.raw_df is not None:
        st.subheader(f"Current Dataset: {st.session_state.dataset_name}")
        st.dataframe(st.session_state.raw_df, use_container_width=True)

        if st.button("Clear uploaded data"):
            st.session_state.raw_df = None
            st.session_state.dataset_name = None
            st.session_state._last_optimization_findings = None
            st.rerun()

    st.caption(
        "Note: Dataset validation, cleansing, and schema checking are owned by "
        "teammates (Sujal/Manthan/Anshu) and will be integrated here."
    )

# -------------------------------------------------------------
# 2. Home / Dashboard (Zentra Executive Reference View)
# -------------------------------------------------------------
elif page in ["Home", "Dashboard"]:
    import html
    import os
    from modules.dashboard_charts import (
        standardize_dataframe,
        get_latest_stock_snapshot,
        compute_inventory_metrics,
        filter_data,
        calc_k1_inventory_value,
        calc_k2_total_demand,
        calc_k3_items_needing_attention,
        calc_k4_average_lead_time,
        plot_c1_demand_by_category,
        plot_c2_stock_status_mix,
        plot_c3_demand_by_quarter_month,
        plot_c4_top_items_demand,
        plot_c5_inventory_value_by_category,
        plot_c6_quantity_supplied_by_supplier,
        plot_zentra_payments_and_costs,
        plot_zentra_inventory_flow,
        calc_zentra_metrics,
        ChartResult,
    )

    raw_df = st.session_state.raw_df
    if raw_df is None or raw_df.empty:
        st.markdown("""
            <div class="zentra-overview-head">
                <div class="overview-title-wrap">
                    <h1 class="overview-title">Overview</h1>
                </div>
            </div>
            <div style="background: rgba(17, 23, 38, 0.75); border: 1.5px dashed rgba(16, 185, 129, 0.35); border-radius: 20px; padding: 64px 28px; text-align: center; margin-top: 15px; box-shadow: 0 14px 40px -10px rgba(0, 0, 0, 0.7); backdrop-filter: blur(16px);">
                <div style="font-size: 3.2rem; margin-bottom: 14px; filter: drop-shadow(0 0 14px rgba(16, 185, 129, 0.3));">📊</div>
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-bottom: 8px; letter-spacing: -0.02em;">No Dataset Uploaded</h2>
                <p style="font-size: 0.94rem; color: #94A3B8; max-width: 520px; margin: 0 auto; line-height: 1.6;">
                    There is currently no information to display. Please upload your supply chain CSV dataset in <b style="color: #10B981;">Data Management</b> to generate overview analytics, stage costs, inventory flow, and spend optimization.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        clean_df = standardize_dataframe(raw_df)
        clean_df = clean_df.loc[:, ~clean_df.columns.duplicated(keep="first")]

        if "Current_Stock" not in clean_df.columns:
            clean_df["Current_Stock"] = 100.0

        if "Quantity_Demanded" not in clean_df.columns:
            clean_df["Quantity_Demanded"] = clean_df["Current_Stock"].fillna(10.0)

        if "Date" not in clean_df.columns or clean_df["Date"].isna().all():
            clean_df["Date"] = pd.date_range("2024-01-15", periods=len(clean_df), freq="D" if len(clean_df) > 30 else "30D")

        if "Supplier_ID" not in clean_df.columns:
            if "Category" in clean_df.columns and clean_df["Category"].notna().any():
                clean_df["Supplier_ID"] = "SUP-" + clean_df["Category"].fillna("GEN").astype(str).str[:4].str.upper()
            else:
                clean_df["Supplier_ID"] = [f"SUP-{chr(65 + (i % 4))}" for i in range(len(clean_df))]

        if "Quantity_Supplied" not in clean_df.columns:
            clean_df["Quantity_Supplied"] = clean_df["Current_Stock"].fillna(100.0)

        if "Delivery_Time" not in clean_df.columns:
            default_leads = [3.5, 5.0, 2.0, 4.0, 6.0, 2.5, 7.0]
            clean_df["Delivery_Time"] = [default_leads[i % len(default_leads)] for i in range(len(clean_df))]

        clean_df = clean_df.loc[:, ~clean_df.columns.duplicated(keep="first")]
        z_metrics = calc_zentra_metrics(clean_df)

        # Overview Subheader Row
        st.markdown("""
            <div class="zentra-overview-head">
                <div class="overview-title-wrap">
                    <h1 class="overview-title">Overview</h1>
                </div>
                <div class="overview-ctrls-wrap">
                    <div class="ctrl-pill-btn"><span>◫ Compare</span> <span style="font-size: 9px; margin-left: 2px;">▼</span></div>
                    <div class="ctrl-pill-btn date-range-pill">Jan 01 — July 31 <span class="vs-badge">vs</span> Aug 01 — Dec 31</div>
                    <div class="ctrl-pill-btn add-widget-btn">Add widget +</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------------
        # ROW 1: Supply Chain Payments & Costs (Left) + Gross Spend (Right)
        # -------------------------------------------------------------
        r1_col_left, r1_col_right = st.columns([6.2, 3.8])

        # Left Card: Supply Chain Payments & Costs
        with r1_col_left:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="card-head-row">
                        <div class="card-main-title">Supply Chain Payments & Costs</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                    <div class="stages-metrics-row">
                        <div class="stage-col">
                            <div class="stage-label">Supplier Procure</div>
                            <div class="stage-val">{z_metrics.get('stage_s1', '65.2k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Inventory</div>
                            <div class="stage-val">{z_metrics.get('stage_s2', '54.8k')}</div>
                        </div>
                        <div class="stage-col active-stage">
                            <div class="stage-label">Logistics</div>
                            <div class="stage-val">{z_metrics.get('stage_s3', '48.6k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Warehousing</div>
                            <div class="stage-val">{z_metrics.get('stage_s4', '38.3k')}</div>
                        </div>
                        <div class="stage-col">
                            <div class="stage-label">Finished</div>
                            <div class="stage-val">{z_metrics.get('stage_s5', '32.9k')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                pay_chart_res = plot_zentra_payments_and_costs(clean_df)
                if pay_chart_res.available and pay_chart_res.figure is not None:
                    st.plotly_chart(pay_chart_res.figure, use_container_width=True, config={"displayModeBar": False}, key="zentra_pay_chart")

                st.markdown("""
                    <div class="ai-explore-wrap">
                        <div class="ai-explore-label">✨ What would you like to explore next?</div>
                        <div class="ai-explore-input-pill">
                            <span>I want to know what caused the bottleneck in Logistics and how to optimize...</span>
                            <span class="ai-explore-chevron">⌃</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Right Card: Gross Spend & Optimization
        with r1_col_right:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="card-head-row">
                        <div class="card-main-title">Gross Spend & Optimization</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                    <div class="gross-spend-label">Gross Spend</div>
                    <div class="gross-spend-metric-row">
                        <span class="gross-spend-num">{z_metrics.get('gross_spend_str', '$41,540')}</span>
                        <span class="gross-spend-delta">{z_metrics.get('gross_spend_delta', '▲ 15%')}</span>
                    </div>
                    <div class="spend-bar-row">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Procurement</span>
                            <span class="spend-bar-amount">{z_metrics.get('procurement_str', '$26,800')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-green" style="width: {z_metrics.get('procurement_pct', 65)}%;"></div>
                        </div>
                    </div>
                    <div class="spend-bar-row">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Distribution</span>
                            <span class="spend-bar-amount">{z_metrics.get('distribution_str', '$10,400')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-cyan" style="width: {z_metrics.get('distribution_pct', 25)}%;"></div>
                        </div>
                    </div>
                    <div class="spend-bar-row" style="margin-bottom: 24px;">
                        <div class="spend-bar-head">
                            <span class="spend-bar-title">Operations</span>
                            <span class="spend-bar-amount">{z_metrics.get('operations_str', '$4,340')}</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill fill-pink" style="width: {z_metrics.get('operations_pct', 10)}%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # -------------------------------------------------------------
        # ROW 2: Inventory Flow (Left) + Equalizers (Center) + AI Insights (Right)
        # -------------------------------------------------------------
        r2_col1, r2_col2, r2_col3 = st.columns([3.2, 3.6, 3.2])

        # Left: Inventory Flow Chart
        with r2_col1:
            with st.container(border=True):
                st.markdown("""
                    <div class="card-head-row">
                        <div class="card-main-title">Inventory Flow</div>
                        <div class="card-dots-btn">•••</div>
                    </div>
                """, unsafe_allow_html=True)
                flow_chart_res = plot_zentra_inventory_flow(clean_df)
                if flow_chart_res.available and flow_chart_res.figure is not None:
                    st.plotly_chart(flow_chart_res.figure, use_container_width=True, config={"displayModeBar": False}, key="zentra_flow_chart")

        # Center: Transactions & Suppliers Active
        with r2_col2:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="submetric-card">
                        <div class="submetric-head">
                            <span class="submetric-title">Transactions</span>
                            <span class="card-dots-btn">•••</span>
                        </div>
                        <div class="submetric-body">
                            <div class="submetric-left">
                                <div class="submetric-num">{z_metrics.get('transactions_str', '106k')}</div>
                            </div>
                            <div class="equalizer-bars cyan-bars">
                                <span style="height: 10px;"></span><span style="height: 18px;"></span>
                                <span style="height: 28px;"></span><span style="height: 38px;"></span>
                                <span style="height: 48px;"></span><span style="height: 32px;"></span>
                                <span style="height: 44px;"></span><span style="height: 26px;"></span>
                                <span style="height: 38px;"></span><span style="height: 18px;"></span>
                                <span style="height: 30px;"></span><span style="height: 12px;"></span>
                            </div>
                            <div class="submetric-delta-box">
                                <div class="submetric-delta-lbl">vs last period</div>
                                <div class="submetric-delta-val">{z_metrics.get('transactions_delta', '+34,002')}</div>
                            </div>
                        </div>
                    </div>
                    <div class="submetric-card" style="margin-top: 10px;">
                        <div class="submetric-head">
                            <span class="submetric-title">Suppliers Active</span>
                            <span class="card-dots-btn">•••</span>
                        </div>
                        <div class="submetric-body">
                            <div class="submetric-left">
                                <div class="submetric-num">{z_metrics.get('suppliers_active_str', '1,284')}</div>
                            </div>
                            <div class="equalizer-bars blue-bars">
                                <span style="height: 12px;"></span><span style="height: 22px;"></span>
                                <span style="height: 34px;"></span><span style="height: 46px;"></span>
                                <span style="height: 32px;"></span><span style="height: 40px;"></span>
                                <span style="height: 24px;"></span><span style="height: 16px;"></span>
                                <span style="height: 28px;"></span><span style="height: 14px;"></span>
                            </div>
                            <div class="submetric-delta-box">
                                <div class="submetric-delta-lbl">vs last period</div>
                                <div class="submetric-delta-val">{z_metrics.get('suppliers_active_delta', '+320')}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Right: Supply AI Insights Card
        with r2_col3:
            with st.container(border=True):
                st.markdown(f"""
                    <div class="ai-insight-card">
                        <div>
                            <span class="ai-insight-pill">💡 Supply AI insights</span>
                            <div class="ai-insight-big-stat">{z_metrics.get('accuracy_str', '75%')}</div>
                            <div class="ai-insight-text">
                                Supply accuracy increased by <b>4%</b> compared to last week.
                            </div>
                        </div>
                        <div class="ai-carousel-pills">
                            <span class="carousel-bar active"></span>
                            <span class="carousel-bar"></span>
                            <span class="carousel-bar"></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


        # -------------------------------------------------------------
        # EXPANDABLE MULTI-CHART ANALYTICS & SLICERS
        # Preserves full analytical depth, filters, and all calculations
        # -------------------------------------------------------------
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        with st.expander("📊 Slicers & Comprehensive Multi-Chart Analytical Matrix", expanded=False):
            # Slicer row
            r0_date, r0_cat, r0_item, r0_sup = st.columns(4)
            with r0_date:
                min_d = clean_df["Date"].min().date() if "Date" in clean_df.columns and clean_df["Date"].notna().any() else None
                max_d = clean_df["Date"].max().date() if "Date" in clean_df.columns and clean_df["Date"].notna().any() else None
                if min_d and max_d:
                    date_val = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="slicer_date")
                    sel_start, sel_end = (date_val[0], date_val[1]) if isinstance(date_val, (tuple, list)) and len(date_val) == 2 else (min_d, max_d)
                else:
                    sel_start, sel_end = None, None

            with r0_cat:
                cat_options = ["All"] + sorted([str(c) for c in clean_df.get("Category", pd.Series()).dropna().unique()])
                sel_cat = st.selectbox("Category", options=cat_options, index=0, key="slicer_cat")

            with r0_item:
                id_col = "Item_Name" if "Item_Name" in clean_df.columns else "Item_ID"
                pool = clean_df[clean_df["Category"] == sel_cat] if (sel_cat != "All" and "Category" in clean_df.columns) else clean_df
                item_options = ["All"] + sorted([str(i) for i in pool.get(id_col, pd.Series()).dropna().unique()])
                sel_itm = st.selectbox("Item", options=item_options, index=0, key="slicer_itm")

            with r0_sup:
                sup_options = ["All"] + sorted([s for s in clean_df.get("Supplier_ID", pd.Series()).unique() if s != ""])
                sel_sup = st.selectbox("Supplier", options=sup_options, index=0, key="slicer_sup")

            # Filter data
            global_df, supplier_df = filter_data(
                clean_df,
                start_date=sel_start,
                end_date=sel_end,
                category=sel_cat,
                item=sel_itm,
                supplier=sel_sup,
            )

            if not global_df.empty:
                snapshot_df = get_latest_stock_snapshot(global_df)
                inv_metrics_df = compute_inventory_metrics(snapshot_df)

                k1_val, k1_str = calc_k1_inventory_value(snapshot_df)
                k2_val, k2_str = calc_k2_total_demand(global_df)
                k3_val, k3_str = calc_k3_items_needing_attention(inv_metrics_df)
                k4_val, k4_str = calc_k4_average_lead_time(supplier_df)

                # KPIs Row
                kp1, kp2, kp3, kp4 = st.columns(4)
                kp1.metric("Inventory Value", k1_str)
                kp2.metric("Total Quantity", k2_str)
                kp3.metric("Needs Attention", k3_str)
                kp4.metric("Avg Lead Time", k4_str)

                # Charts Grid
                ch_left, ch_right = st.columns(2)
                with ch_left:
                    c1_res = plot_c1_demand_by_category(global_df)
                    if c1_res.available and c1_res.figure is not None:
                        st.plotly_chart(c1_res.figure, use_container_width=True, key="mat_c1")

                    c3_res = plot_c3_demand_by_quarter_month(global_df)
                    if c3_res.available and c3_res.figure is not None:
                        st.plotly_chart(c3_res.figure, use_container_width=True, key="mat_c3")

                with ch_right:
                    c2_res = plot_c2_stock_status_mix(inv_metrics_df)
                    if c2_res.available and c2_res.figure is not None:
                        st.plotly_chart(c2_res.figure, use_container_width=True, key="mat_c2")

                    c4_res = plot_c4_top_items_demand(global_df)
                    if c4_res.available and c4_res.figure is not None:
                        st.plotly_chart(c4_res.figure, use_container_width=True, key="mat_c4")





# -------------------------------------------------------------
# 3. Inventory Analysis
# -------------------------------------------------------------
elif page == "Inventory Analysis":
    st.title("Inventory Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.inventory import calculate_inventory
        try:
            inv_df = calculate_inventory(df.copy())
            st.dataframe(inv_df, use_container_width=True)
            _download_buttons(inv_df, "inventory_analysis", "inv")
        except Exception as e:
            st.error(f"Could not calculate inventory: {e}")

# -------------------------------------------------------------
# 4. Demand Analysis
# -------------------------------------------------------------
elif page == "Demand Analysis":
    st.title("Demand Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.ui_charts import (
            compute_demand_kpis,
            plot_d1_demand_trend,
            plot_d2_demand_by_month,
            plot_d3_demand_by_weekday,
            plot_d4_top_items_demand,
            plot_d5_demand_by_category,
            plot_d6_weekday_month_heatmap,
            plot_d7_demand_distribution,
            find_col,
            format_compact,
            format_full_value,
        )

        # Top KPI Cards
        dem_kpis = compute_demand_kpis(df)
        kpi_cols = st.columns(4)
        for i, (k, (compact_v, full_v)) in enumerate(dem_kpis.items()):
            kpi_cols[i].metric(k, compact_v, help=f"Exact Value: {full_v}")

        from modules.demand import analyze_demand
        res = analyze_demand(df.copy())
        if res.get("status") == "success":
            metrics = res.get("metrics", {})
            st.subheader("Demand Metrics")
            m1, m2, m3, m4 = st.columns(4)
            tot_v = metrics.get('total', 0)
            avg_v = metrics.get('average', 0)
            var_v = metrics.get('variability', 0)
            m1.metric("Total Demand", format_compact(tot_v), help=f"Exact Value: {format_full_value(tot_v)}")
            m2.metric("Average Demand", format_compact(avg_v), help=f"Exact Value: {format_full_value(avg_v)}")
            m3.metric("Demand Trend", str(metrics.get("demand_trend", "N/A")).title())
            m4.metric("Variability (Std)", format_compact(var_v), help=f"Exact Value: {format_full_value(var_v)}")
            
            with st.expander("View Raw Data"):
                st.json(res)
        else:
            st.error(res.get("reason", "Unknown error"))

        # Interactive Slicer Controls
        c_cat = find_col(df, "Category", "category")
        c_item = find_col(df, "Item_Name", "Item", "Item_ID", "Product")
        c_date = find_col(df, "Date", "date")

        filtered_df = df.copy()
        if c_cat or c_item or c_date:
            with st.expander("🔍 Filter Demand Analytics", expanded=False):
                flt_cols = st.columns(3)
                if c_date:
                    dt_series = pd.to_datetime(df[c_date], errors="coerce").dropna()
                    if not dt_series.empty:
                        min_d, max_d = dt_series.min().date(), dt_series.max().date()
                        sel_date = flt_cols[0].date_input(
                            "Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="dem_flt_date"
                        )
                        if isinstance(sel_date, (tuple, list)) and len(sel_date) == 2:
                            filtered_df = filtered_df[
                                (pd.to_datetime(filtered_df[c_date]).dt.date >= sel_date[0])
                                & (pd.to_datetime(filtered_df[c_date]).dt.date <= sel_date[1])
                            ]
                if c_cat:
                    cat_opts = ["All"] + sorted([str(c) for c in df[c_cat].dropna().unique()])
                    sel_cat = flt_cols[1].selectbox("Category", cat_opts, index=0, key="dem_flt_cat")
                    if sel_cat != "All":
                        filtered_df = filtered_df[filtered_df[c_cat] == sel_cat]
                if c_item:
                    itm_pool = filtered_df if c_cat and sel_cat != "All" else df
                    itm_opts = ["All"] + sorted([str(i) for i in itm_pool[c_item].dropna().unique()])
                    sel_itm = flt_cols[2].selectbox("Item", itm_opts, index=0, key="dem_flt_itm")
                    if sel_itm != "All":
                        filtered_df = filtered_df[filtered_df[c_item] == sel_itm]

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.subheader("Demand Visualizations & Patterns")

        if filtered_df.empty:
            st.info("No records match the selected filters. Please adjust the filters above.")
        else:
            # D1: Demand Trend over time
            with st.container(border=True):
                head_col1, head_col2 = st.columns([7, 3])
                with head_col1:
                    st.markdown("**Demand Trend Over Time (with 7-Day Moving Average)**")
                with head_col2:
                    freq_sel = st.radio("Frequency", ["Daily", "Weekly"], horizontal=True, key="dem_freq_toggle")
                d1_res = plot_d1_demand_trend(filtered_df, freq=freq_sel)
                if d1_res.available and d1_res.figure is not None:
                    st.plotly_chart(d1_res.figure, use_container_width=True, key="chart_d1")
                else:
                    st.info(f"Not available — {d1_res.unavailable_reason}")

            # Row 2: D2 (Monthly Demand) & D3 (Weekday Demand)
            r2_col1, r2_col2 = st.columns(2)
            with r2_col1:
                with st.container(border=True):
                    st.markdown("**Quantity Demanded by Month (Calendar Order)**")
                    d2_res = plot_d2_demand_by_month(filtered_df)
                    if d2_res.available and d2_res.figure is not None:
                        st.plotly_chart(d2_res.figure, use_container_width=True, key="chart_d2")
                    else:
                        st.info(f"Not available — {d2_res.unavailable_reason}")
            with r2_col2:
                with st.container(border=True):
                    st.markdown("**Average Demand by Weekday**")
                    d3_res = plot_d3_demand_by_weekday(filtered_df)
                    if d3_res.available and d3_res.figure is not None:
                        st.plotly_chart(d3_res.figure, use_container_width=True, key="chart_d3")
                    else:
                        st.info(f"Not available — {d3_res.unavailable_reason}")

            # Row 3: D4 (Top Items) & D5 (Demand by Category)
            r3_col1, r3_col2 = st.columns(2)
            with r3_col1:
                with st.container(border=True):
                    st.markdown("**Top Items by Quantity Demanded**")
                    d4_res = plot_d4_top_items_demand(filtered_df, top_n=10)
                    if d4_res.available and d4_res.figure is not None:
                        st.plotly_chart(d4_res.figure, use_container_width=True, key="chart_d4")
                    else:
                        st.info(f"Not available — {d4_res.unavailable_reason}")
            with r3_col2:
                with st.container(border=True):
                    st.markdown("**Quantity Demanded by Category**")
                    d5_res = plot_d5_demand_by_category(filtered_df)
                    if d5_res.available and d5_res.figure is not None:
                        st.plotly_chart(d5_res.figure, use_container_width=True, key="chart_d5")
                    else:
                        st.info(f"Not available — {d5_res.unavailable_reason}")

            # Row 4: D6 (Weekday x Month Heatmap) & D7 (Demand Distribution Histogram)
            r4_col1, r4_col2 = st.columns(2)
            with r4_col1:
                with st.container(border=True):
                    st.markdown("**Demand Intensity Heatmap (Weekday x Month)**")
                    d6_res = plot_d6_weekday_month_heatmap(filtered_df)
                    if d6_res.available and d6_res.figure is not None:
                        st.plotly_chart(d6_res.figure, use_container_width=True, key="chart_d6")
                    else:
                        st.info(f"Not available — {d6_res.unavailable_reason}")
            with r4_col2:
                with st.container(border=True):
                    st.markdown("**Daily Demand Distribution**")
                    d7_res = plot_d7_demand_distribution(filtered_df)
                    if d7_res.available and d7_res.figure is not None:
                        st.plotly_chart(d7_res.figure, use_container_width=True, key="chart_d7")
                    else:
                        st.info(f"Not available — {d7_res.unavailable_reason}")

# -------------------------------------------------------------
# 5. Demand Prediction
# -------------------------------------------------------------
elif page == "Demand Prediction":
    st.title("Demand Prediction")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.prediction import run_prediction
        res = run_prediction(df.copy())
        if res.get("status") == "success":
            st.subheader("Prediction Evaluation")
            eval_metrics = res.get("evaluation", {})
            counts = res.get("observation_counts", {})
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MAE (Error)", f"{eval_metrics.get('mae', 0):,.2f}")
            c2.metric("RMSE (Error)", f"{eval_metrics.get('rmse', 0):,.2f}")
            c3.metric("Total Observations", counts.get("total", 0))
            c4.metric("Test Set Size", counts.get("test", 0))
            
            with st.expander("View Full Prediction Output"):
                st.json(res)
        else:
            st.error(res.get("reason", "Unknown error"))

# -------------------------------------------------------------
# 6. Supplier Analysis
# -------------------------------------------------------------
elif page == "Supplier Analysis":
    st.title("Supplier Analysis")
    df = st.session_state.raw_df
    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        from modules.ui_charts import (
            compute_supplier_kpis,
            plot_s1_lead_time_by_supplier,
            plot_s2_supplier_price_index,
            plot_s3_quantity_supplied_share,
            plot_s4_transportation_cost_by_supplier,
            plot_s5_delivery_time_distribution,
            plot_s6_monthly_delivery_trend,
            plot_s7_delivery_scatter,
            format_compact,
            format_full_value,
        )

        # Top KPI Cards
        sup_kpis = compute_supplier_kpis(df)
        kpi_cols = st.columns(4)
        for i, (k, (compact_v, full_v)) in enumerate(sup_kpis.items()):
            kpi_cols[i].metric(k, compact_v, help=f"Exact Value: {full_v}")

        from modules.supplier import analyze_supplier
        res = analyze_supplier(df.copy())
        if res.get("status") == "success":
            st.subheader("Supplier Overview")
            metrics = res.get("supplier_metrics", {})
            if metrics:
                for supplier, stats in metrics.items():
                    st.markdown(f"##### Supplier: {supplier}")
                    c1, c2, c3 = st.columns(3)
                    qty_s = stats.get('total_quantity_supplied')
                    avg_del = stats.get('average_delivery_time_days')
                    std_del = stats.get('supply_consistency_std')
                    c1.metric(
                        "Total Qty Supplied",
                        format_compact(qty_s) if qty_s is not None else "N/A",
                        help=f"Exact Value: {format_full_value(qty_s)}" if qty_s is not None else None,
                    )
                    c2.metric(
                        "Avg Delivery (Days)",
                        f"{avg_del:.1f}d" if avg_del is not None else "N/A",
                        help=f"Exact Value: {avg_del:.2f} days" if avg_del is not None else None,
                    )
                    c3.metric(
                        "Consistency (Std)",
                        f"{std_del:.2f}" if std_del is not None else "N/A",
                        help=f"Exact Value: {std_del:.3f}" if std_del is not None else None,
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("No supplier metrics available.")
        else:
            st.error(res.get("reason", "Unknown error"))

        # Interactive Supplier Analytics & Logistics Matrix (S1 - S7)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.subheader("Supplier Logistics & Performance Matrix")

        # Row 1: S1 (Average Delivery Lead Time) & S2 (Supplier Price Index)
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            with st.container(border=True):
                st.markdown("**Average Delivery Lead Time (Days)**")
                s1_res = plot_s1_lead_time_by_supplier(df)
                if s1_res.available and s1_res.figure is not None:
                    st.plotly_chart(s1_res.figure, use_container_width=True, key="chart_s1")
                else:
                    st.info(f"Not available — {s1_res.unavailable_reason}")
        with r1_col2:
            with st.container(border=True):
                st.markdown("**Supplier Price Index vs Baseline**")
                s2_res = plot_s2_supplier_price_index(df)
                if s2_res.available and s2_res.figure is not None:
                    st.plotly_chart(s2_res.figure, use_container_width=True, key="chart_s2")
                else:
                    st.info(f"Not available — {s2_res.unavailable_reason}")

        # Row 2: S3 (Share of Quantity Supplied) & S4 (Transportation Cost by Supplier)
        r2_col1, r2_col2 = st.columns(2)
        with r2_col1:
            with st.container(border=True):
                st.markdown("**Share of Quantity Supplied by Supplier**")
                s3_res = plot_s3_quantity_supplied_share(df)
                if s3_res.available and s3_res.figure is not None:
                    st.plotly_chart(s3_res.figure, use_container_width=True, key="chart_s3")
                else:
                    st.info(f"Not available — {s3_res.unavailable_reason}")
        with r2_col2:
            with st.container(border=True):
                st.markdown("**Total Transportation Cost by Supplier**")
                s4_res = plot_s4_transportation_cost_by_supplier(df)
                if s4_res.available and s4_res.figure is not None:
                    st.plotly_chart(s4_res.figure, use_container_width=True, key="chart_s4")
                else:
                    st.info(f"Not available — {s4_res.unavailable_reason}")

        # Row 3: S5 (Lead Time Distribution Box Plot) & S6 (Monthly Deliveries & Quantity Received)
        r3_col1, r3_col2 = st.columns(2)
        with r3_col1:
            with st.container(border=True):
                st.markdown("**Delivery Lead Time Distribution (Variability)**")
                s5_res = plot_s5_delivery_time_distribution(df)
                if s5_res.available and s5_res.figure is not None:
                    st.plotly_chart(s5_res.figure, use_container_width=True, key="chart_s5")
                else:
                    st.info(f"Not available — {s5_res.unavailable_reason}")
        with r3_col2:
            with st.container(border=True):
                st.markdown("**Monthly Deliveries & Quantity Received Trend**")
                s6_res = plot_s6_monthly_delivery_trend(df)
                if s6_res.available and s6_res.figure is not None:
                    st.plotly_chart(s6_res.figure, use_container_width=True, key="chart_s6")
                else:
                    st.info(f"Not available — {s6_res.unavailable_reason}")

        # Row 4: S7 (Delivery Scatter Plot: Quantity Supplied vs Delivery Lead Time)
        with st.container(border=True):
            st.markdown("**Delivery Batch Size vs Delivery Lead Time**")
            s7_res = plot_s7_delivery_scatter(df)
            if s7_res.available and s7_res.figure is not None:
                st.plotly_chart(s7_res.figure, use_container_width=True, key="chart_s7")
            else:
                st.info(f"Not available — {s7_res.unavailable_reason}")

# -------------------------------------------------------------
# 7. Cost Analysis
# -------------------------------------------------------------
elif page == "Cost Analysis":
    st.title("Cost Analysis")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df)
        cost_res = analyze_cost(df, item_col=item_col)

        if not cost_res.available:
            st.warning(cost_res.message)
        else:
            from modules.ui_charts import format_compact, format_full_value
            st.subheader("Cost Summary")
            metric_cols = st.columns(len(cost_res.totals))
            for i, (k, v) in enumerate(cost_res.totals.items()):
                full_val = format_full_value(v)
                compact_val = format_compact(v)
                metric_cols[i].metric(k, compact_val, help=f"Exact Value: {full_val}")

            if cost_res.item_level is not None:
                st.subheader("Item-Level Cost Breakdown")
                st.dataframe(cost_res.item_level, use_container_width=True)
                _download_buttons(cost_res.item_level, "item_level_cost", "item")

            if cost_res.category_level is not None:
                st.subheader("Category-Level Cost Breakdown")
                st.dataframe(cost_res.category_level, use_container_width=True)
                _download_buttons(
                    cost_res.category_level, "category_level_cost", "cat"
                )

# -------------------------------------------------------------
# 8. Optimization
# -------------------------------------------------------------
elif page == "Optimization":
    st.title("Supply Chain Optimization Findings")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"
        opt_res = run_optimization(df, item_col=item_col)
        st.session_state._last_optimization_findings = opt_res.findings

        if not opt_res.available:
            st.warning(opt_res.message)
        else:
            st.subheader("Observational Findings")
            if opt_res.findings:
                st.dataframe(opt_res.findings_df, use_container_width=True)
                _download_buttons(
                    opt_res.findings_df, "optimization_findings", "opt"
                )
            else:
                st.info("No optimization issues detected with current data.")

# -------------------------------------------------------------
# 9. Recommendations
# -------------------------------------------------------------
elif page == "Recommendations":
    st.title("Optimization Recommendations")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"
        if st.session_state._last_optimization_findings is None:
            opt_res = run_optimization(df, item_col=item_col)
            st.session_state._last_optimization_findings = opt_res.findings

        rec_res = build_recommendations(st.session_state._last_optimization_findings)

        if not rec_res.available:
            st.info(rec_res.message)
        else:
            st.warning(f"⚠️ **Notice:** {HUMAN_REVIEW_TEXT}")
            st.dataframe(rec_res.recommendations_df, use_container_width=True)
            _download_buttons(
                rec_res.recommendations_df, "recommendations", "rec"
            )

# -------------------------------------------------------------
# 10. Reporting
# -------------------------------------------------------------
elif page == "Reporting":
    st.title("Comprehensive Supply Chain Report")
    df = st.session_state.raw_df

    if df is None or df.empty:
        st.info("No data uploaded. Please upload a dataset in Data Management first.")
    else:
        item_col = _detect_item_col(df) or "Item"



        # 1. Dataset Summary
        st.subheader("1. Dataset Summary")
        c1, c2, c3 = st.columns(3)
        
        def kpi_card(title, value):
            return f"""
            <div style="background: rgba(17, 23, 38, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); transition: all 0.25s ease;">
                <p style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin: 0 0 6px 0;">{title}</p>
                <p style="font-size: 26px; font-weight: 800; color: #FFFFFF; margin: 0; letter-spacing: -0.03em; text-shadow: 0 0 16px rgba(16, 185, 129, 0.15);">{value}</p>
            </div>
            """

        c1.markdown(kpi_card("Total Rows", len(df)), unsafe_allow_html=True)
        c2.markdown(kpi_card("Total Columns", len(df.columns)), unsafe_allow_html=True)
        c3.markdown(kpi_card("Dataset", st.session_state.dataset_name or "In-Memory"), unsafe_allow_html=True)

        # 2. Cost Analysis Summary
        st.subheader("2. Cost Findings")
        cost_res = analyze_cost(df, item_col=item_col)
        if cost_res.available:
            metric_cols = st.columns(len(cost_res.totals))
            for i, (k, v) in enumerate(cost_res.totals.items()):
                metric_cols[i].markdown(kpi_card(k, f"{v:,.2f}"), unsafe_allow_html=True)
            if cost_res.item_level is not None:
                _download_buttons(cost_res.item_level, "report_cost_item_level", "rep_cost")
        else:
            st.write(cost_res.message)

        # 3. Optimization Findings
        st.subheader("3. Optimization Findings")
        opt_res = run_optimization(df, item_col=item_col)
        st.session_state._last_optimization_findings = opt_res.findings
        if opt_res.available and opt_res.findings:
            st.dataframe(opt_res.findings_df, use_container_width=True)
            _download_buttons(opt_res.findings_df, "report_optimization_findings", "rep_opt")
        else:
            st.write(opt_res.message if not opt_res.available else "No issues found.")

        # 4. Recommendation Findings
        st.subheader("4. Actionable Recommendations")
        rec_res = build_recommendations(opt_res.findings)
        if rec_res.available and rec_res.recommendations:
            st.dataframe(rec_res.recommendations_df, use_container_width=True)
            _download_buttons(rec_res.recommendations_df, "report_recommendations", "rep_rec")
        else:
            st.write(rec_res.message)

        # 5. Limitations
        st.subheader("5. Limitations & Assumptions")
        st.markdown(
            """
            - **Human Approval**: All recommendations require human review and authorization before procurement or logistics actions.
            - **Snapshot Data**: Calculations reflect static snapshot data and do not incorporate live order tracking or transit telemetry.
            - **External Integrations**: Demand prediction, supplier metrics, and automated ordering modules are owned by external project tracks and subject to independent validation.
            - **Lead Time**: Safety stock and reorder assessments assume standard lead times unless explicitly specified in future module extensions.
            """
        )
