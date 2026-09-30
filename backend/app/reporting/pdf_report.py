from io import BytesIO
from html import escape
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)


def _chart_image(fig, width=6.4 * inch):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=160, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img = Image(buf)
    ratio = img.imageHeight / max(1, img.imageWidth)
    img.drawWidth = width
    img.drawHeight = min(4.2 * inch, width * ratio)
    return img


def _forecast_chart(forecast):
    if not forecast or not forecast.get('available'):
        return None
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    if forecast.get('method') == 'evidence-based-scenario':
        for name, obj in forecast.get('scenarios', {}).items():
            xs = [p['year'] for p in obj.get('series', [])]
            ys = [p['value'] for p in obj.get('series', [])]
            if xs:
                ax.plot(xs, ys, marker='o', label=name.title())
        ax.set_xlabel('Years from baseline')
        ax.legend()
    elif forecast.get('method') == 'ridge-log-trend-ml':
        rows = forecast.get('forecast', [])
        xs = [r['year'] for r in rows]
        if xs:
            ax.plot(xs, [r['predicted'] for r in rows], marker='o', label='Predicted')
            ax.plot(xs, [r['p10'] for r in rows], linestyle='--', label='P10')
            ax.plot(xs, [r['p90'] for r in rows], linestyle='--', label='P90')
            ax.legend()
        ax.set_xlabel('Year')
    else:
        plt.close(fig)
        return None
    ax.set_ylabel('Projected value')
    ax.set_title('Forecast summary')
    ax.grid(alpha=0.2)
    fig.tight_layout()
    return _chart_image(fig)


def _risk_chart(risk):
    rows = risk.get('risks', []) if risk else []
    if not rows:
        return None
    labels = [textwrap.shorten(r.get('text', 'Risk'), width=42, placeholder='...') for r in rows[:8]][::-1]
    scores = [r.get('score', 0) for r in rows[:8]][::-1]
    fig, ax = plt.subplots(figsize=(7.0, max(2.6, 0.42 * len(labels) + 1.3)))
    ax.barh(labels, scores)
    ax.set_xlim(0, 25)
    ax.set_xlabel('Risk score (likelihood × impact, max 25)')
    ax.set_title('Priority risk summary')
    ax.grid(axis='x', alpha=0.2)
    fig.tight_layout()
    return _chart_image(fig)


def _quality_chart(quality):
    if not quality:
        return None
    labels = ['Verification', 'Source quality', 'Domain diversity', 'Evidence coverage']
    values = [
        quality.get('verification_rate', 0),
        quality.get('average_source_quality', 0) * 100,
        quality.get('domain_diversity_score', 0),
        quality.get('evidence_coverage_score', 0),
    ]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    ax.bar(labels, values)
    ax.set_ylim(0, 100)
    ax.set_ylabel('Score / 100')
    ax.set_title('Research quality indicators')
    ax.grid(axis='y', alpha=0.2)
    fig.tight_layout()
    return _chart_image(fig)


def build_pdf_report(result: dict) -> bytes:
    out = BytesIO()
    doc = SimpleDocTemplate(
        out, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=46, bottomMargin=42,
        title='ResearchOps Decision Research Report'
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.black, spaceAfter=12))
    styles.add(ParagraphStyle(name='H2Black', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.black, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name='BodyBlack', parent=styles['BodyText'], fontName='Helvetica', fontSize=9.4, leading=13, textColor=colors.black, spaceAfter=6))
    styles.add(ParagraphStyle(name='SmallBlack', parent=styles['BodyText'], fontName='Helvetica', fontSize=7.6, leading=10, textColor=colors.black, spaceAfter=4))
    styles.add(ParagraphStyle(name='Callout', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.black, borderColor=colors.HexColor('#CBD5E1'), borderWidth=0.7, borderPadding=8, backColor=colors.HexColor('#F8FAFC'), spaceAfter=10))

    story = [
        Paragraph('ResearchOps Decision Research Report', styles['TitleCenter']),
        Paragraph(f"<b>Problem statement:</b> {escape(result.get('question',''))}", styles['BodyBlack']),
    ]
    opts = result.get('request_options', {})
    story.append(Paragraph(
        f"<b>Forecast horizon:</b> {opts.get('forecast_years', 5)} year(s) &nbsp;&nbsp; "
        f"<b>Processing:</b> {escape(result.get('mapreduce',{}).get('engine',''))}",
        styles['BodyBlack']))

    quality = result.get('research_quality', {})
    if quality:
        data = [
            ['Decision readiness', 'Verified findings', 'Unique domains', 'Avg. source quality'],
            [f"{quality.get('readiness_score',0)}/100 ({quality.get('band','')})", str(result.get('metrics',{}).get('verified_findings',0)), str(quality.get('unique_domains',0)), f"{quality.get('average_source_quality',0)*100:.0f}%"]
        ]
        table = Table(data, colWidths=[1.6*inch, 1.4*inch, 1.35*inch, 1.6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF2F7')),
            ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTNAME',(0,1),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#CBD5E1')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ]))
        story += [Spacer(1, 6), table, Spacer(1, 10)]
        qchart = _quality_chart(quality)
        if qchart: story += [qchart, Spacer(1, 8)]

    syn = result.get('synthesis', {})
    story += [Paragraph('Executive Summary', styles['H2Black']), Paragraph(escape(syn.get('executive_summary','No executive summary available.')), styles['BodyBlack'])]

    advice = result.get('decision_suggestion') or {}
    if advice.get('enabled'):
        story += [Paragraph('AI Decision Suggestion', styles['H2Black'])]
        story.append(Paragraph(
            f"<b>{escape(advice.get('stance',''))}</b> &nbsp; | &nbsp; Confidence: {advice.get('confidence',0)}%<br/>{escape(advice.get('summary',''))}",
            styles['Callout']))
        for r in advice.get('reasons', []):
            refs = ', '.join(r.get('source_ids', []))
            story.append(Paragraph(f"• {escape(r.get('text',''))} <font size='7'>[{escape(refs)}]</font>", styles['BodyBlack']))
        if advice.get('conditions'):
            story.append(Paragraph('<b>Conditions before acting</b>', styles['BodyBlack']))
            for x in advice['conditions']:
                story.append(Paragraph(f"• {escape(x)}", styles['BodyBlack']))
        if advice.get('next_actions'):
            story.append(Paragraph('<b>Recommended next actions</b>', styles['BodyBlack']))
            for x in advice['next_actions']:
                story.append(Paragraph(f"• {escape(x)}", styles['BodyBlack']))
        story.append(Paragraph(escape(advice.get('note','')), styles['SmallBlack']))

    story += [Paragraph('Verified Findings', styles['H2Black'])]
    for f in result.get('verified_findings', []):
        refs = ', '.join(f.get('source_ids', []))
        story.append(Paragraph(f"• {escape(f.get('claim',''))} <font size='7'>[{escape(refs)}]</font>", styles['BodyBlack']))

    story += [Paragraph('Business Opportunities', styles['H2Black'])]
    for x in syn.get('opportunities', []):
        story.append(Paragraph(f"• <b>{escape(x.get('text',''))}</b> - {escape(x.get('rationale',''))}", styles['BodyBlack']))

    risk = result.get('risk_assessment', {})
    story += [Paragraph('Risk Analysis', styles['H2Black']), Paragraph(f"Aggregate risk score: <b>{risk.get('overall_score',0)}/100 - {escape(str(risk.get('band','Unknown')))}</b>", styles['BodyBlack'])]
    rchart = _risk_chart(risk)
    if rchart: story += [rchart, Spacer(1, 8)]
    for x in risk.get('risks', []):
        story.append(Paragraph(
            f"• <b>{escape(x.get('text',''))}</b> - likelihood {x.get('likelihood',0)}/5, impact {x.get('impact',0)}/5, score {x.get('score',0)}/25. Mitigation: {escape(x.get('mitigation',''))}",
            styles['BodyBlack']))

    forecast = result.get('forecast', {})
    story += [Paragraph('Forecast', styles['H2Black']), Paragraph(escape(forecast.get('warning') or forecast.get('message','')), styles['BodyBlack'])]
    fchart = _forecast_chart(forecast)
    if fchart: story += [fchart, Spacer(1, 8)]
    if forecast.get('method') == 'evidence-based-scenario':
        rows = [['Scenario', 'Annual rate', 'End value']]
        for name, obj in forecast.get('scenarios', {}).items():
            series = obj.get('series', [])
            rows.append([name.title(), f"{obj.get('annual_rate',0)*100:.2f}%", f"{series[-1]['value']:.2f}" if series else '-'])
        t = Table(rows, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
        t.setStyle(TableStyle([('TEXTCOLOR',(0,0),(-1,-1),colors.black),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF2F7')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#CBD5E1')),('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(1,1),(-1,-1),'RIGHT')]))
        story.append(t)
    elif forecast.get('method') == 'ridge-log-trend-ml':
        rows = [['Year', 'Predicted', 'P10', 'P90']] + [[str(r['year']), f"{r['predicted']:.2f}", f"{r['p10']:.2f}", f"{r['p90']:.2f}"] for r in forecast.get('forecast', [])]
        t = Table(rows, colWidths=[1.2*inch,1.4*inch,1.4*inch,1.4*inch])
        t.setStyle(TableStyle([('TEXTCOLOR',(0,0),(-1,-1),colors.black),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF2F7')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#CBD5E1')),('FONTSIZE',(0,0),(-1,-1),8),('ALIGN',(1,1),(-1,-1),'RIGHT')]))
        story.append(t)

    story += [Paragraph('Decision Questions', styles['H2Black'])]
    for x in syn.get('decision_questions', []):
        story.append(Paragraph(f"• {escape(str(x))}", styles['BodyBlack']))

    story += [Paragraph('Limitations', styles['H2Black'])]
    for x in syn.get('limitations', []):
        story.append(Paragraph(f"• {escape(str(x))}", styles['BodyBlack']))
    story.append(Paragraph(escape(result.get('verification_note','')), styles['SmallBlack']))

    story += [PageBreak(), Paragraph('Source Register', styles['H2Black'])]
    for s in result.get('source_catalog', []):
        url = escape(s.get('url',''), quote=True)
        title = escape(s.get('title','Untitled'))
        domain = escape(s.get('domain',''))
        sid = escape(s.get('source_id',''))
        story.append(Paragraph(f"<b>{sid}</b> - {title} - {domain}<br/><link href='{url}' color='black'>{url}</link>", styles['SmallBlack']))

    doc.build(story)
    return out.getvalue()
