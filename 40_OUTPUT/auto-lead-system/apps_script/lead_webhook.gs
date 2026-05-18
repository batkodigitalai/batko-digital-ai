/**
 * Univerzální lead webhook pro všechny landing pages.
 * Google Sheet → Rozšíření → Apps Script → vložit → Deploy → Web app.
 */
const NOTIFY_EMAIL = 'batko.digital.ai@gmail.com';
const SHEET_NAME = 'Leady';
const DEFAULT_HEADERS = ['timestamp','createdAtCZ','source','formType','pageTitle','pageUrl','name','email','phone','company','volume','budget','timeline','carInfo','note','utm_source','utm_medium','utm_campaign','utm_content','utm_term','rawJson'];

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({ok:true,message:'Auto lead webhook běží.'})).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = parsePayload_(e);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = getOrCreateSheet_(ss);
    ensureHeaders_(sheet, data);
    appendLead_(sheet, data);
    notifyOwner_(data);
    autoReply_(data);
    return json_({ok:true});
  } catch (err) {
    return json_({ok:false,error:String(err)});
  }
}

function parsePayload_(e) {
  if (!e || !e.postData || !e.postData.contents) return {};
  const raw = e.postData.contents;
  try { return JSON.parse(raw); } catch (err) { return {rawPayload: raw}; }
}

function getOrCreateSheet_(ss) {
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(SHEET_NAME);
  return sheet;
}

function ensureHeaders_(sheet, data) {
  const lastCol = Math.max(sheet.getLastColumn(), 1);
  let headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0].filter(String);
  if (headers.length === 0) headers = DEFAULT_HEADERS.slice();
  Object.keys(data || {}).forEach(k => { if (!headers.includes(k)) headers.push(k); });
  if (!headers.includes('rawJson')) headers.push('rawJson');
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.setFrozenRows(1);
}

function appendLead_(sheet, data) {
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const enriched = Object.assign({}, data, {
    createdAtCZ: Utilities.formatDate(new Date(), 'Europe/Prague', 'yyyy-MM-dd HH:mm:ss'),
    rawJson: JSON.stringify(data)
  });
  sheet.appendRow(headers.map(h => enriched[h] || ''));
}

function notifyOwner_(data) {
  const subject = 'Nový lead: ' + (data.name || 'bez jména') + ' / ' + (data.source || data.formType || 'LP');
  const body = 'Nový lead z landing page

'
    + 'Zdroj: ' + (data.source || '-') + '
'
    + 'Typ: ' + (data.formType || '-') + '
'
    + 'Jméno: ' + (data.name || '-') + '
'
    + 'Email: ' + (data.email || '-') + '
'
    + 'Telefon: ' + (data.phone || '-') + '
'
    + 'Firma: ' + (data.company || '-') + '
'
    + 'Objem: ' + (data.volume || '-') + '
'
    + 'Rozpočet: ' + (data.budget || '-') + '
'
    + 'Timing: ' + (data.timeline || '-') + '
'
    + 'Auto: ' + (data.carInfo || '-') + '
'
    + 'Poznámka: ' + (data.note || '-') + '
'
    + 'Stránka: ' + (data.pageUrl || '-') + '

'
    + 'UTM: ' + (data.utm_source || '-') + ' / ' + (data.utm_medium || '-') + ' / ' + (data.utm_campaign || '-') + '

'
    + 'Deadline odpovědi: do 24 hodin.';
  MailApp.sendEmail(NOTIFY_EMAIL, subject, body);
}

function autoReply_(data) {
  if (!data.email) return;
  const subject = 'Přijal jsem vaši poptávku na analýzu auta';
  const body = 'Dobrý den,

'
    + 'děkuji za odeslání poptávky.

'
    + 'Podívám se na zadané auto / požadavek a ozvu se vám s dalším postupem.
'
    + 'Pokud jste poslali konkrétní odkaz nebo VIN, cílem je odpověď do 24 hodin.

'
    + 'Ing. Jaroslav Batko
analýza a dovoz aut z evropských aukcí
batko.digital.ai@gmail.com';
  MailApp.sendEmail(data.email, subject, body);
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
