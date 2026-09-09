from pathlib import Path
import hashlib
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from pypdf import PdfReader
from PIL import Image as PILImage

root = Path(__file__).resolve().parent
repo = root.parent
destination = root
data = json.loads((root/'comparison-data.json').read_text())
styles = getSampleStyleSheet()
ink = colors.HexColor('#17324d')
styles.add(ParagraphStyle(name='TitleCustom', fontName='Helvetica-Bold', fontSize=22,
                         leading=26, textColor=ink, spaceAfter=14))
styles.add(ParagraphStyle(name='BodyCustom', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=10))
styles.add(ParagraphStyle(name='Note', fontName='Helvetica', fontSize=8.5, leading=11.5,
                         textColor=colors.HexColor('#465668'), spaceAfter=9))
styles.add(ParagraphStyle(name='SectionCustom', fontName='Helvetica-Bold', fontSize=13,
                         leading=17, textColor=ink, spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name='Column', fontName='Helvetica-Bold', fontSize=10,
                         leading=13, alignment=TA_CENTER, textColor=ink, spaceAfter=6))
story = []

def p(text, style='BodyCustom'):
    return Paragraph(text, styles[style])

def add(text, style='BodyCustom'):
    story.append(p(text, style))

def table(rows, widths, size=9):
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),ink), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),size), ('LEADING',(0,0),(-1,-1),size+3),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf2f6'),colors.white]),
        ('LINEBELOW',(0,-1),(-1,-1),0.5,colors.HexColor('#bdcbd7'))]))
    story.extend([t, Spacer(1, 10)])

def img(path, width):
    w, h = PILImage.open(path).size
    return Image(str(path), width=width, height=width*h/w)

def image_pairs(rows):
    t = Table(rows, colWidths=[255.5,255.5], hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
        ('RIGHTPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#c9d4dd'))
    canvas.line(42,36,A4[0]-42,36)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#465668'))
    canvas.drawString(42,23,'FRB array review | All Dylan corrections | 9 September 2026')
    canvas.drawRightString(A4[0]-42,23,str(doc.page))
    canvas.restoreState()


add('FRB array model<br/>Before and after Dylan\'s corrections', 'TitleCustom')
add('<b>One combined revision.</b> Before means the work preceding Dylan Gormley\'s commits. '
    'After includes his August archival changes and their September extension.', 'BodyCustom')
add('Numerical boundary: <b>95d7ed5</b> (Pranav Sanghavi) to <b>16e98aa plus the complete extension</b>. '
    'The final pre-Dylan commit deleted the manuscript, so paper-before.pdf uses the last '
    'retained pre-Dylan manuscript at <b>c74d910</b>. That paper has an earlier processing-cost '
    'model. Numerical tables and paired Figure 1 panels here use 95d7ed5; see page 6.', 'Note')
add('Main conclusion', 'SectionCustom')
add('The sampled design preferences survive, but the corrected absolute rates differ '
    'substantially. All optimized frequency-doubling ratios remain below 1/4. Dishes still '
    'beat aperture tiles at the tested slopes alpha = -1.5 and -2; the optimal aperture '
    'tile at alpha = -1 remains a single dipole.')
add('Changes in absolute scale', 'SectionCustom')
add('The notebook used a daily Parkes rate under an annual label and an incorrect '
    'Boltzmann constant. At a fixed area, frequency and element count, the complete '
    'normalization correction gives these multipliers:')
table([['alpha','Days per year','Boltzmann factor','Combined factor']] +
      [[f"{r['alpha']:g}",f"{r['day_to_year']:.2f}",f"{r['boltzmann']:.5f}",f"{r['combined']:.5f}"]
       for r in data['scales']], [60,145,145,161])
add('Changes in designs and curve shapes', 'SectionCustom')
add('Your aperture-cost and budget fixes change element counts, so the full revision '
    'does <b>not</b> preserve curve shapes. After removing the scale multipliers, optimized '
    'aperture rates change by <b>-12.0% to +14.2%</b>. Dish peaks change by <b>-0.4% to +4.3%</b>. '
    'The alpha = -2, 1600 MHz dish optimum moves from the old 29.9 m<super>2</super> grid edge '
    'to <b>42.676 m<super>2</super></b>.')
add('Figure 2 and Table 1 also change', 'SectionCustom')
add('Survey uncertainties are passed as error magnitudes, the Parkes 2016 fluence threshold '
    'is consistently 4 Jy ms, and its tabulated uncertainties are corrected by a factor of '
    'ten. Figure 2 is part of this combined revision; it is not unchanged.', 'BodyCustom')

story.append(PageBreak())
add('Optimal designs and predicted rates', 'TitleCustom')
add('<b>Before:</b> the actual numbers produced by 95d7ed5, which had incorrect annual '
    'labels and budget counts. <b>After:</b> annual rates using corrected counts. Before dish '
    'optima use the 0.1 m<super>2</super> grid ending at 29.9 m<super>2</super>; after dish '
    'optima search every affordable integer count. Aperture choices use the same discrete tiles.', 'Note')
for kind in ['dish','aperture']:
    add('Dish arrays' if kind == 'dish' else 'Aperture tiles', 'SectionCustom')
    rows = [['alpha','MHz','Old area','New area','Old n','New n','Old rate','New /yr']]
    for r in data['optima']:
        if r['kind'] != kind:
            continue
        rows.append([f"{r['alpha']:g}",f"{r['frequency_MHz']:.0f}", f"{r['before_area_m2']:.3f}",
            f"{r['after_area_m2']:.3f}",str(r['before_n']),str(r['after_n']),
            f"{r['before_rate_as_printed']:,.2f}",f"{r['after_rate_per_year']:,.1f}"])
    table(rows,[42,40,65,65,47,47,82,123],size=8)
add('Areas are effective collecting areas in m<super>2</super>; n counts dishes or tiles. '
    'At alpha = -1 the dish calculation retains A &gt;= 0.1 m<super>2</super>. That '
    'mathematical minimum lies in the dashed small-dish extrapolation and is not a '
    'validated practical dish design.', 'Note')
add('Fixed-tile changes can be larger than changes in the optimum. Across all 117 aperture '
    'grid points and three slopes, rates divided by the normalization factors change by '
    '0.84683 to 6.25 times. The 6.25 maximum is at 400 MHz and m = 1444 (A = 258.19 '
    'm<super>2</super>, outside the displayed plot), where the corrected count is 20 instead of 8.', 'Note')

story.append(PageBreak())
add('Frequency and feasibility comparisons', 'TitleCustom')
add('Ratio of the optimized rate after doubling frequency', 'SectionCustom')
rows = [['Design','alpha','Frequency change','Before','After']]
for r in data['frequency_ratios']:
    rows.append([r['kind'].capitalize(),f"{r['alpha']:g}",
        f"{r['from_MHz']:.0f} to {r['to_MHz']:.0f} MHz",f"{r['before']:.6f}",f"{r['after']:.6f}"])
table(rows,[90,55,156,105,105],size=9)
add('The largest absolute change is the dish alpha = -2 ratio for 800 to 1600 MHz: '
    '0.220916 to 0.231127. The aperture ratios change because the collector-cost function '
    'and budget counts change. Uniform normalization factors cancel in these ratios.', 'Note')
add('Effective area at dish diameter d = 5 wavelengths', 'SectionCustom')
table([['Frequency','Before (m^2)','After (m^2)']] +
      [[f'{f} MHz',f'{a:.6f}',f'{b:.6f}'] for f,a,b in
       zip([400,800,1600],data['old_cutoffs_m2'],data['new_cutoffs_m2'])], [171,170,170])
add('At aperture efficiency 0.5, effective area is 0.5 pi (2.5 lambda)<super>2</super>. '
    'The previous code divided by 0.5. Corrected line-style boundaries are one-quarter '
    'the old areas; this plotting correction does not itself change rates.', 'Note')

story.append(PageBreak())
add('Figure 1: before and after', 'TitleCustom')
add('Before panels are the images committed at 95d7ed5, using its N log N processing model. '
    'After panels are regenerated from the corrected notebook. The x range expands from '
    '0-30 to 0-60 m<super>2</super>; y limits scale by the page 1 factors. Shapes also change '
    'because aperture and budget counts are corrected.', 'Note')
rows = [[p('BEFORE: 95d7ed5','Column'),p('AFTER: ALL CORRECTIONS','Column')]]
for name in ['ratevsaeff_alpha1.png','ratevsaeff_alpha15.png','ratevsaeff_alpha2.png']:
    rows.append([img(root/'before-figures'/name,250), img(repo/'paper'/name,250)])
image_pairs(rows)

story.append(PageBreak())
add('Figure 2: survey rates and uncertainty', 'TitleCustom')
add('Both panels scale the cited surveys to a common 1 Jy ms threshold using alpha = -3/2. '
    'The historical image comes from c74d910; its survey notebook is byte-identical at '
    '95d7ed5. The after panel includes your August corrections.', 'Note')
image_pairs([[p('BEFORE','Column'),p('AFTER','Column')],
             [img(root/'before-figures/frbrate_alpha15.png',250),img(repo/'paper/frbrate_alpha15.png',250)]])
add('Examples of displayed central rates and intervals', 'SectionCustom')
rows = [['Survey','Old center','Old interval','New center','New interval']]
for i in [1,4]:
    r = data['survey_comparison'][i]
    rows.append([r['survey'].split(' et')[0],f"{r['before_central']:,.0f}",
        f"{r['before_lower_endpoint']:,.0f} - {r['before_upper_endpoint']:,.0f}",
        f"{r['after_central']:,.0f}",f"{r['after_lower_endpoint']:,.0f} - {r['after_upper_endpoint']:,.0f}"])
table(rows,[70,75,145,75,146],size=8)
add('These are scaled survey rates per sky per day, not the annual model rates on page 2. '
    'Intervals are those actually drawn from the notebook\'s central value and error magnitudes.', 'Note')
add('What the correction does', 'SectionCustom')
add('<b>Error bars:</b> Matplotlib expects distances from the central value. Supplying '
    'absolute interval endpoints made the old displayed intervals wrong; the new arrays '
    'use separately scaled positive lower and upper uncertainties.')
add('<b>Parkes 2016 / Rane:</b> changing 4.4 to the cited 4 Jy ms lowers the scaled center '
    'from 40,610 to 35,200 (13.32%). Its corrected interval is 10,400-76,800. Table 1 now '
    'gives the unscaled rate as 4400 with +5200/-3100 uncertainty, replacing +520/-310.')
add('<b>Upper limits:</b> the underlying three limit values are unchanged. Arrow lengths '
    'are now proportional to the plotted values; they are presentation choices, not '
    'statistical uncertainty intervals. The other survey centers are unchanged. The '
    'legend now sits above the axes so every limit marker remains visible.', 'BodyCustom')

story.append(PageBreak())
add('Provenance and validation', 'TitleCustom')
add('The authorship boundary', 'SectionCustom')
add('<b>Before calculations:</b> 95d7ed56d345e4a4d7bd12fece20bbbf6e56615c, Pranav Sanghavi, '
    '20 May 2020. <b>After:</b> Dylan Gormley\'s 16e98aa75f74a877999536318c11dbe88209e956 '
    'plus the September corrections accompanying this report. The August checkpoint is part of the after '
    'state, not a separate paper version.', 'Note')
add('<b>Before manuscript:</b> c74d910faa1dffde60868d0f05260b2a8b1cf5f5 (v1.0), the last '
    'manuscript retained in the original repository before Dylan\'s work. It uses a '
    'linear processing approximation. The subsequent pre-Dylan notebook uses an explicit '
    'N log N term. The after paper also incorporates a later working draft restored during '
    'archiving. Therefore a paper-to-paper textual diff includes that draft history; it '
    'cannot attribute every change solely to numerical corrections.', 'Note')
add('What changes in the corrected manuscript', 'SectionCustom')
add('The abstract\'s optimum-area range extends to about 43 m<super>2</super>. Cost prose '
    'records the implemented aperture coefficient and processing terms. Figure 1 and the '
    'rate normalization use consistent annual units. Sections 5-7 give corrected yields, '
    'optima and frequency ratios. Figure 2 and Table 1 include the survey uncertainty '
    'fixes. The after PDF identifies itself as an unpublished working draft.')
add('Verification completed', 'SectionCustom')
add('Six regression tests pass: independent SI-unit rate calculation; all 1,917 modeled '
    'counts within budget and maximal; the 5-wavelength geometry; the off-grid optimum '
    'against independent numerical roots; sampled frequency/design comparisons; and '
    'canonical error magnitudes at all three slopes. Both notebooks execute successfully '
    '(20 code cells combined). Both manuscript PDFs have five pages.')
add('The before rebuild changes only TeX compatibility: removes the redundant amssymb '
    'load and unsupported table placement, and supplies an empty bibliography series field. '
    'Historical text, figures and publication placeholders remain. Its legacy equation '
    'layout warning is retained. The after manuscript resolves citations and has no '
    'overfull boxes. All delivered PDF pages were visually checked.', 'Note')
add('Scientific scope', 'SectionCustom')
add('The common normalization factors alone are 484-642; these are not small changes '
    'in absolute predictions. The qualitative conclusions above concern only the tested '
    'frequencies, slopes and cost assumptions. They do not validate the power-law '
    'extrapolation or every historical survey measurement, nor establish a preferred '
    'design for every continuous value of alpha.', 'Note')
add('Sources and reproducibility', 'SectionCustom')
add('<link href="https://academic.oup.com/mnras/article/475/2/1427/4668427" color="#174e85">Bhandari et al. (2018)</link> '
    '(daily normalization); <link href="https://academic.oup.com/mnras/article/455/2/2207/1115567" color="#174e85">Rane et al.</link> '
    '(4 Jy ms and uncertainties); <link href="https://physics.nist.gov/cuu/Constants/Table/allascii.txt" color="#174e85">NIST constants</link>; '
    '<link href="https://science.nrao.edu/opportunities/courses/era/lecture-summaries" color="#174e85">NRAO, equation 84</link> '
    '(aperture efficiency); <link href="https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.errorbar.html" color="#174e85">Matplotlib errorbar</link>. '
    'JSON and CSV files alongside this report contain the numbers. The comparison directory '
    'contains source diffs and build scripts. The corrected working draft and this report '
    'are distributed together; the v1.0 tag remains unchanged.', 'Note')

pdf = destination/'results-comparison.pdf'
doc = SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=42, leftMargin=42,
    topMargin=42, bottomMargin=48, title='FRB array model - all Dylan corrections',
    author='Repository maintenance review')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('Report pages:',len(PdfReader(str(pdf)).pages))
manifest = {p.relative_to(repo).as_posix(): {
    'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
    'pages': len(PdfReader(str(p)).pages)} for p in
    [repo/'paper/frbarray.pdf', root/'paper-before.pdf', root/'results-comparison.pdf']}
(root/'pdf-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
