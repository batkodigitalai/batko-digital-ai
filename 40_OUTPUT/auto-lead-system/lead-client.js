// lead-client.js — univerzální odesílání leadů do Google Apps Script
(function () {
  function getParam(name) {
    return new URLSearchParams(window.location.search).get(name) || '';
  }
  function getConfig() { return window.LEAD_CONFIG || {}; }
  async function submitLead(form, options) {
    const cfg = getConfig();
    const endpoint = cfg.APPS_SCRIPT_URL || '';
    if (!endpoint || endpoint.indexOf('PASTE_') !== -1) throw new Error('Chybí APPS_SCRIPT_URL v config.js');
    const formData = new FormData(form);
    const data = {
      timestamp: new Date().toISOString(),
      pageUrl: window.location.href,
      pageTitle: document.title,
      source: options.source || formData.get('source') || cfg.DEFAULT_SOURCE || 'unknown',
      formType: formData.get('formType') || options.formType || '',
      utm_source: getParam('utm_source'),
      utm_medium: getParam('utm_medium'),
      utm_campaign: getParam('utm_campaign'),
      utm_content: getParam('utm_content'),
      utm_term: getParam('utm_term')
    };
    for (const [k, v] of formData.entries()) data[k] = v;
    await fetch(endpoint, { method: 'POST', mode: 'no-cors', headers: {'Content-Type':'text/plain;charset=utf-8'}, body: JSON.stringify(data) });
    if (typeof gtag !== 'undefined') gtag('event', 'lead_submit', { form_type: data.formType, source: data.source });
    if (typeof fbq !== 'undefined') fbq('track', 'Lead');
    return data;
  }
  function bindLeadForm(formId, options) {
    const form = document.getElementById(formId || 'leadForm');
    if (!form) return;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const btn = document.getElementById('submitBtn') || form.querySelector('button[type="submit"]');
      const successMsg = document.getElementById('successMsg');
      const errorMsg = document.getElementById('errorMsg');
      const emailEcho = document.getElementById('emailEcho');
      if (btn) { btn.disabled = true; btn.textContent = 'Odesílám...'; }
      if (successMsg) successMsg.classList.remove('show');
      if (errorMsg) errorMsg.classList.remove('show');
      try {
        const data = await submitLead(form, options || {});
        if (emailEcho) emailEcho.textContent = data.email || '';
        if (successMsg) successMsg.classList.add('show');
        form.style.display = 'none';
      } catch (err) {
        console.error(err);
        if (errorMsg) errorMsg.classList.add('show');
        alert('Formulář se nepodařilo odeslat. Zkuste to znovu nebo napište na batko.digital.ai@gmail.com.');
        if (btn) { btn.disabled = false; btn.textContent = 'Zkusit znovu →'; }
      }
    });
  }
  window.LeadSystem = { bindLeadForm };
})();
