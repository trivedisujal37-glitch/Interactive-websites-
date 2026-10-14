"""UI Charts and visual enhancement module for Supply Chain Optimization.

Provides pure functions returning Plotly figures for Supplier Analysis (S1-S7)
and Demand Analysis (D1-D7), plus format_compact helper for KPI cards.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# Color Palette Tokens (Matching Dark Obsidian SaaS Theme)
# -----------------------------------------------------------------------------
COLOR_PAGE_BG = "#090D16"
COLOR_CARD_BG = "#111726"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_TEXT = "#E2E8F0"
COLOR_MUTED = "#94A3B8"
COLOR_GREEN = "#10B981"
COLOR_CYAN = "#00F2FE"
COLOR_BLUE = "#3B82F6"
COLOR_VIOLET = "#8B5CF6"
COLOR_AMBER = "#FBBF24"
COLOR_ROSE = "#F43F5E"

PALETTE = [COLOR_GREEN, COLOR_CYAN, COLOR_BLUE, COLOR_VIOLET, COLOR_AMBER, COLOR_ROSE]


@dataclass
class ChartResult:
    """Standard container for visual chart outputs."""
    available: bool
    figure: go.Figure | None = None
    unavailable_reason: str | None = None


# -----------------------------------------------------------------------------
# Helper: format_compact (Task 2)
# -----------------------------------------------------------------------------
def format_compact(val: object, prefix: str = "", suffix: str = "") -> str:
    """Format compact numbers for KPI card display.
    
    Rules:
    - below 1,000: plain number (up to 2 decimals if decimal, stripped trailing zeros)
    - 1,000 to 999,999: show K (e.g. 24,000 -> 24K, 34,000 -> 34K, 74,876.4 -> 74.9K)
    - 1,000,000 to 999,999,999: show M (e.g. 1,782,430 -> 1.78M)
    - 1,000,000,000+: show B (e.g. 2.5e9 -> 2.5B)
    - Handle negatives, zero ('0'), NaN/None ('-'), numpy types, and string inputs.
    """
    if val is None:
        return "-"
    if isinstance(val, (float, np.floating)) and (np.isnan(val) or np.isinf(val)):
        return "-"
    try:
        if isinstance(val, str):
            clean_str = val.replace(",", "").strip()
            if not clean_str or clean_str == "-":
                return "-"
            num = float(clean_str)
        else:
            num = float(val)
    except (ValueError, TypeError):
        return "-"

    if np.isnan(num) or np.isinf(num):
        return "-"

    if num == 0:
        return f"{prefix}0{suffix}"

    sign = "-" if num < 0 else ""
    abs_num = abs(num)

    if abs_num >= 1e9 - 1e7:
        scaled = abs_num / 1e9
        txt = f"{scaled:.2f}".rstrip("0").rstrip(".")
        if txt == "1000":
            res = f"{sign}1T"
        else:
            res = f"{sign}{txt}B"
    elif abs_num >= 1e6 - 1e4:
        scaled = abs_num / 1e6
        txt = f"{scaled:.2f}".rstrip("0").rstrip(".")
        if txt == "1000":
            res = f"{sign}1B"
        else:
            res = f"{sign}{txt}M"
    elif abs_num >= 1000 - 0.05:
        scaled = abs_num / 1000
        txt = f"{scaled:.1f}".rstrip("0").rstrip(".")
        if txt == "1000":
            res = f"{sign}1M"
        else:
            res = f"{sign}{txt}K"
    else:
        if abs_num == int(abs_num):
            res = f"{sign}{int(abs_num)}"
        else:
            res = f"{sign}{abs_num:.2f}".rstrip("0").rstrip(".")

    return f"{prefix}{res}{suffix}"


def format_full_value(val: object, prefix: str = "", suffix: str = "") -> str:
    """Format exact full number for tooltips/help text."""
    if val is None:
        return "-"
    if isinstance(val, (float, np.floating)) and (np.isnan(val) or np.isinf(val)):
        return "-"
    try:
        if isinstance(val, str):
            clean_str = val.replace(",", "").strip()
            num = float(clean_str)
        else:
            num = float(val)
    except (ValueError, TypeError):
        return str(val)
    if num == int(num):
        return f"{prefix}{int(num):,}{suffix}"
    return f"{prefix}{num:,.2f}{suffix}"


# -----------------------------------------------------------------------------
# Column Finding Helper
# -----------------------------------------------------------------------------
def find_col(df: pd.DataFrame | None, *candidates: str) -> str | None:
    """Find the first matching column name in df (case-insensitive)."""
    if df is None or df.empty:
        return None
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        cl = cand.strip().lower()
        if cl in lower_map:
            return lower_map[cl]
    return None


def apply_ui_chart_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    """Apply unified dark obsidian theme to Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT, family="'Plus Jakarta Sans', -apple-system, sans-serif", size=11),
        margin=dict(l=30, r=20, t=30, b=30),
        height=height,
        hoverlabel=dict(
            bgcolor="#111726",
            font_color="#FFFFFF",
            font_size=11,
            font_family="'Plus Jakarta Sans', sans-serif",
            bordercolor="rgba(16, 185, 129, 0.4)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_MUTED),
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(color=COLOR_MUTED, size=10),
    )
    fig.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        tickfont=dict(color=COLOR_MUTED, size=10),
    )
    return fig


# -----------------------------------------------------------------------------
# S1 - S7: Supplier Analysis Charts
# -----------------------------------------------------------------------------
def get_supplier_delivery_df(df: pd.DataFrame | None) -> tuple[pd.DataFrame, dict[str, str]]:
    """Extract rows with non-empty delivery records. Never mutate original df."""
    if df is None or df.empty:
        return pd.DataFrame(), {}
    
    col_sup = find_col(df, "Supplier_ID", "supplier_id", "Supplier ID", "Supplier", "supplier")
    col_lead = find_col(df, "Delivery_Time", "delivery_time", "Delivery Time", "lead time", "delivery_time_days")
    col_qty = find_col(df, "Quantity_Supplied", "quantity_supplied", "Quantity Supplied", "units supplied")
    col_s_price = find_col(df, "Supplier_Unit_Price", "supplier_unit_price", "Supplier Unit Price", "purchase cost", "purchase price")
    col_u_price = find_col(df, "Unit_Price", "unit_price", "Unit Price", "price")
    col_trans = find_col(df, "Transportation_Cost", "transportation_cost", "Transportation Cost", "shipping cost")
    col_date = find_col(df, "Date", "date", "Delivery Date")
    
    cols = {
        "supplier": col_sup,
        "lead_time": col_lead,
        "quantity_supplied": col_qty,
        "supplier_price": col_s_price,
        "unit_price": col_u_price,
        "trans_cost": col_trans,
        "date": col_date,
    }
    
    if not col_sup:
        return pd.DataFrame(), cols
        
    # Filter to rows where supplier is not null or empty
    sub = df[df[col_sup].notna() & (df[col_sup].astype(str).str.strip() != "")].copy()
    return sub, cols


def plot_s1_lead_time_by_supplier(df: pd.DataFrame | None) -> ChartResult:
    """S1: Horizontal bar - Average Delivery Lead Time (days) by supplier, ordered by Supplier_ID."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_lead = cols.get("supplier"), cols.get("lead_time")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_lead or c_lead not in sub.columns:
        return ChartResult(False, None, "Delivery_Time column not in this dataset")
        
    valid = sub.dropna(subset=[c_lead]).copy()
    valid[c_lead] = pd.to_numeric(valid[c_lead], errors="coerce")
    valid = valid.dropna(subset=[c_lead])
    valid = valid[valid[c_lead] > 0]
    if valid.empty:
        return ChartResult(False, None, "No valid delivery lead times found")
        
    grp = valid.groupby(c_sup, as_index=False)[c_lead].mean()
    # Order supplier charts by Supplier_ID (no performance sorting)
    grp.sort_values(c_sup, ascending=True, inplace=True)
    
    sups = grp[c_sup].astype(str).tolist()
    leads = grp[c_lead].tolist()
    text_labels = [f"{v:.1f}d" for v in leads]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=leads,
                y=sups,
                orientation="h",
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_CYAN, cornerradius=8),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=max(220, len(sups) * 36))
    fig.update_layout(xaxis_title="Average Lead Time (Days)", yaxis_title="")
    return ChartResult(True, fig)


def plot_s2_supplier_price_index(df: pd.DataFrame | None) -> ChartResult:
    """S2: Horizontal bar - Supplier Price Index = average(Supplier_Unit_Price / Unit_Price).
    Reference line at 1.00. Caption: '1.00 = standard cost. For comparison only.'
    """
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_sp, c_up = cols.get("supplier"), cols.get("supplier_price"), cols.get("unit_price")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_sp or not c_up or c_sp not in sub.columns or c_up not in sub.columns:
        return ChartResult(False, None, "Supplier_Unit_Price or Unit_Price not in this dataset")
        
    valid = sub.dropna(subset=[c_sp, c_up]).copy()
    valid[c_sp] = pd.to_numeric(valid[c_sp], errors="coerce")
    valid[c_up] = pd.to_numeric(valid[c_up], errors="coerce")
    valid = valid.dropna(subset=[c_sp, c_up])
    valid = valid[(valid[c_up] > 0) & (valid[c_sp] > 0)]
    if valid.empty:
        return ChartResult(False, None, "No comparable price data found")
        
    valid["price_index"] = valid[c_sp] / valid[c_up]
    grp = valid.groupby(c_sup, as_index=False)["price_index"].mean()
    grp.sort_values(c_sup, ascending=True, inplace=True)
    
    sups = grp[c_sup].astype(str).tolist()
    indices = grp["price_index"].tolist()
    text_labels = [f"{v:.2f}" for v in indices]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=indices,
                y=sups,
                orientation="h",
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_GREEN, cornerradius=8),
            )
        ]
    )
    fig.add_vline(
        x=1.0,
        line_width=2,
        line_dash="dash",
        line_color=COLOR_AMBER,
        annotation_text="1.00 Baseline",
        annotation_position="top right",
        annotation_font_color=COLOR_AMBER,
    )
    apply_ui_chart_theme(fig, height=max(220, len(sups) * 36))
    fig.update_layout(
        xaxis_title="Price Ratio (1.00 = standard cost. For comparison only)",
        yaxis_title="",
    )
    return ChartResult(True, fig)


def plot_s3_quantity_supplied_share(df: pd.DataFrame | None) -> ChartResult:
    """S3: Donut - Share of Quantity Supplied by supplier, total in centre."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_qty = cols.get("supplier"), cols.get("quantity_supplied")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_qty or c_qty not in sub.columns:
        return ChartResult(False, None, "Quantity_Supplied column not in this dataset")
        
    valid = sub.dropna(subset=[c_qty]).copy()
    valid[c_qty] = pd.to_numeric(valid[c_qty], errors="coerce")
    valid = valid.dropna(subset=[c_qty])
    valid = valid[valid[c_qty] > 0]
    if valid.empty:
        return ChartResult(False, None, "No supplied quantities found")
        
    grp = valid.groupby(c_sup, as_index=False)[c_qty].sum()
    grp.sort_values(c_sup, ascending=True, inplace=True)
    
    total_qty = grp[c_qty].sum()
    sups = grp[c_sup].astype(str).tolist()
    vals = grp[c_qty].tolist()
    
    fig = go.Figure(
        data=[
            go.Pie(
                labels=sups,
                values=vals,
                hole=0.62,
                textinfo="label+percent",
                textposition="outside",
                marker=dict(colors=PALETTE),
                showlegend=False,
            )
        ]
    )
    fig.add_annotation(
        text=f"Total<br><b>{format_compact(total_qty)}</b>",
        x=0.5,
        y=0.5,
        font=dict(size=12, color=COLOR_CYAN, family="'Plus Jakarta Sans', sans-serif"),
        showarrow=False,
    )
    apply_ui_chart_theme(fig, height=280)
    return ChartResult(True, fig)


def plot_s4_transportation_cost_by_supplier(df: pd.DataFrame | None) -> ChartResult:
    """S4: Column chart - Total Transportation Cost by supplier."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_trans = cols.get("supplier"), cols.get("trans_cost")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_trans or c_trans not in sub.columns:
        return ChartResult(False, None, "Transportation_Cost column not in this dataset")
        
    valid = sub.dropna(subset=[c_trans]).copy()
    valid[c_trans] = pd.to_numeric(valid[c_trans], errors="coerce")
    valid = valid.dropna(subset=[c_trans])
    valid = valid[valid[c_trans] > 0]
    if valid.empty:
        return ChartResult(False, None, "No transportation costs found")
        
    grp = valid.groupby(c_sup, as_index=False)[c_trans].sum()
    grp.sort_values(c_sup, ascending=True, inplace=True)
    
    sups = grp[c_sup].astype(str).tolist()
    costs = grp[c_trans].tolist()
    text_labels = [format_compact(v) for v in costs]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=sups,
                y=costs,
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_BLUE, cornerradius=6),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=270)
    fig.update_layout(xaxis_title="", yaxis_title="Transportation Cost")
    return ChartResult(True, fig)


def plot_s5_delivery_time_distribution(df: pd.DataFrame | None) -> ChartResult:
    """S5: Box plot - Distribution of Delivery_Time per supplier (shows variability)."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_lead = cols.get("supplier"), cols.get("lead_time")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_lead or c_lead not in sub.columns:
        return ChartResult(False, None, "Delivery_Time column not in this dataset")
        
    valid = sub.dropna(subset=[c_lead]).copy()
    valid[c_lead] = pd.to_numeric(valid[c_lead], errors="coerce")
    valid = valid.dropna(subset=[c_lead])
    valid = valid[valid[c_lead] > 0]
    if valid.empty:
        return ChartResult(False, None, "No delivery lead time distributions found")
        
    # Sort suppliers
    ordered_sups = sorted(valid[c_sup].astype(str).unique())
    fig = go.Figure()
    for idx, sup in enumerate(ordered_sups):
        sup_data = valid[valid[c_sup].astype(str) == sup][c_lead]
        fig.add_trace(
            go.Box(
                y=sup_data,
                name=sup,
                boxmean=True,
                marker_color=PALETTE[idx % len(PALETTE)],
            )
        )
    apply_ui_chart_theme(fig, height=280)
    fig.update_layout(yaxis_title="Lead Time (Days)", showlegend=False)
    return ChartResult(True, fig)


def plot_s6_monthly_delivery_trend(df: pd.DataFrame | None) -> ChartResult:
    """S6: Line/column chart - Deliveries received per month (count) and Quantity Supplied."""
    sub, cols = get_supplier_delivery_df(df)
    c_date, c_qty = cols.get("date"), cols.get("quantity_supplied")
    if sub.empty:
        return ChartResult(False, None, "Supplier delivery records not in this dataset")
    if not c_date or c_date not in sub.columns:
        return ChartResult(False, None, "Date column not in this dataset")
        
    valid = sub.dropna(subset=[c_date]).copy()
    valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
    valid = valid.dropna(subset=["_dt"])
    if valid.empty:
        return ChartResult(False, None, "No dated delivery records found")
        
    valid["YearMonth"] = valid["_dt"].dt.to_period("M")
    valid["MonthLabel"] = valid["_dt"].dt.strftime("%b %Y")
    
    if c_qty and c_qty in valid.columns:
        valid["_qty"] = pd.to_numeric(valid[c_qty], errors="coerce").fillna(0)
    else:
        valid["_qty"] = 0.0
        
    grp = valid.groupby(["YearMonth", "MonthLabel"], as_index=False).agg(
        delivery_count=("_dt", "count"),
        total_qty=("_qty", "sum"),
    )
    grp.sort_values("YearMonth", inplace=True)
    
    months = grp["MonthLabel"].tolist()
    counts = grp["delivery_count"].tolist()
    qtys = grp["total_qty"].tolist()
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=months,
            y=counts,
            name="Delivery Count",
            marker=dict(color=COLOR_GREEN, cornerradius=4),
            yaxis="y",
        )
    )
    if any(q > 0 for q in qtys):
        fig.add_trace(
            go.Scatter(
                x=months,
                y=qtys,
                name="Quantity Supplied",
                mode="lines+markers",
                line=dict(color=COLOR_CYAN, width=2.5),
                marker=dict(size=6),
                yaxis="y2",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Deliveries (Count)", gridcolor="rgba(255, 255, 255, 0.05)"),
            yaxis2=dict(
                title="Units Supplied",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(color=COLOR_MUTED, size=10),
            ),
        )
    else:
        fig.update_layout(yaxis_title="Deliveries (Count)")
        
    apply_ui_chart_theme(fig, height=280)
    return ChartResult(True, fig)


def plot_s7_delivery_scatter(df: pd.DataFrame | None) -> ChartResult:
    """S7: Scatter - each delivery: Quantity_Supplied (x) vs Delivery_Time (y), color by supplier."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_qty, c_lead, c_date = cols.get("supplier"), cols.get("quantity_supplied"), cols.get("lead_time"), cols.get("date")
    if sub.empty or not c_sup:
        return ChartResult(False, None, "Supplier column not in this dataset")
    if not c_qty or not c_lead or c_qty not in sub.columns or c_lead not in sub.columns:
        return ChartResult(False, None, "Quantity_Supplied or Delivery_Time not in this dataset")
        
    valid = sub.dropna(subset=[c_qty, c_lead]).copy()
    valid[c_qty] = pd.to_numeric(valid[c_qty], errors="coerce")
    valid[c_lead] = pd.to_numeric(valid[c_lead], errors="coerce")
    valid = valid.dropna(subset=[c_qty, c_lead])
    valid = valid[(valid[c_qty] > 0) & (valid[c_lead] > 0)]
    if valid.empty:
        return ChartResult(False, None, "No valid delivery records for scatter plot")
        
    ordered_sups = sorted(valid[c_sup].astype(str).unique())
    fig = go.Figure()
    
    for idx, sup in enumerate(ordered_sups):
        sup_rows = valid[valid[c_sup].astype(str) == sup]
        hover_texts = []
        for _, r in sup_rows.iterrows():
            d_val = str(r[c_date])[:10] if (c_date and c_date in r and pd.notna(r[c_date])) else "-"
            hover_texts.append(f"Supplier: {sup}<br>Date: {d_val}<br>Qty: {format_compact(r[c_qty])}<br>Lead: {r[c_lead]:.1f}d")
            
        fig.add_trace(
            go.Scatter(
                x=sup_rows[c_qty],
                y=sup_rows[c_lead],
                mode="markers",
                name=sup,
                hovertext=hover_texts,
                hoverinfo="text",
                marker=dict(
                    size=8,
                    color=PALETTE[idx % len(PALETTE)],
                    line=dict(width=1, color="#FFFFFF"),
                    opacity=0.85,
                ),
            )
        )
    apply_ui_chart_theme(fig, height=300)
    fig.update_layout(
        xaxis_title="Quantity Supplied",
        yaxis_title="Lead Time (Days)",
    )
    return ChartResult(True, fig)


def compute_supplier_kpis(df: pd.DataFrame | None) -> dict[str, tuple[str, str]]:
    """Compute KPI tuple (compact_val, full_tooltip) for Supplier Analysis."""
    sub, cols = get_supplier_delivery_df(df)
    c_sup, c_qty, c_lead = cols.get("supplier"), cols.get("quantity_supplied"), cols.get("lead_time")
    
    if sub.empty or not c_sup:
        return {
            "Total Deliveries": ("-", "No deliveries recorded"),
            "Total Quantity Supplied": ("-", "No quantity supplied recorded"),
            "Average Lead Time": ("-", "No lead time recorded"),
            "Number of Suppliers": ("-", "No suppliers found"),
        }
        
    num_deliveries = len(sub)
    num_sups = sub[c_sup].nunique()
    
    if c_qty and c_qty in sub.columns:
        valid_qty = pd.to_numeric(sub[c_qty], errors="coerce").dropna()
        tot_qty = float(valid_qty.sum())
    else:
        tot_qty = 0.0
        
    if c_lead and c_lead in sub.columns:
        valid_lead = pd.to_numeric(sub[c_lead], errors="coerce").dropna()
        valid_lead = valid_lead[valid_lead > 0]
        avg_lead = float(valid_lead.mean()) if not valid_lead.empty else None
    else:
        avg_lead = None
        
    return {
        "Total Deliveries": (format_compact(num_deliveries), format_full_value(num_deliveries)),
        "Total Quantity Supplied": (format_compact(tot_qty), format_full_value(tot_qty)),
        "Average Lead Time": (f"{avg_lead:.1f}d" if avg_lead is not None else "-", f"{avg_lead:.2f} days" if avg_lead is not None else "-"),
        "Number of Suppliers": (str(num_sups), str(num_sups)),
    }


# -----------------------------------------------------------------------------
# D1 - D7: Demand Analysis Charts
# -----------------------------------------------------------------------------
def get_demand_df(df: pd.DataFrame | None) -> tuple[pd.DataFrame, dict[str, str]]:
    """Extract demand dataframe and resolve canonical column names."""
    if df is None or df.empty:
        return pd.DataFrame(), {}
        
    c_dem = find_col(df, "Quantity_Demanded", "demand", "demand measure", "sales", "Quantity Demanded")
    c_date = find_col(df, "Date", "date")
    c_item = find_col(df, "Item_Name", "Item", "Item_ID", "item_id", "Product", "Product_Name", "item identifier")
    c_cat = find_col(df, "Category", "category", "item category", "product category")
    
    cols = {"demand": c_dem, "date": c_date, "item": c_item, "category": c_cat}
    return df.copy(), cols


def plot_d1_demand_trend(df: pd.DataFrame | None, freq: str = "daily") -> ChartResult:
    """D1: Line chart - Quantity Demanded over time with 7-day moving average.
    Supports daily or weekly aggregation toggle.
    """
    sub, cols = get_demand_df(df)
    c_dem, c_date = cols.get("demand"), cols.get("date")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_date or c_date not in sub.columns:
        return ChartResult(False, None, "Date column not in this dataset")
        
    valid = sub.dropna(subset=[c_date, c_dem]).copy()
    valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dt", "_dem"])
    if valid.empty:
        return ChartResult(False, None, "No dated demand records found")
        
    valid = valid.sort_values("_dt")
    rule = "W-MON" if freq.lower() == "weekly" else "D"
    resampled = valid.set_index("_dt").resample(rule)["_dem"].sum().reset_index()
    if resampled.empty:
        return ChartResult(False, None, "No resampled demand records found")
        
    resampled["ma7"] = resampled["_dem"].rolling(window=7, min_periods=1).mean()
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=resampled["_dt"],
            y=resampled["_dem"],
            mode="lines+markers",
            name="Demand",
            line=dict(color=COLOR_GREEN, width=2.2),
            marker=dict(size=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=resampled["_dt"],
            y=resampled["ma7"],
            mode="lines",
            name="7-Point Moving Avg",
            line=dict(color=COLOR_CYAN, width=2.2, dash="dot"),
        )
    )
    apply_ui_chart_theme(fig, height=290)
    fig.update_layout(xaxis_title="", yaxis_title="Quantity Demanded")
    return ChartResult(True, fig)


def plot_d2_demand_by_month(df: pd.DataFrame | None) -> ChartResult:
    """D2: Column chart - Quantity Demanded by month in calendar order with value labels."""
    sub, cols = get_demand_df(df)
    c_dem, c_date = cols.get("demand"), cols.get("date")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_date or c_date not in sub.columns:
        return ChartResult(False, None, "Date column not in this dataset")
        
    valid = sub.dropna(subset=[c_date, c_dem]).copy()
    valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dt", "_dem"])
    if valid.empty:
        return ChartResult(False, None, "No dated demand records found")
        
    valid["YearMonth"] = valid["_dt"].dt.to_period("M")
    valid["MonthLabel"] = valid["_dt"].dt.strftime("%b %Y")
    
    grp = valid.groupby(["YearMonth", "MonthLabel"], as_index=False)["_dem"].sum()
    grp.sort_values("YearMonth", inplace=True)
    
    months = grp["MonthLabel"].tolist()
    demands = grp["_dem"].tolist()
    text_labels = [format_compact(v) for v in demands]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=months,
                y=demands,
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_CYAN, cornerradius=6),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=270)
    fig.update_layout(xaxis_title="", yaxis_title="Quantity Demanded")
    return ChartResult(True, fig)


def plot_d3_demand_by_weekday(df: pd.DataFrame | None) -> ChartResult:
    """D3: Column chart - Average demand by weekday (Monday to Sunday in calendar order)."""
    sub, cols = get_demand_df(df)
    c_dem, c_date = cols.get("demand"), cols.get("date")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_date or c_date not in sub.columns:
        return ChartResult(False, None, "Date column not in this dataset")
        
    valid = sub.dropna(subset=[c_date, c_dem]).copy()
    valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dt", "_dem"])
    if valid.empty:
        return ChartResult(False, None, "No dated demand records found")
        
    valid["DayNum"] = valid["_dt"].dt.dayofweek
    valid["DayName"] = valid["_dt"].dt.day_name()
    
    grp = valid.groupby(["DayNum", "DayName"], as_index=False)["_dem"].mean()
    grp.sort_values("DayNum", inplace=True)
    
    days = grp["DayName"].tolist()
    avgs = grp["_dem"].tolist()
    text_labels = [format_compact(v) for v in avgs]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=days,
                y=avgs,
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_GREEN, cornerradius=6),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=260)
    fig.update_layout(xaxis_title="", yaxis_title="Average Demand")
    return ChartResult(True, fig)


def plot_d4_top_items_demand(df: pd.DataFrame | None, top_n: int = 10) -> ChartResult:
    """D4: Horizontal bar - Top items by Quantity Demanded, descending (highest at top)."""
    sub, cols = get_demand_df(df)
    c_dem, c_item = cols.get("demand"), cols.get("item")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_item or c_item not in sub.columns:
        return ChartResult(False, None, "Item column not in this dataset")
        
    valid = sub.dropna(subset=[c_item, c_dem]).copy()
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dem"])
    if valid.empty:
        return ChartResult(False, None, "No item demand records found")
        
    grp = valid.groupby(c_item, as_index=False)["_dem"].sum()
    grp = grp.sort_values(by="_dem", ascending=False).head(top_n)
    # Reverse so highest is at top of horizontal chart
    grp = grp.sort_values(by="_dem", ascending=True)
    
    items = grp[c_item].astype(str).tolist()
    demands = grp["_dem"].tolist()
    text_labels = [format_compact(v) for v in demands]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=demands,
                y=items,
                orientation="h",
                text=text_labels,
                textposition="outside",
                marker=dict(color=COLOR_CYAN, cornerradius=8),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=max(220, len(items) * 34))
    fig.update_layout(xaxis_title="Total Quantity Demanded", yaxis_title="")
    return ChartResult(True, fig)


def plot_d5_demand_by_category(df: pd.DataFrame | None) -> ChartResult:
    """D5: Donut - Quantity Demanded by Category (only if Category exists)."""
    sub, cols = get_demand_df(df)
    c_dem, c_cat = cols.get("demand"), cols.get("category")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_cat or c_cat not in sub.columns:
        return ChartResult(False, None, "Category column not in this dataset")
        
    valid = sub.dropna(subset=[c_cat, c_dem]).copy()
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dem"])
    valid = valid[valid["_dem"] > 0]
    if valid.empty:
        return ChartResult(False, None, "No categorical demand records found")
        
    grp = valid.groupby(c_cat, as_index=False)["_dem"].sum()
    grp.sort_values(by="_dem", ascending=False, inplace=True)
    
    total_dem = grp["_dem"].sum()
    cats = grp[c_cat].astype(str).tolist()
    vals = grp["_dem"].tolist()
    
    fig = go.Figure(
        data=[
            go.Pie(
                labels=cats,
                values=vals,
                hole=0.62,
                textinfo="label+percent",
                textposition="outside",
                marker=dict(colors=PALETTE),
                showlegend=False,
            )
        ]
    )
    fig.add_annotation(
        text=f"Total<br><b>{format_compact(total_dem)}</b>",
        x=0.5,
        y=0.5,
        font=dict(size=12, color=COLOR_GREEN, family="'Plus Jakarta Sans', sans-serif"),
        showarrow=False,
    )
    apply_ui_chart_theme(fig, height=280)
    return ChartResult(True, fig)


def plot_d6_weekday_month_heatmap(df: pd.DataFrame | None) -> ChartResult:
    """D6: Heatmap - weekday (rows, Mon-Sun) x month (columns, Jan-Dec) average demand."""
    sub, cols = get_demand_df(df)
    c_dem, c_date = cols.get("demand"), cols.get("date")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
    if not c_date or c_date not in sub.columns:
        return ChartResult(False, None, "Date column not in this dataset")
        
    valid = sub.dropna(subset=[c_date, c_dem]).copy()
    valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dt", "_dem"])
    if valid.empty:
        return ChartResult(False, None, "No dated demand records for heatmap")
        
    valid["DayName"] = valid["_dt"].dt.day_name()
    valid["DayNum"] = valid["_dt"].dt.dayofweek
    valid["MonthName"] = valid["_dt"].dt.strftime("%b")
    valid["MonthNum"] = valid["_dt"].dt.month
    
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = valid.pivot_table(index="DayName", columns="MonthName", values="_dem", aggfunc="mean").fillna(0)
    
    # Reindex weekdays so Monday is top row
    pivot = pivot.reindex([d for d in weekday_order if d in pivot.index])
    # Order months by calendar order
    month_order = sorted(valid["MonthNum"].unique())
    month_names = [pd.to_datetime(f"2024-{m:02d}-01").strftime("%b") for m in month_order]
    pivot = pivot.reindex(columns=[m for m in month_names if m in pivot.columns])
    
    if pivot.empty:
        return ChartResult(False, None, "Insufficient data matrix for heatmap")
        
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale=[[0, "#111726"], [0.5, "#0284C7"], [1, "#10B981"]],
            hoverongaps=False,
            colorbar=dict(
                title=dict(text="Avg Demand", font=dict(color=COLOR_MUTED, size=10)),
                tickfont=dict(color=COLOR_MUTED, size=9),
            ),
        )
    )
    apply_ui_chart_theme(fig, height=270)
    fig.update_layout(xaxis_title="", yaxis_title="")
    return ChartResult(True, fig)


def plot_d7_demand_distribution(df: pd.DataFrame | None) -> ChartResult:
    """D7: Histogram - distribution of daily Quantity Demanded."""
    sub, cols = get_demand_df(df)
    c_dem, c_date = cols.get("demand"), cols.get("date")
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return ChartResult(False, None, "Demand column not in this dataset")
        
    valid = sub.dropna(subset=[c_dem]).copy()
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dem"])
    if valid.empty:
        return ChartResult(False, None, "No numeric demand records found")
        
    # Aggregate daily if date exists, otherwise use row values
    if c_date and c_date in valid.columns:
        valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
        valid = valid.dropna(subset=["_dt"])
        if not valid.empty:
            daily_vals = valid.groupby("_dt")["_dem"].sum().values
        else:
            daily_vals = valid["_dem"].values
    else:
        daily_vals = valid["_dem"].values
        
    fig = go.Figure(
        data=[
            go.Histogram(
                x=daily_vals,
                nbinsx=20,
                marker=dict(
                    color=COLOR_VIOLET,
                    line=dict(color="rgba(255, 255, 255, 0.2)", width=1),
                ),
            )
        ]
    )
    apply_ui_chart_theme(fig, height=270)
    fig.update_layout(xaxis_title="Daily Demand Units", yaxis_title="Day Count (Frequency)")
    return ChartResult(True, fig)


def compute_demand_kpis(df: pd.DataFrame | None) -> dict[str, tuple[str, str]]:
    """Compute KPI tuple (compact_val, full_tooltip) for Demand Analysis."""
    sub, cols = get_demand_df(df)
    c_dem, c_date, c_item = cols.get("demand"), cols.get("date"), cols.get("item")
    
    if sub.empty or not c_dem or c_dem not in sub.columns:
        return {
            "Total Demand": ("-", "No demand recorded"),
            "Average Daily Demand": ("-", "No daily demand recorded"),
            "Peak Demand Day": ("-", "No peak demand found"),
            "Number of Items": ("-", "No items recorded"),
        }
        
    valid = sub.dropna(subset=[c_dem]).copy()
    valid["_dem"] = pd.to_numeric(valid[c_dem], errors="coerce")
    valid = valid.dropna(subset=["_dem"])
    if valid.empty:
        return {
            "Total Demand": ("-", "No numeric demand recorded"),
            "Average Daily Demand": ("-", "No daily demand recorded"),
            "Peak Demand Day": ("-", "No peak demand found"),
            "Number of Items": ("-", "No items recorded"),
        }
        
    total_dem = float(valid["_dem"].sum())
    num_items = valid[c_item].nunique() if (c_item and c_item in valid.columns) else len(valid)
    
    if c_date and c_date in valid.columns:
        valid["_dt"] = pd.to_datetime(valid[c_date], errors="coerce")
        valid_dated = valid.dropna(subset=["_dt"])
        if not valid_dated.empty:
            daily_grp = valid_dated.groupby(valid_dated["_dt"].dt.date)["_dem"].sum()
            avg_daily = float(daily_grp.mean())
            peak_date = str(daily_grp.idxmax())
            peak_val = float(daily_grp.max())
            peak_compact = f"{peak_date} ({format_compact(peak_val)})"
            peak_full = f"{peak_date}: {peak_val:,.0f} units"
        else:
            avg_daily = float(valid["_dem"].mean())
            peak_compact = "-"
            peak_full = "-"
    else:
        avg_daily = float(valid["_dem"].mean())
        peak_compact = "-"
        peak_full = "-"
        
    return {
        "Total Demand": (format_compact(total_dem), format_full_value(total_dem)),
        "Average Daily Demand": (format_compact(avg_daily), format_full_value(avg_daily)),
        "Peak Demand Day": (peak_compact, peak_full),
        "Number of Items": (str(num_items), str(num_items)),
    }
