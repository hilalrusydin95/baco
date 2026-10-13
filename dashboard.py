from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd

# 1. Membaca dataset CSV
df = pd.read_csv('dataset_fiskal_97_hipoFull (1).csv')
df = df.sort_values(by=['Kota', 'Tahun'])

# Daftar pilihan kota dan tahun
daftar_kota = sorted(df['Kota'].unique())
min_tahun = int(df['Tahun'].min())
max_tahun = int(df['Tahun'].max())

# Kolom indikator untuk pilihan dropdown
kolom_kecuali = ['Kota', 'Tahun']
daftar_indikator = [col for col in df.columns if col not in kolom_kecuali]
options_indikator = [{'label': col.replace('_', ' ').upper(), 'value': col} for col in daftar_indikator]

# Inisialisasi aplikasi Dash
app = Dash(__name__)
server = app.server

# 2. Desain Layout Profesional Berbasis Narasi Data
app.layout = html.Div([
    # Header Utama
    html.Div([
        html.H1("Kajian Komprehensif Fiskal & Kinerja Pembangunan Daerah", 
                style={'color': '#0F172A', 'margin': '0', 'fontSize': '24px', 'fontWeight': '700'}),
        html.P("Analisis mendalam hubungan antara kemandirian fiskal (PAD), alokasi belanja modal, dan indeks kesejahteraan masyarakat.", 
               style={'color': '#475569', 'margin': '8px 0 0 0', 'fontSize': '14px'}),
    ], style={'backgroundColor': '#FFFFFF', 'padding': '30px', 'borderRadius': '12px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)'}),

    # Panel Filter & Kontrol
    html.Div([
        html.Div([
            html.Label("Wilayah Observasi Utama:", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '6px', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-kota-utama',
                options=[{'label': k, 'value': k} for k in daftar_kota],
                value='Kota Makassar',
                clearable=False,
                style={'borderRadius': '6px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.Label("Wilayah Pembanding (Opsional):", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '6px', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-kota-pembanding',
                options=[{'label': k, 'value': k} for k in daftar_kota],
                value=None,
                clearable=True,
                placeholder="Pilih wilayah pembanding...",
                style={'borderRadius': '6px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label("Fokus Indikator Analisis:", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '6px', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-indikator',
                options=options_indikator,
                value='PAD',
                clearable=False,
                style={'borderRadius': '6px'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%', 'verticalAlign': 'top'})
    ], style={'backgroundColor': '#FFFFFF', 'padding': '20px 25px', 'borderRadius': '12px', 'marginBottom': '20px', 'border': '1px solid #E2E8F0'}),

    # Range Slider Tahun
    html.Div([
        html.Label("Rentang Waktu Pengamatan:", style={'fontWeight': '600', 'color': '#334155', 'display': 'block', 'marginBottom': '10px', 'fontSize': '13px'}),
        dcc.RangeSlider(
            id='slider-tahun',
            min=min_tahun,
            max=max_tahun,
            step=1,
            value=[min_tahun, max_tahun],
            marks={str(y): str(y) for y in range(min_tahun, max_tahun + 1, 2)}
        )
    ], style={'backgroundColor': '#FFFFFF', 'padding': '15px 25px', 'borderRadius': '12px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0'}),

    # Kotak Narasi Data (Insight Storytelling Box)
    html.Div(id='storytelling-box', style={'backgroundColor': '#F8FAFC', 'borderLeft': '4px solid #2563EB', 'padding': '20px 25px', 'borderRadius': '8px', 'marginBottom': '25px', 'border': '1px solid #E2E8F0', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)'}),

    # Kartu Metrik Ringkasan (KPI Cards)
    html.Div(id='kpi-cards-container', style={'display': 'flex', 'gap': '20px', 'marginBottom': '25px'}),

    # Navigasi Tab Visualisasi & Komposisi Belanja
    dcc.Tabs(id='tabs-story', value='tab-tren', children=[
        dcc.Tab(label='📊 Analisis Tren & Dinamika Indikator', value='tab-tren', style={'fontWeight': 'bold'}, selected_style={'fontWeight': 'bold', 'color': '#2563EB'}),
        dcc.Tab(label='🏗️ Alokasi Belanja Sektoral (Modal)', value='tab-belanja', style={'fontWeight': 'bold'}, selected_style={'fontWeight': 'bold', 'color': '#2563EB'}),
        dcc.Tab(label='📋 Tabel Data & Arsip Rinci', value='tab-tabel', style={'fontWeight': 'bold'}, selected_style={'fontWeight': 'bold', 'color': '#2563EB'}),
    ], style={'marginBottom': '20px'}),

    # Konten Dinamis Tab
    html.Div(id='konten-tab-story'),

    # Footer
    html.Div([
        html.P("Pusat Data Kebijakan Fiskal Daerah | Dikembangkan dengan Python Dash & Plotly", 
               style={'textAlign': 'center', 'color': '#94A3B8', 'fontSize': '12px', 'marginTop': '40px'})
    ])
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1250px', 'margin': '0 auto', 'padding': '25px', 'backgroundColor': '#F1F5F9', 'minHeight': '100vh'})


# 3. Callback Utama untuk Narasi Data dan Grafik
@app.callback(
    [Output('storytelling-box', 'children'),
     Output('kpi-cards-container', 'children'),
     Output('konten-tab-story', 'children')],
    [Input('dropdown-kota-utama', 'value'),
     Input('dropdown-kota-pembanding', 'value'),
     Input('dropdown-indikator', 'value'),
     Input('slider-tahun', 'value'),
     Input('tabs-story', 'value')]
)
def update_dashboard_story(kota_utama, kota_pembanding, indikator, rentang_tahun, active_tab):
    df_f = df[(df['Tahun'] >= rentang_tahun[0]) & (df['Tahun'] <= rentang_tahun[1])]
    df_utama = df_f[df_f['Kota'] == kota_utama]
    
    # Membuat Narasi / Storytelling Otomatis berdasarkan Data
    story_content = "Memuat analisis naratif data..."
    if not df_utama.empty and indikator in df_utama.columns:
        val_awal = df_utama.iloc[0][indikator]
        val_akhir = df_utama.iloc[-1][indikator]
        thn_awal = int(df_utama.iloc[0]['Tahun'])
        thn_akhir = int(df_utama.iloc[-1]['Tahun'])
        
        perubahan = val_akhir - val_awal
        persentase = (perubahan / val_awal * 100) if val_awal != 0 else 0
        arah = "menunjukkan tren kenaikan" if perubahan >= 0 else "mengalami koreksi penurunan"
        
        avg_ipm = df_utama['IPM'].mean() if 'IPM' in df_utama.columns else 0
        avg_pe = df_utama['PE'].mean() if 'PE' in df_utama.columns else 0

        story_content = [
            html.H4(f"📖 Ringkasan Eksekutif & Karakteristik Data: {kota_utama}", style={'color': '#1E293B', 'margin': '0 0 8px 0', 'fontSize': '16px'}),
            html.P([
                f"Selama periode pengamatan dari tahun ", html.B(f"{thn_awal}"), f" hingga ", html.B(f"{thn_akhir}"), 
                f", indikator ", html.B(f"{indikator.replace('_', ' ').upper()} di {kota_utama} "),
                f"{arah} sebesar ", html.B(f"{abs(persentase):.2f}% "),
                f"(dari {val_awal:,.2f} pada awal tahun menjadi {val_akhir:,.2f} pada akhir periode). ",
                f"Secara makro, wilayah ini mencatat rata-rata Indeks Pembangunan Manusia (IPM) sebesar ", html.B(f"{avg_ipm:,.2f}"),
                f" dengan rata-rata Pertumbuhan Ekonomi (PE) di kisaran ", html.B(f"{avg_pe:,.2f}%"), f"."
            ], style={'color': '#334155', 'margin': '0', 'fontSize': '14px', 'lineHeight': '1.5'})
        ]

    # Kartu Metrik Utama
    latest_row = df_utama.iloc[-1] if not df_utama.empty else None
    kpi_cards = []
    if latest_row is not None and indikator in latest_row:
        val_terkini = latest_row[indikator]
        mean_val = df_utama[indikator].mean()
        
        metrics = [
            ("Wilayah Analisis", f"{kota_utama}", "#0F172A"),
            (f"Rata-Rata {indikator.replace('_', ' ').upper()}", f"{mean_val:,.2f}", "#2563EB"),
            (f"Nilai Terkini ({int(latest_row['Tahun'])})", f"{val_terkini:,.2f}", "#059669"),
            ("Capaian IPM Terakhir", f"{latest_row['IPM']:,.2f}", "#D97706")
        ]
        for title, val, color in metrics:
            kpi_cards.append(
                html.Div([
                    html.P(title, style={'margin': '0', 'color': '#64748B', 'fontSize': '12px', 'fontWeight': '600'}),
                    html.H3(val, style={'margin': '6px 0 0 0', 'color': color, 'fontSize': '18px', 'fontWeight': 'bold'})
                ], style={'flex': '1', 'backgroundColor': '#FFFFFF', 'padding': '15px 20px', 'borderRadius': '8px', 'borderLeft': f'4px solid {color}', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)', 'border': '1px solid #E2E8F0'})
            )

    # Konten Tab
    konten = []
    if active_tab == 'tab-tren':
        if kota_pembanding:
            df_gabung = df_f[df_f['Kota'].isin([kota_utama, kota_pembanding])]
            fig = px.line(
                df_gabung, x='Tahun', y=indikator, color='Kota', markers=True,
                title=f"Analisis Komparatif [{indikator.replace('_', ' ').upper()}]: {kota_utama} vs {kota_pembanding}",
                template='plotly_white'
            )
        else:
            fig = px.line(
                df_utama, x='Tahun', y=indikator, markers=True,
                title=f"Dinamika Historis [{indikator.replace('_', ' ').upper()}] di {kota_utama}",
                template='plotly_white'
            )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(title_font_size=15, title_font_color='#1E293B')
        konten = html.Div([dcc.Graph(figure=fig)], style={'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #E2E8F0', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)'})

    elif active_tab == 'tab-belanja':
        fig = px.bar(
            df_utama, x='Tahun', 
            y=['bm_pendidikan', 'bm_kesehatan', 'bm_infrastruktur', 'bm_ekonomi'],
            title=f"Komposisi Alokasi Belanja Modal Sektoral di {kota_utama}",
            barmode='group',
            labels={'value': 'Nilai Anggaran', 'variable': 'Sektor Belanja'},
            template='plotly_white'
        )
        fig.update_layout(title_font_size=15, title_font_color='#1E293B', legend_title='Sektor Prioritas')
        konten = html.Div([dcc.Graph(figure=fig)], style={'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #E2E8F0', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)'})

    elif active_tab == 'tab-tabel':
        table_data = df_utama.to_dict('records')
        columns = [{"name": c.replace('_', ' ').upper(), "id": c} for c in df.columns]
        konten = html.Div([
            html.H4(f"Arsip Data Rinci: {kota_utama}", style={'color': '#1E293B', 'marginBottom': '15px'}),
            dash_table.DataTable(
                data=table_data,
                columns=columns,
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#1E293B', 'color': 'white', 'fontWeight': 'bold'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': 'Arial', 'minWidth': '120px'}
            )
        ], style={'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '8px', 'border': '1px solid #E2E8F0', 'boxShadow': '0 1px 3px rgba(0,0,0,0.02)'})

    return story_content, kpi_cards, konten


if __name__ == '__main__':
    app.run(debug=True)