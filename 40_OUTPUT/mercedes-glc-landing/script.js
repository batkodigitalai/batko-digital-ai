/* =========================================================
   Mercedes-Benz GLC 300d Landing Page — v2 interactivity
   - Smooth scrolling pro anchor linky (s offsetem pro sticky header)
   - Header shadow při scrollu
   - Form validation (email + CZ/SK telefon)

   (Single-channel, takže žádné tab switching jako ve v1.)
   ========================================================= */

(function () {
    "use strict";

    /* ---------- 1) Header shadow on scroll ---------- */
    const header = document.getElementById("header");
    const SCROLL_THRESHOLD = 8;

    function onScroll() {
        if (!header) return;
        if (window.scrollY > SCROLL_THRESHOLD) {
            header.classList.add("is-scrolled");
        } else {
            header.classList.remove("is-scrolled");
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    /* ---------- 2) Smooth scrolling + offset pro sticky header ---------- */
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");
            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);
            if (!target) return;

            e.preventDefault();
            const headerHeight = header ? header.offsetHeight : 0;
            const offsetTop = target.getBoundingClientRect().top + window.scrollY - headerHeight - 8;

            window.scrollTo({
                top: offsetTop,
                behavior: "smooth"
            });
        });
    });

    /* ---------- 3) Form validation ---------- */
    const form = document.getElementById("contact-form");
    const successMsg = document.getElementById("form-success");

    // Email regex — RFC 5322-light, stačí pro UX validaci
    const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // CZ/SK telefon: +420/+421 prefix volitelný, 9 číslic; akceptuje mezery
    const PHONE_REGEX = /^(\+?42[01])?\s?\d{3}\s?\d{3}\s?\d{3}$/;

    function setError(fieldName, message) {
        const field = document.getElementById(fieldName);
        const errorEl = document.querySelector(`[data-error-for="${fieldName}"]`);
        if (field && field.parentElement) {
            field.parentElement.classList.toggle("has-error", Boolean(message));
        }
        if (errorEl) {
            errorEl.textContent = message || "";
        }
    }

    function validateField(field) {
        const name = field.name;
        const value = (field.value || "").trim();

        if (name === "name") {
            if (!value) return "Zadejte prosím své jméno.";
            if (value.length < 2) return "Jméno je příliš krátké.";
        }
        if (name === "email") {
            if (!value) return "Zadejte prosím e-mail.";
            if (!EMAIL_REGEX.test(value)) return "E-mail nemá správný formát.";
        }
        if (name === "phone") {
            if (!value) return "Zadejte prosím telefon.";
            if (!PHONE_REGEX.test(value)) return "Telefon ve formátu +420 777 123 456.";
        }
        if (name === "gdpr") {
            if (!field.checked) return "Pro odeslání je potřeba souhlas se zpracováním údajů.";
        }
        return "";
    }

    if (form) {
        // Live validation on blur — uzemnění uživatele dřív než klikne Odeslat
        form.querySelectorAll("input, select, textarea").forEach((field) => {
            field.addEventListener("blur", () => {
                const err = validateField(field);
                setError(field.name, err);
            });
        });

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const fieldsToValidate = ["name", "email", "phone", "gdpr"];
            let firstErrorField = null;
            let hasError = false;

            fieldsToValidate.forEach((fieldName) => {
                const field = form.elements[fieldName];
                if (!field) return;
                const err = validateField(field);
                setError(fieldName, err);
                if (err) {
                    hasError = true;
                    if (!firstErrorField) firstErrorField = field;
                }
            });

            if (hasError) {
                if (firstErrorField && typeof firstErrorField.focus === "function") {
                    firstErrorField.focus();
                }
                return;
            }

            // Demo "odeslání" — v reálu by tu šel fetch na backend (Formspree / vlastní endpoint).
            // POZOR: aktuálně forma neodesílá data nikam. Pro produkční nasazení doplnit.
            if (successMsg) {
                successMsg.hidden = false;
            }
            form.reset();
        });
    }
})();
