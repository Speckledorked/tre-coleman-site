/*
 * Exit‑Intent Pop‑Up for TreColeman.com
 *
 * This script listens for exit‑intent behaviour (mouse moving toward the top
 * of the viewport) and displays a modal offering one of two free lead
 * magnets: the Operations Audit or the 90‑Day AI & Operations Playbook. To
 * encourage sign‑ups it uses a compelling headline, social proof and
 * responsive design matching the brand colours. The pop‑up only appears
 * once per session, uses simple FormSubmit forms for lead capture and
 * supports basic A/B testing by randomly emphasising either offer.
 *
 * How to use:
 * 1. Include a script tag loading this file just before the closing
 *    </body> tag of your pages.
 * 2. Ensure there is no conflicting element with ids
 *    `exitIntentOverlay` or `exitIntentModal` in your markup.
 */
// Crisp Chat Integration
window.$crisp=[];
window.CRISP_WEBSITE_ID="be57159b-af24-45a1-8e47-1207df3715lf";
(function(){
  var d=document,s=d.createElement("script");
  s.src="https://client.crisp.chat/l.js";
  s.async=1;
  d.getElementsByTagName("head")[0].appendChild(s);
})();


(function () {
  const SESSION_KEY = 'tre_exit_intent_shown';
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (sessionStorage.getItem(SESSION_KEY)) return;

  let shown = false;

  /**
   * Append the pop‑up HTML and CSS to the document. Randomly choose a
   * variant (audit‑focused or playbook‑focused) for A/B testing.
   */
  function showExitPopup() {
    if (shown) return;
    shown = true;
    sessionStorage.setItem(SESSION_KEY, 'true');

    //     // Decide which variant to emphasise using sessionStorage
    const VARIANT_KEY = 'exit_intent_variant';
    let variant = sessionStorage.getItem(VARIANT_KEY);
    if (!variant) {
      variant = Math.random() < 0.5 ? 'audit' : 'playbook';
      sessionStorage.setItem(VARIANT_KEY, variant);
    }
    const emphasiseAudit = variant === 'audit';
    

    // Base colours – update these to match your palette
    const primaryColour = '#2c5f2d';
    const secondaryColour = '#97bc62';
    const accentColour = '#e3b448';

    // Inline CSS for the overlay and modal. Using inline styles avoids
    // requiring a separate stylesheet and keeps the pop‑up self contained.
    const style = document.createElement('style');
    style.setAttribute('id', 'exitIntentStyles');
    style.textContent = `
      #exitIntentOverlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        padding: 1rem;
        overflow-y: auto;
      }
      #exitIntentModal {
        background: #ffffff;
        border-radius: 8px;
        max-width: 500px;
        width: 100%;
        padding: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        position: relative;
        text-align: center;
        font-family: inherit;
      }
      #exitIntentModal h2 {
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        color: ${primaryColour};
      }
      #exitIntentModal p.social-proof {
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #555;
      }
      #exitIntentModal .offers {
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      #exitIntentModal .offer {
        border: 1px solid ${primaryColour};
        border-radius: 6px;
        padding: 1rem;
      }
      #exitIntentModal .offer h3 {
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
        color: ${primaryColour};
      }
      #exitIntentModal .offer form {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-top: 0.5rem;
      }
      #exitIntentModal .offer input[type="text"],
      #exitIntentModal .offer input[type="email"],
      #exitIntentModal .offer textarea {
        padding: 0.5rem;
        font-size: 0.9rem;
        border: 1px solid #ccc;
        border-radius: 4px;
      }
      #exitIntentModal .offer button {
        background: ${primaryColour};
        color: #fff;
        border: none;
        padding: 0.6rem;
        font-size: 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s ease;
      }
      #exitIntentModal .offer button:hover {
        background: ${secondaryColour};
      }
      #exitIntentModal .close-btn {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: transparent;
        border: none;
        font-size: 1.5rem;
        color: ${primaryColour};
        cursor: pointer;
      }
      #exitIntentModal a.no-thanks {
        display: inline-block;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        color: ${primaryColour};
        text-decoration: underline;
        cursor: pointer;
      }
      @media (max-width: 480px) {
        #exitIntentModal {
          padding: 1rem;
        }
      }
    `;
    document.head.appendChild(style);

    // Build overlay element
    const overlay = document.createElement('div');
    overlay.id = 'exitIntentOverlay';

    // Build modal element
    const modal = document.createElement('div');
    modal.id = 'exitIntentModal';

    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', function () {
      document.body.removeChild(overlay);
    });

    // Heading and social proof
    const heading = document.createElement('h2');
    heading.textContent = emphasiseAudit
      ? "Wait! Don't miss your free profit analysis"
      : "Wait! Your free playbook is inside";
    const social = document.createElement('p');
    social.className = 'social-proof';
    social.textContent = 'Join 500+ restaurant operators who already use these tools';

    // Build offers container
    const offersContainer = document.createElement('div');
    offersContainer.className = 'offers';

    // Helper to create each offer block
    function createOffer(options) {
      const { title, subject, nextUrl, autoResponse, primary } = options;
      const offerDiv = document.createElement('div');
      offerDiv.className = 'offer';
      // Title
      const h3 = document.createElement('h3');
      h3.textContent = title;
      offerDiv.appendChild(h3);
      // Form
      const form = document.createElement('form');
      form.action = 'https://formsubmit.co/hello@trecoleman.com';
      form.method = 'POST';
      form.setAttribute('novalidate', '');
      // Name field
      const nameInput = document.createElement('input');
      nameInput.type = 'text';
      nameInput.name = 'name';
      nameInput.placeholder = 'Name';
      nameInput.required = true;
      form.appendChild(nameInput);
      // Email field
      const emailInput = document.createElement('input');
      emailInput.type = 'email';
      emailInput.name = 'email';
      emailInput.placeholder = 'Email';
      emailInput.required = true;
      form.appendChild(emailInput);
      // Hidden fields
      const subjectField = document.createElement('input');
      subjectField.type = 'hidden';
      subjectField.name = '_subject';
      subjectField.value = subject;
      form.appendChild(subjectField);
      const nextField = document.createElement('input');
      nextField.type = 'hidden';
      nextField.name = '_next';
      nextField.value = nextUrl;
      form.appendChild(nextField);
      const captchaField = document.createElement('input');
      captchaField.type = 'hidden';
      captchaField.name = '_captcha';
      captchaField.value = 'false';
      form.appendChild(captchaField);
      const autoResponseField = document.createElement('input');
      autoResponseField.type = 'hidden';
      autoResponseField.name = '_autoresponse';
      autoResponseField.value = autoResponse;
      form.appendChild(autoResponseField);
      // Button
      const submitButton = document.createElement('button');
      submitButton.type = 'submit';
      submitButton.textContent = title;
      form.appendChild(submitButton);
      // Append form
      offerDiv.appendChild(form);
      return offerDiv;
    }
        // Define offers
            // Define offers
    const auditOffer = {
      title: 'Free Operations Audit',
      subject: 'New Operations Audit (Exit Intent)',
      nextUrl: 'https://trecoleman.com/audit.html?submitted=1',
      autoResponse: "Thanks for completing the operations audit! We'll review your submission and follow up soon with a personalized consultation. Want to dive deeper? Book a $750 Profit Leak Snapshot: https://trecoleman.com/profit-leak-snapshot.html",
      primary: emphasiseAudit
    };

    const playbookOffer = {
      title: 'Free 90-Day Playbook',
      subject: 'New Playbook Request (Exit Intent)',
      nextUrl: 'https://trecoleman.com/5_Phase_AI_Lead_System_FULL_Detailed_TreColeman.pdf',
      autoResponse: "Thanks for requesting the playbook! I'll be in touch soon.\n\nReady to identify your profit leaks? Book a $750 Profit Leak Snapshot: https://trecoleman.com/profit-leak-snapshot.html",
      primary: !emphasiseAudit
    };

    // Append only the selected offer based on the emphasised variant
    const selectedOffer = emphasiseAudit ? auditOffer : playbookOffer;
    offersContainer.appendChild(createOffer(selectedOffer));
    
// Append only the selected offer based on the emphasised variant

    
     
        const selectedOffer = emphasiseAudit ? auditOffer : playbookOffer;
        offersContainer.appendChild(createOffer(selectedOffer));

    // Build modal structure
    modal.appendChild(closeBtn);
    modal.appendChild(heading);
    modal.appendChild(social);
    modal.appendChild(offersContainer);
    // Add "No thanks" link
    const noThanks = document.createElement('a');
    noThanks.className = 'no-thanks';
    noThanks.textContent = 'No thanks, keep browsing';
    noThanks.addEventListener('click', function (e) {
      e.preventDefault();
      document.body.removeChild(overlay);
    });
    modal.appendChild(noThanks);

    // Append modal to overlay
    overlay.appendChild(modal);
    // Append overlay to body
    document.body.appendChild(overlay);
  }

  /**
   * Detect exit intent by listening for mouse movements toward the top of
   * the viewport. When triggered, remove the listener and show the pop‑up.
   */
  function handleMouseOut(event) {
    // If the mouse leaves to the top (y <= 0) and not to a descendant
    if (event.clientY <= 0 && !shown) {
      document.removeEventListener('mouseout', handleMouseOut);
      showExitPopup();
    }
  }

  // Attach listener after a slight delay so the page can load
  setTimeout(function () {
    document.addEventListener('mouseout', handleMouseOut);
  }, 1000);
})();
