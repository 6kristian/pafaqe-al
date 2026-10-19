#!/usr/bin/env python3
"""Apply all fixes to index.html.   Usage: python apply_patches.py index.html
All-or-nothing: if any anchor doesn't match your file, nothing is written and the misses are listed.
A backup is saved as index.html.bak first."""
import re, shutil, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
raw = open(path, encoding='utf-8', newline='').read()
crlf = '\r\n' in raw
s = raw.replace('\r\n', '\n')
fails = []


def sub(old, new, n=1):
    global s
    c = s.count(old)
    if c != n:
        fails.append(f'text {old[:70]!r}: found {c}x, expected {n}')
        return
    s = s.replace(old, new)


def rx(pat, new, n=1, flags=0):
    global s
    s, c = re.subn(pat, lambda m: new, s, flags=flags)
    if c != n:
        fails.append(f'regex {pat[:70]!r}: matched {c}x, expected {n}')


def cut(a, b, insert=''):
    global s
    i, j = s.find(a), s.find(b)
    if i < 0 or j < i:
        fails.append(f'cut {a[:50]!r} .. {b[:30]!r} not found')
        return
    s = s[:i] + insert + s[j:]


# ---------------------------------------------------------------- head / copy
sub('<html lang="sq" class="dark">', '<html lang="en" class="dark">')
sub('Ready-made web design leads with phone numbers and ratings.', 'Ready-made web design leads with phone numbers.')
sub('<link rel="icon" type="image/x-icon" href="favicon.ico">',
    '<meta property="og:title" content="PaFaqe.al \u2014 Albanian Businesses Without a Website">\n'
    '<meta property="og:description" content="Local Albanian businesses with no website listed: phone numbers and lead scores for web designers.">\n'
    '<meta property="og:type" content="website">\n'
    '<link rel="icon" type="image/x-icon" href="favicon.ico">')
sub('title="Toggle Light/Dark Theme"', 'title="Toggle Light/Dark Theme" aria-label="Toggle light/dark theme"')
sub('Discover verified local businesses', 'Discover local businesses')
sub('>without a website</b>. Access direct phone numbers, lead scoring, and instant WhatsApp outreach tools.',
    '>with no website listed on OpenStreetMap</b>. Access phone numbers, lead scoring, and WhatsApp pitch tools.')
sub('Unlock All Verified Albanian Leads', 'Unlock All Albanian Leads')
sub('Loading verified leads...', 'Loading leads...')
sub('providing accurate contact details, categories, and lead scoring',
    'providing phone numbers where available, categories, and lead scoring')
sub('<p>Created and maintained by <b>Kristian Frroku</b>.</p>',
    '<p>Created and maintained by <b>Kristian Frroku</b>.</p>\n'
    '          <p class="mt-2">Data \u00a9 <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener" class="underline">OpenStreetMap contributors</a>, '
    'available under the ODbL. "No website" means no website is tagged in OpenStreetMap, so some of these businesses may have one. '
    'To correct or remove a listing, use the Contact tab.</p>')
sub('<p class="text-[11px] subtext mt-0.5">\u00a9 2026 Developed by <b class="text-amber-500 dark:text-amber-400">Kristian Frroku</b></p>',
    '<p class="text-[11px] subtext mt-0.5">\u00a9 2026 Developed by <b class="text-amber-500 dark:text-amber-400">Kristian Frroku</b></p>\n'
    '    <p class="text-[11px] subtext mt-0.5">Data \u00a9 <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener" class="underline">OpenStreetMap contributors</a> (ODbL)</p>')

# ---------------------------------------------------------------- ratings don't exist in the data
sub('<option value="rating">Sort: Rating (High\u2192Low)</option>', '')
sub('<div class="flex items-center gap-2 ml-auto sm:ml-0">', '<div class="hidden">')
sub('<th class="w-[9%] px-3 sm:px-4 py-3 font-semibold">Rating</th>', '')
rx(r'^[ \t]*<td[^\n]*\$\{b\.rating \?[^\n]*\n', '', flags=re.M)
sub("'<span class=\"subtext\">\u2014</span>'", "`<span class=\"subtext\">${escapeHtml(b.phone_masked || '\u2014')}</span>`")

# ---------------------------------------------------------------- niche chips (no hotel categories exist in the data)
sub("quickNicheFilter('Hotel')", "quickNicheFilter('Travel')")
sub('\U0001F3E8 Hotels & Tourism', '\U0001F9F3 Travel Agencies')
sub("quickNicheFilter('Dental')", "quickNicheFilter('Dentist')")
sub("quickNicheFilter('Auto')", "quickNicheFilter('Car')")
sub('function quickNicheFilter(keyword) {', 'function quickNicheFilter(keyword) {\n  if (!currentUser) { openAuthModal(); return; }')

# ---------------------------------------------------------------- real paywall: guests get the preview, verified users get Firestore chunks
rx(r"fetch\('leads\.json'\)\s*\.then\(r => r\.ok \? r\.json\(\) : Promise\.reject\(\)\)\s*"
   r"\.then\(j => \{ DATA = j; init\(\); \}\)\s*\.catch\(\(\) => \{ DATA = DEMO; init\(\); \}\);",
   r'''let PREVIEW = null, FULL_LOADED = false;
const previewPromise = fetch('leads-preview.json')
  .then(r => r.ok ? r.json() : Promise.reject())
  .then(j => { PREVIEW = j; if (!FULL_LOADED) { DATA = j; init(); } })
  .catch(() => {
    document.getElementById('rows').innerHTML = '<tr><td colspan="10" class="p-16 text-center subtext">Could not load leads. <button onclick="location.reload()" class="underline text-amber-500">Retry</button></td></tr>';
  });''')
sub('await loadCloudData();', 'await loadCloudData();\n    loadFullLeads();')
sub('if (btn) btn.innerHTML = `<span>Sign In</span>`;',
    'if (btn) btn.innerHTML = `<span>Sign In</span>`;\n    FULL_LOADED = false; selectedLeads.clear(); showVerifyNotice(false);\n    if (PREVIEW) DATA = PREVIEW;')
sub('function leadScore(b){', 'function leadScore(b){\n  if (typeof b.score === \'number\') return b.score;')
sub("if (sAvg) sAvg.textContent = sc.length ? Math.round(sc.reduce((a,c) => a + c, 0) / sc.length) : 0;",
    "if (sAvg) sAvg.textContent = sc.length ? Math.round(sc.reduce((a,c) => a + c, 0) / sc.length) : 0;\n"
    "  if (!FULL_LOADED && DATA.stats) {\n"
    "    if (sLeads) sLeads.textContent = DATA.stats.leads.toLocaleString();\n"
    "    if (sCities) sCities.textContent = DATA.stats.cities;\n"
    "    if (sAvg) sAvg.textContent = DATA.stats.avg;\n  }")
sub('${DATA.businesses.length.toLocaleString()} businesses',
    '${(DATA.stats ? DATA.stats.leads : DATA.businesses.length).toLocaleString()} businesses')

# ---------------------------------------------------------------- remove the fake "automated email" reminder, add the leads loader
rx(r'[ \t]*//[^\n]*Automated Email Reminder Trigger[^\n]*\n', '')
rx(r'[ \t]*if \(dueRemindersCount > 0 && [^\n]*\n[^\n]*\n[^\n]*\n[ \t]*\}\n', '')
cut('// Function to send automated email reminder via Web3Forms API', 'function getLeadStatus(id) {', r'''async function loadFullLeads() {
  await previewPromise;
  if (!currentUser) return;
  try {
    await currentUser.reload();
    if (!currentUser.emailVerified) { renderVerificationStatus(); showVerifyNotice(true); return; }
    showVerifyNotice(false);
    await currentUser.getIdToken(true);
    const snap = await db.collection('lead_chunks').orderBy(firebase.firestore.FieldPath.documentId()).get();
    const rows = [];
    snap.forEach(d => rows.push(...(d.data().rows || [])));
    if (!rows.length || !currentUser) return;
    DATA = { source: 'live', businesses: rows };
    FULL_LOADED = true;
    init();
  } catch (err) { console.error('Error loading leads:', err); }
}

function showVerifyNotice(on) {
  let el = document.getElementById('verifyNotice');
  if (!el) {
    if (!on) return;
    el = document.createElement('div');
    el.id = 'verifyNotice';
    el.className = 'p-4 rounded-2xl card-bg border border-amber-500/50 text-xs sm:text-sm flex flex-wrap items-center justify-between gap-3';
    el.innerHTML = '<span>Verify your email to unlock all leads. Check your inbox (and spam), then reload this page.</span><button onclick="resendVerificationEmail()" class="px-3 py-1.5 rounded-lg card-bg border text-xs font-semibold">Resend email</button>';
    document.getElementById('tabLeads').prepend(el);
  }
  el.classList.toggle('hidden', !on);
}

''')

# ---------------------------------------------------------------- bugs
rx(r"errBox\.textContent = err\.message;\s*errBox\.classList\.add\('hidden'\);",
   "errBox.textContent = err.message;\n      errBox.classList.remove('hidden');", n=2)
sub("((b.reviews || 0) - (b.reviews || 0))", "((b.reviews || 0) - (a.reviews || 0))")
sub('href="${escapeHtml(b.website)}"', r'''href="${/^https?:\/\//i.test(b.website) ? escapeHtml(b.website) : '#'}"''')

# ---------------------------------------------------------------- phones / WhatsApp / pitch
sub('const waLink = getWhatsAppLink(b.phone);', 'const waLink = b.mobile ? getWhatsAppLink(b.phone) : null;')
sub('if (waBtn) waBtn.href = waUrl;',
    "window._pitchWa = formatted ? `https://wa.me/${formatted}` : 'https://wa.me/';\n"
    "  if (waBtn) { waBtn.href = waUrl; waBtn.classList.toggle('hidden', !b.mobile); }")
sub('rows="6" readonly class="w-full card-bg border rounded-xl p-3 text-xs font-mono select-all outline-none"',
    '''rows="6" oninput="document.getElementById('whatsappSendBtn').href=(window._pitchWa||'https://wa.me/')+'?text='+encodeURIComponent(this.value)" class="w-full card-bg border rounded-xl p-3 text-xs font-mono outline-none"''')

# ---------------------------------------------------------------- CSV export
sub('phone,rating,reviews,website,lead_score', 'phone,mobile,website,lead_score')
rx(r"return \[\s*`\"\$\{\(b\.name.*?\]\.join\(','\);",
   r'''const q = s => { s = String(s || ''); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
    return [q(b.name), q(b.category), q(b.city), q(b.address), excelPhone, b.mobile ? 'yes' : 'no', q(b.website), leadScore(b)].join(',');''',
   flags=re.S)

# ---------------------------------------------------------------- cookie banner, contact form, accessibility
sub('<button onclick="acceptCookies()" class="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold transition cursor-pointer">Prano t\u00eb gjitha</button>',
    '<button onclick="declineCookies()" class="px-4 py-2 rounded-xl card-bg border font-bold transition cursor-pointer">Refuzo</button>\n'
    '    <button onclick="acceptCookies()" class="px-4 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold transition cursor-pointer">Prano t\u00eb gjitha</button>')
sub('function checkCookieConsent() {',
    "function declineCookies() {\n  setCookie('pafaqe_cookie_consent', 'declined', 365);\n"
    "  const b = document.getElementById('cookieBanner');\n  if (b) b.classList.add('hidden');\n}\n\nfunction checkCookieConsent() {")
sub('<form onsubmit="handleContactSubmit(event)" class="space-y-4">',
    '<form onsubmit="handleContactSubmit(event)" class="space-y-4">\n          <input type="checkbox" id="botcheck" style="display:none" tabindex="-1" autocomplete="off">')
sub('subject: `New Message from ${name} via PaFaqe.al`,',
    "subject: `New Message from ${name} via PaFaqe.al`,\n        botcheck: document.getElementById('botcheck').checked,")
for m in ('authModal', 'forgotPasswordModal', 'notesModal', 'pitchModal'):
    sub(f'id="{m}" class="hidden fixed', f'id="{m}" role="dialog" aria-modal="true" class="hidden fixed')
sub('function escapeHtml(str) {',
    "document.addEventListener('keydown', e => {\n  if (e.key !== 'Escape') return;\n"
    "  closeAuthModal(); closeForgotPasswordModal(); closeNotesModal(); closePitchModal();\n});\n\nfunction escapeHtml(str) {")

# ---------------------------------------------------------------- write
if fails:
    print('NOTHING WRITTEN. These patches did not match your file:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
shutil.copyfile(path, path + '.bak')
open(path, 'w', encoding='utf-8', newline='').write(s.replace('\n', '\r\n') if crlf else s)
print('OK: patched', path, '(backup:', path + '.bak)')
