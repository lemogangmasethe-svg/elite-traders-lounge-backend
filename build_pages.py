#!/usr/bin/env python3
"""Generates register-sitter.html, book.html, checkin.html, policies.html
using a shared header/footer so nav stays consistent with index.html."""
import pathlib

ROOT = pathlib.Path(__file__).parent

BRAND_SVG = '''<svg class="brand__mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <path d="M24 4 8 11v10c0 12 7 19 16 23 9-4 16-11 16-23V11L24 4Z" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>
        <path d="M24 15c-4.5 0-7 3-7 6.4 0 4.2 4.3 6.7 7 9.6 2.7-2.9 7-5.4 7-9.6 0-3.4-2.5-6.4-7-6.4Z" fill="currentColor"/>
      </svg>'''


def header(active=""):
    def cls(name):
        return ' class="is-active"' if name == active else ""
    return f'''<header class="header">
  <div class="container header__inner">
    <a href="./index.html" class="brand" aria-label="Elite Traders Lounge home">
      {BRAND_SVG}
      <span class="brand__name">
        <span>Elite Traders Lounge</span>
        <span>Babysitting Services</span>
      </span>
    </a>

    <nav class="nav" aria-label="Primary">
      <ul class="nav__links">
        <li><a href="./index.html#how-it-works">How it works</a></li>
        <li><a href="./guide.html"{cls('guide')}>Getting started guide</a></li>
        <li><a href="./index.html#trust">Trust &amp; safety</a></li>
        <li><a href="./index.html#pricing">Rates</a></li>
        <li><a href="./policies.html"{cls('policies')}>Policies</a></li>
        <li><a href="./terms.html"{cls('terms')}>Terms &amp; Conditions</a></li>
        <li><a href="./index.html#faq">FAQ</a></li>
        <li><a href="./index.html#contact">Contact</a></li>
      </ul>
    </nav>

    <div class="header__actions">
      <button class="theme-toggle" data-theme-toggle aria-label="Switch to dark mode">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
      <a href="./register-sitter.html" class="btn btn--secondary btn--sm">Become a sitter</a>
      <a href="./book.html" class="btn btn--primary btn--sm">Book a sitter</a>
      <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" data-menu-toggle>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      </button>
    </div>
  </div>
  <div class="container">
    <div class="mobile-menu" data-mobile-menu>
      <a href="./index.html#how-it-works">How it works</a>
      <a href="./guide.html">Getting started guide</a>
      <a href="./index.html#trust">Trust &amp; safety</a>
      <a href="./index.html#pricing">Rates</a>
      <a href="./policies.html">Policies</a>
      <a href="./terms.html">Terms &amp; Conditions</a>
      <a href="./index.html#faq">FAQ</a>
      <a href="./index.html#contact">Contact</a>
      <a href="./register-sitter.html">Become a sitter</a>
      <a href="./book.html">Book a sitter</a>
      <a href="./checkin.html">Confirm arrival / departure</a>
    </div>
  </div>
</header>'''


FOOTER = '''<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a href="./index.html" class="brand" aria-label="Elite Traders Lounge home">
          <svg class="brand__mark" viewBox="0 0 48 48" fill="none" aria-hidden="true" style="width:32px;height:32px;">
            <path d="M24 4 8 11v10c0 12 7 19 16 23 9-4 16-11 16-23V11L24 4Z" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/>
            <path d="M24 15c-4.5 0-7 3-7 6.4 0 4.2 4.3 6.7 7 9.6 2.7-2.9 7-5.4 7-9.6 0-3.4-2.5-6.4-7-6.4Z" fill="currentColor"/>
          </svg>
          <span class="brand__name"><span>Elite Traders Lounge</span></span>
        </a>
        <p>A verified booking platform connecting South African families with independent babysitters. Payments are processed and settled securely through Paystack Split Payments. Registration K2017318876.</p>
      </div>
      <div>
        <h4>Platform</h4>
        <ul>
          <li><a href="./index.html#how-it-works">How it works</a></li>
          <li><a href="./guide.html">Getting started guide</a></li>
          <li><a href="./index.html#pricing">Rate bands</a></li>
          <li><a href="./index.html#trust">Trust &amp; safety</a></li>
          <li><a href="./register-sitter.html">Become a sitter</a></li>
          <li><a href="./book.html">Book a sitter</a></li>
          <li><a href="./checkin.html">Confirm arrival / departure</a></li>
        </ul>
      </div>
      <div>
        <h4>Support</h4>
        <ul>
          <li><a href="./index.html#faq">FAQ</a></li>
          <li><a href="mailto:lemo.masethe@elitetraders.co.za">Email support</a></li>
          <li><a href="tel:+27814270419">Call support</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="./policies.html#minimum-wage">Minimum wage &amp; rate bands</a></li>
          <li><a href="./policies.html#refund-policy">Refund &amp; cancellation policy</a></li>
          <li><a href="./policies.html#popia">POPIA &amp; data protection</a></li>
          <li><a href="./terms.html">Terms &amp; Conditions</a></li>
          <li><a href="./policies.html">All policies</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 2026 Elite Traders Lounge (Pty) Ltd · Reg. K2017318876</span>
      <span>Kwa-Guqa, Mpumalanga, South Africa</span>
    </div>
  </div>
</footer>'''


def page(title, description, active, body, extra_js=None):
    js_files = [extra_js] if isinstance(extra_js, str) else (extra_js or [])
    extra = ''.join(f'\n<script src="./{f}" defer></script>' for f in js_files)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{description}" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://api.fontshare.com/v2/css?f[]=chillax@400,500,600,700&f[]=general-sans@400,500,600,700&display=swap" rel="stylesheet" />

<link rel="stylesheet" href="./base.css" />
<link rel="stylesheet" href="./style.css" />
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>

{header(active)}

<main id="main">
{body}
</main>

{FOOTER}

<script src="./app.js" defer></script>
<script src="./api.js" defer></script>{extra}
</body>
</html>
'''


GUIDE_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Getting started</span></div>
      <span class="eyebrow">Getting started</span>
      <h1>How to get started &mdash; a simple guide.</h1>
      <p>This page uses short, easy steps. Don't worry if you have never used an app like this before. Just follow the steps in order. If you get stuck, call or email us &mdash; our details are at the bottom of this page.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <span class="eyebrow">Step 1 &middot; for everyone</span>
      <h2 class="section-title">First, get your free Paystack account.</h2>
      <p class="section-lede">Paystack is the safe app that moves money between families and babysitters. Elite Traders Lounge never touches your money &mdash; Paystack does, so it is always safe. Everyone needs their own Paystack account before they can register.</p>

      <div class="guide-steps">
        <div class="guide-step">
          <span class="guide-step__num">1</span>
          <div class="guide-step__body">
            <h3>Open the Paystack sign-up page</h3>
            <p>Tap the button below. It opens in a new tab, so you won't lose this guide.</p>
            <a href="https://dashboard.paystack.com/#/signup" target="_blank" rel="noopener" class="btn btn--primary">Open Paystack sign-up</a>
          </div>
        </div>
        <div class="guide-step">
          <span class="guide-step__num">2</span>
          <div class="guide-step__body">
            <h3>Type in your details</h3>
            <ul>
              <li>Your full name</li>
              <li>Your email address (use one you check often)</li>
              <li>A password you will remember</li>
            </ul>
          </div>
        </div>
        <div class="guide-step">
          <span class="guide-step__num">3</span>
          <div class="guide-step__body">
            <h3>Check your email</h3>
            <p>Paystack sends you a message to confirm it is really you. Open that email and tap the confirm link inside it.</p>
          </div>
        </div>
        <div class="guide-step">
          <span class="guide-step__num">4</span>
          <div class="guide-step__body">
            <h3>Add your bank account</h3>
            <p>Inside Paystack, go to Settings and add your South African bank account. This is where your money will be paid to, or paid from.</p>
          </div>
        </div>
        <div class="guide-step">
          <span class="guide-step__num">5</span>
          <div class="guide-step__body">
            <h3>Copy your Paystack email</h3>
            <p>Write down or remember the email address you used for Paystack. You will type this same email into the Elite Traders Lounge form in Step 2.</p>
          </div>
        </div>
      </div>

      <div class="guide-audio">
        <p><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-3px;margin-right:6px;"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>Prefer to listen?</p>
        <audio controls preload="none" src="./guide-audio-paystack.mp3"></audio>
      </div>
    </div>
  </section>

  <section class="section-pad section-pad--tight" style="background: var(--color-surface-offset);">
    <div class="container container--narrow">
      <span class="eyebrow">Step 2 &middot; choose one</span>
      <h2 class="section-title">Now, tell us what you want to do.</h2>
      <p class="section-lede">Are you looking after children, or looking for a babysitter? Tap the one that is you.</p>

      <div class="tabs" role="tablist" aria-label="Choose your guide" style="margin-top: var(--space-8);">
        <button class="tab" role="tab" aria-selected="true" id="tab-family" aria-controls="panel-family" data-tab="family">I want to book a babysitter</button>
        <button class="tab" role="tab" aria-selected="false" id="tab-sitter" aria-controls="panel-sitter" data-tab="sitter">I want to become a babysitter</button>
      </div>

      <div id="panel-family" role="tabpanel" aria-labelledby="tab-family">
        <div class="guide-steps">
          <div class="guide-step">
            <span class="guide-step__num">1</span>
            <div class="guide-step__body">
              <h3>Open the booking form</h3>
              <p>Tap the button below to go to the family sign-up page.</p>
              <a href="./book.html" class="btn btn--primary">Open the booking form</a>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">2</span>
            <div class="guide-step__body">
              <h3>Fill in your details</h3>
              <ul>
                <li>Your full name, ID or passport number, and cellphone number</li>
                <li>Your home address &mdash; this is where the babysitter will come</li>
                <li>How many children you have, and their ages</li>
                <li>If you have pets, say what type</li>
              </ul>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">3</span>
            <div class="guide-step__body">
              <h3>Upload two documents</h3>
              <ul>
                <li>A copy of your ID or passport</li>
                <li>A proof of address (like a light bill) from the last 3 months</li>
              </ul>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">4</span>
            <div class="guide-step__body">
              <h3>Type in your Paystack email</h3>
              <p>Use the same email you used when you made your Paystack account in Step 1.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">5</span>
            <div class="guide-step__body">
              <h3>Choose your booking</h3>
              <p>Pick the date, time, and how many hours you need. You can also choose a babysitter you like, or let our team pick one for you.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">6</span>
            <div class="guide-step__body">
              <h3>Take a quick selfie</h3>
              <p>This is just to prove it is really you &mdash; it only takes a few seconds.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">7</span>
            <div class="guide-step__body">
              <h3>Pay the R99 fee</h3>
              <p>This fee checks your identity and keeps everyone safe. Tap the Paystack pay button on the form to pay it. You only pay this once a year.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">8</span>
            <div class="guide-step__body">
              <h3>Submit the form and wait</h3>
              <p>Our team checks your details, usually within a day or two. Once approved, your babysitter booking is confirmed.</p>
            </div>
          </div>
        </div>
        <div class="guide-audio">
          <p><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-3px;margin-right:6px;"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>Prefer to listen?</p>
          <audio controls preload="none" src="./guide-audio-family.mp3"></audio>
        </div>
      </div>

      <div id="panel-sitter" role="tabpanel" aria-labelledby="tab-sitter" hidden>
        <div class="guide-steps">
          <div class="guide-step">
            <span class="guide-step__num">1</span>
            <div class="guide-step__body">
              <h3>Open the babysitter sign-up form</h3>
              <p>Tap the button below to go to the babysitter sign-up page.</p>
              <a href="./register-sitter.html" class="btn btn--primary">Open the sign-up form</a>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">2</span>
            <div class="guide-step__body">
              <h3>Fill in your details</h3>
              <ul>
                <li>Your full name, ID or passport number, and cellphone number</li>
                <li>Your nationality and home address</li>
                <li>Your years of childcare experience and when you are available</li>
              </ul>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">3</span>
            <div class="guide-step__body">
              <h3>Upload your documents</h3>
              <p>You will need clear photos or scans of:</p>
              <ul>
                <li>Your ID or passport</li>
                <li>Proof of address (like a light bill) from the last 3 months</li>
                <li>An AFIS check or police clearance certificate</li>
                <li>A Child Protection Register (Part B) clearance letter</li>
                <li>If you are not a South African citizen: a police clearance from your home country too</li>
              </ul>
              <p>Don't have these documents yet? The form tells you exactly how and where to apply for each one.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">4</span>
            <div class="guide-step__body">
              <h3>Add a reference</h3>
              <p>Give the name and contact details of someone who knows your childcare experience. They will be contacted to confirm.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">5</span>
            <div class="guide-step__body">
              <h3>Type in your Paystack email</h3>
              <p>Use the same email you used when you made your Paystack account in Step 1. This is where your pay will be sent.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">6</span>
            <div class="guide-step__body">
              <h3>Take a selfie and a short video</h3>
              <p>This proves you are a real person, not a photo. It only takes a few seconds and is never recorded.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">7</span>
            <div class="guide-step__body">
              <h3>Pay the R99 fee</h3>
              <p>This fee checks your identity and documents. Tap the Paystack pay button on the form to pay it. You pay this once a year, when you renew your documents.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">8</span>
            <div class="guide-step__body">
              <h3>Submit and wait for approval</h3>
              <p>Our team checks your documents, usually within a few days. Once approved, families can find and book you.</p>
            </div>
          </div>
          <div class="guide-step">
            <span class="guide-step__num">9</span>
            <div class="guide-step__body">
              <h3>Renew every year</h3>
              <p>Once a year, you will need to upload fresh copies of your police clearance and Child Protection Register letter, and pay the R99 fee again. You do this from your own babysitter dashboard &mdash; we will remind you when it is due.</p>
            </div>
          </div>
        </div>
        <div class="guide-audio">
          <p><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-3px;margin-right:6px;"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>Prefer to listen?</p>
          <audio controls preload="none" src="./guide-audio-sitter.mp3"></audio>
        </div>
      </div>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <span class="eyebrow">Words explained simply</span>
      <h2 class="section-title">Not sure what a word means?</h2>
      <dl class="guide-glossary">
        <div>
          <dt>Paystack</dt>
          <dd>The safe app that sends and receives money for bookings. It is not made by Elite Traders Lounge &mdash; it is a trusted, separate payment company used all over Africa.</dd>
        </div>
        <div>
          <dt>Verification</dt>
          <dd>Checking that you are really you, and that your documents are real and up to date.</dd>
        </div>
        <div>
          <dt>Commission</dt>
          <dd>A small part of the booking fee (10&ndash;15%) that Elite Traders Lounge keeps for running the platform. The rest goes to the babysitter.</dd>
        </div>
        <div>
          <dt>R99 fee</dt>
          <dd>A yearly fee, paid by both families and babysitters, that covers the cost of checking documents and identity.</dd>
        </div>
        <div>
          <dt>Police clearance</dt>
          <dd>An official letter from the police (or AFIS) that shows a person does not have a serious criminal record.</dd>
        </div>
        <div>
          <dt>Booking reference</dt>
          <dd>A short code given to every booking, used to confirm arrival and departure.</dd>
        </div>
      </dl>

      <div class="alert alert--info">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <span>Still stuck? Email <a href="mailto:lemo.masethe@elitetraders.co.za">lemo.masethe@elitetraders.co.za</a> or call <a href="tel:+27814270419">081 427 0419</a> and we will help you step by step.</span>
      </div>
    </div>
  </section>
'''


REGISTER_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Register as a babysitter</span></div>
      <span class="eyebrow">Babysitter sign-up</span>
      <h1>Join Elite Traders Lounge as a verified babysitter.</h1>
      <p>Tell us about your experience so we can place you in the right rate band. Every applicant completes Smile ID identity verification before receiving bookings, and every booking pays at or above the National Minimum Wage (R30.23/hour, effective 1 March 2026) &mdash; never negotiated down.</p>
      <div class="alert alert--info">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <span>New to this? Read our <a href="./guide.html">simple, step-by-step getting started guide</a> first &mdash; it walks you through everything, including creating your Paystack account.</span>
      </div>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <div class="form-shell">
        <form id="sitter-form" novalidate>

          <div class="form-section">
            <div class="form-section__title">Your details</div>
            <div class="form-section__hint">This information is used for Smile ID identity verification and to contact you about bookings.</div>
            <div class="field">
              <label for="full_name">Full name</label>
              <input type="text" id="full_name" name="full_name" autocomplete="name" required minlength="2" maxlength="120" />
            </div>

            <div class="field">
              <label>Identity document</label>
              <div class="radio-cards" data-id-type-group>
                <label class="radio-card">
                  <input type="radio" name="id_type" value="sa_id" checked data-id-type-toggle />
                  <strong>South African ID</strong>
                  <span>SA citizens &amp; permanent residents</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="id_type" value="passport" data-id-type-toggle />
                  <strong>Passport + work permit</strong>
                  <span>Foreign nationals registering as freelancers</span>
                </label>
              </div>
            </div>

            <div class="field-grid" data-id-fields="sa_id">
              <div class="field">
                <label for="id_number">South African ID number</label>
                <input type="text" id="id_number" name="id_number" inputmode="numeric" minlength="5" maxlength="20" />
              </div>
            </div>

            <div class="field-grid" data-id-fields="passport" hidden>
              <div class="field">
                <label for="passport_number">Passport number</label>
                <input type="text" id="passport_number" name="passport_number" maxlength="20" />
              </div>
              <div class="field">
                <label for="work_permit_number">Work permit number</label>
                <input type="text" id="work_permit_number" name="work_permit_number" maxlength="40" />
                <span class="field__hint">Required by South African immigration law &mdash; freelance babysitters who are not SA citizens or permanent residents must hold a valid work permit.</span>
              </div>
              <div class="field">
                <label for="work_permit_expiry">Work permit expiry date</label>
                <input type="date" id="work_permit_expiry" name="work_permit_expiry" />
              </div>
            </div>

            <div class="field">
              <label for="nationality">Nationality</label>
              <input type="text" id="nationality" name="nationality" required maxlength="60" placeholder="e.g. South African" />
            </div>

            <div class="field-grid">
              <div class="field">
                <label for="phone">Cellphone number</label>
                <input type="tel" id="phone" name="phone" autocomplete="tel" required minlength="7" maxlength="20" placeholder="e.g. 081 234 5678" />
              </div>
              <div class="field">
                <label for="email">Email address</label>
                <input type="email" id="email" name="email" autocomplete="email" required />
              </div>
            </div>
            <div class="field">
              <label for="address">Home address</label>
              <input type="text" id="address" name="address" autocomplete="street-address" required minlength="5" maxlength="300" />
            </div>
            <div class="field-grid">
              <div class="field">
                <label for="town">Town / suburb</label>
                <input type="text" id="town" name="town" autocomplete="address-level2" required minlength="2" maxlength="80" placeholder="e.g. Modelpark" />
              </div>
              <div class="field">
                <label for="province">Province</label>
                <select id="province" name="province" required>
                  <option value="">Select province</option>
                  <option>Gauteng</option>
                  <option>Mpumalanga</option>
                  <option>Western Cape</option>
                  <option>Eastern Cape</option>
                  <option>KwaZulu-Natal</option>
                  <option>Free State</option>
                  <option>Limpopo</option>
                  <option>North West</option>
                  <option>Northern Cape</option>
                </select>
              </div>
            </div>
            <div class="form-section__hint">This tells families roughly where you're based so we can match you with bookings within a practical, local travel distance (our 40km service-area policy) &mdash; we never show your exact street address to families.</div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Public profile (shown to families)</div>
            <div class="form-section__hint">Once you're verified, families browsing babysitters on our website see this information alongside your photo, so they can choose who best fits their household. Your profile photo is simply the selfie you capture below for identity verification &mdash; no separate upload needed.</div>
            <div class="field-grid">
              <div class="field">
                <label for="profile_gender">Gender</label>
                <select id="profile_gender" name="profile_gender" required>
                  <option value="" disabled selected>Select</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              <div class="field">
                <label for="profile_race">Race / ethnicity</label>
                <select id="profile_race" name="profile_race" required>
                  <option value="" disabled selected>Select</option>
                  <option value="black_african">Black African</option>
                  <option value="coloured">Coloured</option>
                  <option value="indian_asian">Indian / Asian</option>
                  <option value="white">White</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              <div class="field">
                <label for="profile_age">Age</label>
                <input type="number" id="profile_age" name="profile_age" min="18" max="80" required placeholder="e.g. 28" />
              </div>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Upload your documents</div>
            <div class="form-section__hint">Upload clear photos or scans (JPG, PNG, or PDF, max 6MB each) right here &mdash; our verification team reviews them directly with your application. No need to email or WhatsApp them separately.</div>
            <div class="field">
              <label for="id_document">Copy of your ID / passport</label>
              <input type="file" id="id_document" name="id_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">JPG, PNG, or PDF &middot; max 6MB</span>
              <span class="file-status" id="id_document-status"></span>
            </div>
            <div class="field">
              <label for="proof_of_address_type">Proof of address document type</label>
              <select id="proof_of_address_type" name="proof_of_address_type" required>
                <option value="" disabled selected>Select a document type</option>
                <option value="utility_bill">Utility bill (municipal / electricity / water)</option>
                <option value="bank_statement">Bank statement</option>
                <option value="lease_agreement">Lease agreement</option>
                <option value="affidavit">Affidavit confirming residential address</option>
              </select>
            </div>
            <div class="field">
              <label for="proof_of_address_document">Upload proof of address</label>
              <input type="file" id="proof_of_address_document" name="proof_of_address_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">A utility bill, bank statement, lease agreement, or affidavit dated within the last 3 months, matching the home address above &middot; JPG, PNG, or PDF, max 6MB</span>
              <span class="file-status" id="proof_of_address_document-status"></span>
            </div>
            <div class="checkbox-field">
              <input type="checkbox" id="proof_of_address_confirmed" name="proof_of_address_confirmed" required />
              <label for="proof_of_address_confirmed">I confirm this document is dated within the last 3 months and matches the home address above.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Experience &amp; rate band</div>
            <div class="form-section__hint">Choose the level that matches your experience &mdash; this determines your Appendix C rate band. Our team confirms your final level during verification.</div>
            <div class="field">
              <label>Experience level</label>
              <div class="radio-cards">
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="1" required />
                  <strong>Level 1 &mdash; Entry</strong>
                  <span>0&ndash;1 year &middot; R45/hr day (5hr min) or R315/day flat</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="2" />
                  <strong>Level 2 &mdash; Standard</strong>
                  <span>1&ndash;3 years, references &middot; R55/hr day (5hr min) or R385/day flat</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="3" />
                  <strong>Level 3 &mdash; Advanced</strong>
                  <span>3+ yrs, First Aid/CPR &middot; R65/hr day (4hr min) or R450/day flat, R700/night overnight</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="4" />
                  <strong>Level 4 &mdash; Specialist</strong>
                  <span>Overnight / special needs &middot; R850/night (10hr)</span>
                </label>
              </div>
            </div>
            <div class="field-grid">
              <div class="field">
                <label for="years_experience">Years of babysitting / childcare experience</label>
                <input type="text" id="years_experience" name="years_experience" required placeholder="e.g. 2 years" />
              </div>
              <div class="field">
                <label for="certifications">Certifications <span class="field__hint">(optional)</span></label>
                <input type="text" id="certifications" name="certifications" placeholder="e.g. First Aid, CPR, ECD qualification" />
              </div>
            </div>
            <div class="field">
              <label for="availability">Availability</label>
              <input type="text" id="availability" name="availability" required minlength="2" maxlength="300" placeholder="e.g. Weekday evenings, weekends, overnight from Fridays" />
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Reference &amp; affidavit</div>
            <div class="form-section__hint">Provide one contactable reference. This person will be asked to complete and sign the standard Reference Affidavit (Appendix A of your contract) before a Commissioner of Oaths, confirming your character and childcare experience.</div>
            <div class="field-grid">
              <div class="field">
                <label for="reference_name">Reference full name</label>
                <input type="text" id="reference_name" name="reference_name" required minlength="2" maxlength="120" />
              </div>
              <div class="field">
                <label for="reference_relationship">Relationship to you</label>
                <input type="text" id="reference_relationship" name="reference_relationship" required minlength="2" maxlength="80" placeholder="e.g. Former employer, family friend" />
              </div>
              <div class="field">
                <label for="reference_phone">Reference cellphone number</label>
                <input type="tel" id="reference_phone" name="reference_phone" required minlength="7" maxlength="20" />
              </div>
              <div class="field">
                <label for="reference_email">Reference email address</label>
                <input type="email" id="reference_email" name="reference_email" required />
              </div>
            </div>
            <div class="checkbox-field">
              <input type="checkbox" id="reference_affidavit_consent" name="reference_affidavit_consent" required />
              <label for="reference_affidavit_consent">I confirm this reference has agreed to be contacted by Elite Traders Lounge and to complete the Reference Affidavit template in Appendix A of the Babysitter Contract.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Paystack payout account</div>
            <div class="form-section__hint">Elite Traders Lounge uses Paystack Split Payment: every booking pays into Paystack once, and Paystack pays your net share directly to your own Paystack account &mdash; Elite Traders Lounge never holds or is responsible for your funds. Enter the email address linked to your Paystack account; if you don't have one yet, create a free account at <a href="https://paystack.com" target="_blank" rel="noopener">paystack.com</a> before submitting.</div>
            <div class="field">
              <label for="paystack_email">Paystack account email</label>
              <input type="email" id="paystack_email" name="paystack_email" required />
            </div>
          </div>

          <div class="form-section form-section--final">
            <div class="form-section__title">Selfie &amp; liveness check &middot; Verify your identity with Smile ID</div>
            <div class="form-section__hint">Elite Traders Lounge partners with Smile ID to confirm your identity against your ID/passport and run a facial-liveness check automatically when you submit this form. Once verified, your profile displays a &ldquo;Verified identity&rdquo; badge that families can see.</div>
            <div class="selfie-capture" id="selfie-capture">
              <div class="selfie-capture__frame">
                <div class="selfie-capture__placeholder" id="selfie-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="3"/><path d="M6.5 18.5c1.2-2.3 3.2-3.5 5.5-3.5s4.3 1.2 5.5 3.5"/></svg>
                </div>
                <video id="selfie-video" autoplay playsinline muted hidden></video>
                <img id="selfie-preview" hidden alt="Captured selfie preview" />
                <canvas id="selfie-canvas" hidden></canvas>
              </div>
              <div class="selfie-capture__actions">
                <button type="button" class="btn btn--secondary" id="selfie-start-btn">Turn on camera</button>
                <button type="button" class="btn btn--primary" id="selfie-capture-btn" hidden>Capture selfie</button>
                <button type="button" class="btn btn--ghost" id="selfie-retake-btn" hidden>Retake</button>
              </div>
              <span class="field__hint">We take one clear photo of your face, then a quick photo burst while you slowly turn your head &mdash; this proves a real person is registering, not a photo of a photo. Your camera feed is never recorded, only these still frames are sent to Smile ID.</span>
              <span class="file-status" id="selfie-status"></span>
            </div>
            <div class="field">
              <label for="police_clearance_document">AFIS check or police clearance certificate <span class="field__hint">(required)</span></label>
              <input type="file" id="police_clearance_document" name="police_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">A valid SAPS Police Clearance Certificate &middot; JPG, PNG, or PDF, max 6MB. Don't have one yet? You can apply at any police station for a once-off fee of R190 &mdash; take your ID/passport, get SAPS 91(a) fingerprints taken, and pay at the station or by EFT; see the <a href="https://www.saps.gov.za/services/applying_clearence_certificate.php" target="_blank" rel="noopener">official SAPS guidance</a>. It typically takes a few weeks to be issued, so we recommend applying early. This is not a once-off check &mdash; to remain verified, you'll need to submit a fresh clearance certificate every 12 months.</span>
              <span class="file-status" id="police_clearance_document-status"></span>
            </div>
            <div class="field">
              <label for="child_protection_clearance_document">Child Protection Register (Part B) clearance letter <span class="field__hint">(required)</span></label>
              <input type="file" id="child_protection_clearance_document" name="child_protection_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">Proof you are not listed on Part B of South Africa's National Child Protection Register, which bars unsuitable people from working with children &middot; JPG, PNG, or PDF, max 6MB. Apply for a free Form 30 individual enquiry by emailing your ID copy to <a href="mailto:CPRenquiries@dsd.gov.za">CPRenquiries@dsd.gov.za</a> (Department of Social Development) &mdash; it typically takes a few weeks, so apply early. Like the police clearance above, this must be renewed every 12 months to keep your verified status.</span>
              <span class="file-status" id="child_protection_clearance_document-status"></span>
            </div>
            <div class="field-grid" data-id-fields="passport" hidden>
              <div class="field">
                <label for="foreign_police_clearance_document">Foreign police clearance certificate <span class="field__hint">(required for non-SA sitters)</span></label>
                <input type="file" id="foreign_police_clearance_document" name="foreign_police_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" />
                <span class="field__hint">South African immigration law requires foreign nationals to also provide a police clearance certificate from any country they lived in for 12+ months as an adult during the last 5 years, issued within the last 6 months &middot; JPG, PNG, or PDF, max 6MB. Contact that country's police or diplomatic mission for the correct process. This also needs renewing every 12 months.</span>
                <span class="file-status" id="foreign_police_clearance_document-status"></span>
              </div>
            </div>
            <div class="checkbox-field">
              <input type="checkbox" id="smile_id_consent" name="smile_id_consent" required />
              <label for="smile_id_consent">I consent to Smile ID verifying my identity (document check + facial liveness) and to Elite Traders Lounge reviewing my police clearance certificate, Child Protection Register clearance, and (if applicable) foreign police clearance as part of registration and each annual renewal.</label>
            </div>
          </div>

          <div class="form-section form-section--final">
            <div class="form-section__title">Annual registration &amp; verification fee &middot; R99</div>
            <div class="form-section__hint">An R99 fee covers your identity and document verification. It is completely separate from the 10&ndash;15% booking commission described above, and is the same R99 fee families pay. Because your police clearance and Child Protection Register checks must be renewed every 12 months to keep your safety verification current, this fee is charged annually rather than once &mdash; you'll pay it again each year alongside your renewal documents, from your sitter dashboard.</div>
            <a href="https://paystack.shop/pay/-c63v2905q" target="_blank" rel="noopener" class="btn btn--primary">Pay R99 registration fee via Paystack</a>
            <span class="field__hint" style="display:block;margin-top:var(--space-3);">Use the same email address you entered above as your payment reference so our team can match your payment. Our team confirms receipt on the Paystack account and marks your registration fee as paid &mdash; you don't need to upload proof.</span>
          </div>

          <div class="form-section">
            <div class="checkbox-field">
              <input type="checkbox" id="agreed_terms" name="agreed_terms" required />
              <label for="agreed_terms">I confirm the details above are accurate and I agree to the Elite Traders Lounge Babysitter Contract (emailed to me on submission), the <a href="./terms.html">Terms &amp; Conditions</a>, the <a href="./policies.html#refund-policy">Refund &amp; Cancellation Policy</a>, and the <a href="./policies.html#popia">POPIA data protection terms</a>. I understand Elite Traders Lounge reserves the right to refuse or cancel service to any user who provides false information or breaches its rules.</label>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn--primary" id="sitter-submit">Submit application</button>
              <span class="form-section__hint" style="margin:0;">Already applied? <a href="mailto:lemo.masethe@elitetraders.co.za">Email support</a> for a status update.</span>
            </div>
            <div class="alert alert--success" id="sitter-success" hidden>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4M12 3l7 3v6c0 5-3 8.5-7 9-4-.5-7-4-7-9V6l7-3Z"/></svg>
              <span id="sitter-success-text">Application received. Our team will contact you to complete Smile ID verification before you can accept bookings.</span>
              <span class="badge-verified badge-verified--pending" style="margin-left: var(--space-3);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>Verification pending</span>
              <a href="#" id="sitter-contract-link" style="margin-left: var(--space-3); white-space: nowrap;" target="_blank" rel="noopener" hidden>Download contract</a>
            </div>
            <div class="booking-ref-box" id="sitter-access-box" hidden>
              <div class="booking-ref-box__item"><span>Your dashboard access code</span><strong id="sitter-access-code">&ndash;</strong></div>
            </div>
            <p class="form-section__hint" id="sitter-access-hint" hidden style="margin-top: var(--space-3);">Save this code &mdash; with your email, it logs you into your <a href="./sitter-dashboard.html">babysitter dashboard</a> to accept or decline bookings and set your availability. It's also included in your emailed contract.</p>
            <div class="alert alert--error" id="sitter-error" hidden>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
              <span id="sitter-error-text">Something went wrong.</span>
            </div>
          </div>
        </form>
      </div>
    </div>
  </section>
'''


BOOK_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Book a sitter</span></div>
      <span class="eyebrow">Parent / guardian &middot; book a sitter</span>
      <h1>Register as a parent or guardian and book a sitter.</h1>
      <p>Choose the level and booking type &mdash; the rate is fixed per Appendix C (no negotiation needed) and checked against the National Minimum Wage (R30.23/hour, effective 1 March 2026). Level 1 &amp; 2 day bookings need a minimum of 5 hours; Level 3 day bookings need a minimum of 4 hours; overnight bookings need a minimum of 10 hours.</p>
      <div class="alert alert--info">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <span>New to this? Read our <a href="./guide.html">simple, step-by-step getting started guide</a> first &mdash; it walks you through everything, including creating your Paystack account.</span>
      </div>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <div class="form-shell">
        <form id="booking-form" novalidate>

          <div class="form-section">
            <div class="form-section__title">Parent / guardian details</div>
            <div class="form-section__hint">This information is used for Smile ID identity verification and to contact you about your booking.</div>
            <div class="field">
              <label for="parent_name">Full name</label>
              <input type="text" id="parent_name" name="parent_name" autocomplete="name" required minlength="2" maxlength="120" />
            </div>

            <div class="field">
              <label>Identity document</label>
              <div class="radio-cards" data-id-type-group>
                <label class="radio-card">
                  <input type="radio" name="id_type" value="sa_id" checked data-id-type-toggle />
                  <strong>South African ID</strong>
                  <span>SA citizens &amp; permanent residents</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="id_type" value="passport" data-id-type-toggle />
                  <strong>Passport</strong>
                  <span>Foreign nationals resident in South Africa</span>
                </label>
              </div>
            </div>

            <div class="field-grid" data-id-fields="sa_id">
              <div class="field">
                <label for="id_number">South African ID number</label>
                <input type="text" id="id_number" name="id_number" inputmode="numeric" minlength="5" maxlength="20" />
              </div>
            </div>

            <div class="field-grid" data-id-fields="passport" hidden>
              <div class="field">
                <label for="passport_number">Passport number</label>
                <input type="text" id="passport_number" name="passport_number" maxlength="20" />
              </div>
              <div class="field">
                <label for="nationality">Nationality</label>
                <input type="text" id="nationality" name="nationality" maxlength="60" />
              </div>
            </div>

            <div class="field-grid">
              <div class="field">
                <label for="phone">Cellphone number</label>
                <input type="tel" id="phone" name="phone" autocomplete="tel" required minlength="7" maxlength="20" placeholder="e.g. 081 234 5678" />
              </div>
              <div class="field">
                <label for="email">Email address</label>
                <input type="email" id="email" name="email" autocomplete="email" required />
              </div>
            </div>
            <div class="field-grid">
              <div class="field">
                <label for="address">Home address where care will take place</label>
                <input type="text" id="address" name="address" autocomplete="street-address" required minlength="5" maxlength="300" />
              </div>
              <div class="field">
                <label for="children_count">Number and ages of children</label>
                <input type="text" id="children_count" name="children_count" required minlength="1" maxlength="20" placeholder="e.g. 2 children, ages 3 and 6" />
              </div>
            </div>

            <div class="field-grid">
              <div class="field">
                <label for="town">Town / suburb</label>
                <input type="text" id="town" name="town" autocomplete="address-level2" required minlength="2" maxlength="80" placeholder="e.g. Sandton" />
              </div>
              <div class="field">
                <label for="province">Province</label>
                <select id="province" name="province" required>
                  <option value="">Select province</option>
                  <option>Gauteng</option>
                  <option>Mpumalanga</option>
                  <option>Western Cape</option>
                  <option>Eastern Cape</option>
                  <option>KwaZulu-Natal</option>
                  <option>Free State</option>
                  <option>Limpopo</option>
                  <option>North West</option>
                  <option>Northern Cape</option>
                </select>
              </div>
            </div>
            <div id="coverage-result" class="alert" hidden></div>
            <div class="form-section__hint">We can only confirm bookings where a verified babysitter can reach you within our 40km local service area &mdash; see our <a href="./terms.html">terms</a>. We'll check this automatically once you enter your town above.</div>

            <div class="field">
              <label>Do you have any pets at home?</label>
              <div class="action-toggle">
                <label><input type="radio" name="has_pets" value="no" checked data-has-pets-toggle /> No pets</label>
                <label><input type="radio" name="has_pets" value="yes" data-has-pets-toggle /> Yes, we have pets</label>
              </div>
              <span class="field__hint">This helps us find the best-fit babysitter for your household and keeps your children and pets safe together.</span>
            </div>
            <div class="field" data-pet-type-field hidden>
              <label for="pet_type">What type of pet(s) do you have?</label>
              <input type="text" id="pet_type" name="pet_type" maxlength="120" placeholder="e.g. 1 medium dog, 2 cats" />
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Upload your documents</div>
            <div class="form-section__hint">Upload clear photos or scans (JPG, PNG, or PDF, max 6MB each) right here &mdash; our verification team reviews them directly with your booking. No need to email or WhatsApp them separately.</div>
            <div class="field">
              <label for="id_document">Copy of your ID / passport</label>
              <input type="file" id="id_document" name="id_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">JPG, PNG, or PDF &middot; max 6MB</span>
              <span class="file-status" id="id_document-status"></span>
            </div>
            <div class="field">
              <label for="proof_of_address_type">Proof of address document type</label>
              <select id="proof_of_address_type" name="proof_of_address_type" required>
                <option value="" disabled selected>Select a document type</option>
                <option value="utility_bill">Utility bill (municipal / electricity / water)</option>
                <option value="bank_statement">Bank statement</option>
                <option value="lease_agreement">Lease agreement</option>
                <option value="affidavit">Affidavit confirming residential address</option>
              </select>
            </div>
            <div class="field">
              <label for="proof_of_address_document">Upload proof of address</label>
              <input type="file" id="proof_of_address_document" name="proof_of_address_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
              <span class="field__hint">A utility bill, bank statement, lease agreement, or affidavit dated within the last 3 months, matching the home address above &middot; JPG, PNG, or PDF, max 6MB</span>
              <span class="file-status" id="proof_of_address_document-status"></span>
            </div>
            <div class="checkbox-field">
              <input type="checkbox" id="proof_of_address_confirmed" name="proof_of_address_confirmed" required />
              <label for="proof_of_address_confirmed">I confirm this document is dated within the last 3 months and matches the home address above.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Paystack account</div>
            <div class="form-section__hint">Payments run on Paystack Split Payment &mdash; Elite Traders Lounge never holds your funds in a wallet; Paystack pays the babysitter's share and Elite Traders Lounge's commission share directly, on the same transaction.</div>
            <div class="field">
              <label for="paystack_email">Paystack account email</label>
              <input type="email" id="paystack_email" name="paystack_email" required />
              <span class="field__hint">Don't have one yet? Create a free account at <a href="https://paystack.com" target="_blank" rel="noopener">paystack.com</a> before submitting.</span>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Booking details</div>
            <div class="form-section__hint">Select day or overnight, then the babysitter's level, and confirm the hourly rate you've agreed.</div>

            <div class="field">
              <label>Booking type</label>
              <div class="action-toggle">
                <label><input type="radio" name="rate_type" value="day" checked /> Day booking <span class="field__hint">(hourly, fixed rate by level)</span></label>
                <label><input type="radio" name="rate_type" value="full_day" /> Full-day flat rate <span class="field__hint">(7 hours, fixed rate by level)</span></label>
                <label><input type="radio" name="rate_type" value="overnight" /> Overnight <span class="field__hint">(min. 10 hours, fixed rate by level)</span></label>
              </div>
            </div>

            <div class="field-grid field-grid--3">
              <div class="field">
                <label for="level">Babysitter level</label>
                <select id="level" name="level" required>
                  <option value="1">Level 1 &mdash; Entry</option>
                  <option value="2">Level 2 &mdash; Standard</option>
                  <option value="3">Level 3 &mdash; Advanced</option>
                  <option value="4">Level 4 &mdash; Specialist (overnight only)</option>
                </select>
              </div>
              <div class="field" id="day-rate-field" hidden>
                <label>Flat day rate</label>
                <p class="field__static" id="day-rate-display">Level 1 flat day rate: R315/day (7 hours)</p>
              </div>
              <div class="field" id="day-count-field" hidden>
                <label for="day_count">Number of days</label>
                <input type="number" id="day_count" min="1" step="1" value="1" />
              </div>
              <div class="field">
                <label for="hourly_rate">Rate for this level (R)</label>
                <input type="number" id="hourly_rate" name="hourly_rate" required min="1" step="0.01" readonly />
                <span class="field__hint" id="band-hint">Level 1 day rate: R45/hour (fixed, minimum 5 hours)</span>
              </div>
              <div class="field">
                <label for="duration_hours">Duration (hours)</label>
                <input type="number" id="duration_hours" name="duration_hours" required min="1" step="0.5" placeholder="e.g. 4" />
              </div>
            </div>

            <div class="field-grid">
              <div class="field">
                <label for="booking_date">Booking date</label>
                <input type="date" id="booking_date" name="booking_date" required />
              </div>
              <div class="field">
                <label for="start_time">Start time</label>
                <input type="time" id="start_time" name="start_time" required />
              </div>
            </div>

            <div class="field">
              <label for="special_instructions">Care instructions <span class="field__hint">(optional)</span></label>
              <textarea id="special_instructions" name="special_instructions" maxlength="1000" placeholder="Feeding, naps, emergency contacts, house rules..."></textarea>
            </div>

            <div class="quote-box" id="quote-box" hidden>
              <div class="quote-box__row"><span>Rate for this level</span><strong id="q-rate">&ndash;</strong></div>
              <div class="quote-box__row"><span>Duration</span><strong id="q-duration">&ndash;</strong></div>
              <div class="quote-box__row"><span>Babysitter's booking fee</span><strong id="q-fee">&ndash;</strong></div>
              <div class="quote-box__row"><span>+ Elite Traders Lounge commission (<span id="q-family-comm-pct">&ndash;</span>, added to your bill)</span><strong id="q-family-comm">&ndash;</strong></div>
              <div class="quote-box__row total"><span>Total you pay as the Family</span><strong id="q-family-total">&ndash;</strong></div>
              <div class="quote-box__row"><span>&ndash; Elite Traders Lounge commission (<span id="q-sitter-comm-pct">&ndash;</span>, deducted from babysitter)</span><strong id="q-comm">&ndash;</strong></div>
              <div class="quote-box__row total"><span>Net the babysitter receives</span><strong id="q-net">&ndash;</strong></div>
              <div class="quote-box__row"><span>Total Elite Traders Lounge commission on this booking</span><strong id="q-total-comm-pct">&ndash;</strong></div>
              <p class="quote-box__note" id="q-note" hidden></p>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Special requests &amp; important rules</div>
            <div class="form-section__hint">Tell us if you need extra help with your child's routine, and please read the rules below carefully &mdash; they protect your child and your babysitter.</div>
            <div class="field-grid">
              <div class="checkbox-field">
                <input type="checkbox" id="special_bath_baby" name="special_bath_baby" />
                <label for="special_bath_baby">Babysitter will be required to bath the baby / child</label>
              </div>
              <div class="checkbox-field">
                <input type="checkbox" id="special_feed_baby" name="special_feed_baby" />
                <label for="special_feed_baby">Babysitter will be required to feed the baby / child</label>
              </div>
            </div>
            <div class="field">
              <label for="special_precautions">Special precautions the babysitter must follow <span class="field__hint">(optional)</span></label>
              <textarea id="special_precautions" name="special_precautions" maxlength="1000" placeholder="Allergies, safe-sleep routine, feeding schedule, any other precautions..."></textarea>
            </div>
            <div class="alert alert--error" style="align-items:flex-start;">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
              <span>Babysitters are <strong>not permitted to administer any medicine</strong> to a child under any circumstances, and may only perform duties directly related to caring for the child (feeding, bathing, comforting, play, and supervision as requested above) &mdash; <strong>never general household cleaning or chores</strong>. If a family or babysitter breaks either rule, Elite Traders Lounge is not held liable for the consequences.</span>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Choose a babysitter <span class="field__hint">(optional)</span></div>
            <div class="form-section__hint">Browse verified babysitters and tell us who you'd prefer &mdash; our admin team makes the final assignment based on real availability and the best fit for your family, but your preference helps guide that decision. Fill in the booking date, start time, and duration above first to see who's available.</div>
            <div class="sitter-browse" id="sitter-browse">
              <label class="sitter-card sitter-card--none">
                <input type="radio" name="preferred_sitter_id" value="" checked />
                <div class="sitter-card__body">
                  <strong>No preference</strong>
                  <span>Let Elite Traders Lounge assign the best-suited available babysitter.</span>
                </div>
              </label>
              <div id="sitter-browse-list" class="sitter-browse__list">
                <p class="sitter-browse__empty" id="sitter-browse-empty">Loading verified babysitters&hellip;</p>
              </div>
            </div>
          </div>

          <div class="form-section form-section--final">
            <div class="form-section__title">Selfie &amp; liveness check &middot; Verify your identity with Smile ID</div>
            <div class="form-section__hint">Elite Traders Lounge partners with Smile ID to confirm your identity automatically when you submit this form, before a babysitter is placed in your home.</div>
            <div class="selfie-capture" id="selfie-capture">
              <div class="selfie-capture__frame">
                <div class="selfie-capture__placeholder" id="selfie-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="3"/><path d="M6.5 18.5c1.2-2.3 3.2-3.5 5.5-3.5s4.3 1.2 5.5 3.5"/></svg>
                </div>
                <video id="selfie-video" autoplay playsinline muted hidden></video>
                <img id="selfie-preview" hidden alt="Captured selfie preview" />
                <canvas id="selfie-canvas" hidden></canvas>
              </div>
              <div class="selfie-capture__actions">
                <button type="button" class="btn btn--secondary" id="selfie-start-btn">Turn on camera</button>
                <button type="button" class="btn btn--primary" id="selfie-capture-btn" hidden>Capture selfie</button>
                <button type="button" class="btn btn--ghost" id="selfie-retake-btn" hidden>Retake</button>
              </div>
              <span class="field__hint">We take one clear photo of your face, then a quick photo burst while you slowly turn your head &mdash; this proves a real person is registering, not a photo of a photo. Your camera feed is never recorded, only these still frames are sent to Smile ID.</span>
              <span class="file-status" id="selfie-status"></span>
            </div>
            <div class="form-section__hint" style="margin-top: var(--space-2);">Elite Traders Lounge reserves the right to conduct criminal background checks on any Family or Babysitter registered on the platform.</div>
            <div class="checkbox-field">
              <input type="checkbox" id="smile_id_consent" name="smile_id_consent" required />
              <label for="smile_id_consent">I consent to Smile ID verifying my identity (document check + facial liveness) as part of this booking.</label>
            </div>
          </div>

          <div class="form-section form-section--final">
            <div class="form-section__title">Annual registration &amp; verification fee &middot; R99</div>
            <div class="form-section__hint">An R99 fee covers your identity and document verification. It is completely separate from the booking commission shown in your quote above, and is the same R99 fee babysitters pay. This fee is charged annually, once every 12 months, to keep your identity details current — if you've paid within the last year, our team will confirm this and you won't be asked to pay again until it's due.</div>
            <a href="https://paystack.shop/pay/-c63v2905q" target="_blank" rel="noopener" class="btn btn--primary">Pay R99 registration fee via Paystack</a>
            <span class="field__hint" style="display:block;margin-top:var(--space-3);">Use the same email address you entered above as your payment reference so our team can match your payment. Our team confirms receipt on the Paystack account and marks your registration fee as paid &mdash; you don't need to upload proof.</span>
          </div>

          <div class="form-section">
            <div class="checkbox-field">
              <input type="checkbox" id="agreed_terms" name="agreed_terms" required />
              <label for="agreed_terms">I agree to the Elite Traders Lounge Family Service Agreement (emailed to me on submission), the <a href="./terms.html">Terms &amp; Conditions</a>, the Appendix C rate bands shown above, and the <a href="./policies.html#refund-policy">Refund &amp; Cancellation Policy</a>. I understand Elite Traders Lounge reserves the right to refuse or cancel service to any user who provides false information or breaches its rules.</label>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn--primary" id="booking-submit">Submit booking request</button>
            </div>
            <div class="alert alert--error" id="booking-error" hidden>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
              <span id="booking-error-text">Something went wrong.</span>
            </div>
          </div>
        </form>

        <div id="booking-result" hidden>
          <div class="alert alert--success">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4M12 3l7 3v6c0 5-3 8.5-7 9-4-.5-7-4-7-9V6l7-3Z"/></svg>
            <span id="result-message">Booking request received. Save your reference and PIN below &mdash; you and your babysitter both need them to confirm arrival and departure.</span>
            <span class="badge-verified badge-verified--pending" style="margin-left: var(--space-3);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>Verification pending</span>
          </div>
          <div class="booking-ref-box">
            <div class="booking-ref-box__item"><span>Booking reference</span><strong id="result-ref">&ndash;</strong></div>
            <div class="booking-ref-box__item"><span>PIN</span><strong id="result-pin">&ndash;</strong></div>
          </div>
          <p class="form-section__hint" style="margin-top: var(--space-6);">Share the reference and PIN with your babysitter. When they arrive, both of you confirm on the <a href="./checkin.html">check-in page</a> &mdash; that's what starts the clock on worked hours.</p>
          <a href="./checkin.html" class="btn btn--secondary" style="margin-top: var(--space-4);">Go to check-in tool</a>
          <a href="#" id="result-contract-link" class="btn btn--secondary" style="margin-top: var(--space-4); margin-left: var(--space-3);" target="_blank" rel="noopener" hidden>Download Family Service Agreement</a>
        </div>
      </div>
    </div>
  </section>
'''


CHECKIN_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Confirm arrival &amp; departure</span></div>
      <span class="eyebrow">Dual-party confirmation</span>
      <h1>Confirm arrival and departure to protect worked hours.</h1>
      <p>Both the babysitter and the parent/guardian must independently confirm using the booking reference and PIN. A session's start time is the confirmed arrival of both parties; the end time is the confirmed departure of both parties. This protects the babysitter's pay, the family's booking, and gives Elite Traders Lounge a clear, timestamped record for any dispute.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container">
      <div class="checkin-grid">

        <div class="form-shell">
          <div class="form-section" style="margin-top:0; padding-top:0; border-top:none;">
            <div class="form-section__title">Confirm your arrival or departure</div>
            <div class="form-section__hint">Enter the booking reference and PIN shared with you, choose your role and whether you're arriving or leaving.</div>

            <form id="checkin-form" novalidate>
              <div class="field-grid">
                <div class="field">
                  <label for="booking_ref">Booking reference</label>
                  <input type="text" id="booking_ref" name="booking_ref" required placeholder="ETL-XXXXXX" autocapitalize="characters" />
                </div>
                <div class="field">
                  <label for="pin">4-digit PIN</label>
                  <input type="text" id="pin" name="pin" required inputmode="numeric" maxlength="4" placeholder="1234" />
                </div>
              </div>

              <div class="field">
                <label>I am the...</label>
                <div class="role-toggle" role="group" aria-label="Select your role">
                  <button type="button" data-role="sitter" aria-pressed="true">Babysitter</button>
                  <button type="button" data-role="parent" aria-pressed="false">Parent / guardian</button>
                </div>
              </div>

              <div class="field">
                <label>I am confirming my...</label>
                <div class="action-toggle">
                  <label><input type="radio" name="action" value="arrival" checked /> Arrival</label>
                  <label><input type="radio" name="action" value="departure" /> Departure</label>
                </div>
              </div>

              <div class="field">
                <label for="note">Note <span class="field__hint">(optional)</span></label>
                <input type="text" id="note" name="note" maxlength="200" placeholder="e.g. Arrived at the front gate" />
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn--primary" id="checkin-submit">Confirm now</button>
                <button type="button" class="btn btn--ghost" id="checkin-lookup">Look up booking status</button>
              </div>
              <div class="alert alert--success" id="checkin-success" hidden>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4M12 3l7 3v6c0 5-3 8.5-7 9-4-.5-7-4-7-9V6l7-3Z"/></svg>
                <span id="checkin-success-text">Confirmed.</span>
              </div>
              <div class="alert alert--error" id="checkin-error" hidden>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></svg>
                <span id="checkin-error-text">Something went wrong.</span>
              </div>
            </form>
          </div>
        </div>

        <div class="status-card" id="status-card">
          <h3>Booking status</h3>
          <p class="form-section__hint" id="status-empty">Confirm an arrival or departure, or look up a booking, to see live status here.</p>
          <div id="status-content" hidden>
            <div class="status-row">
              <span>Babysitter arrival</span>
              <span><span class="status-pill" id="pill-sitter-arrival">Pending</span> <span class="status-timestamp" id="ts-sitter-arrival"></span></span>
            </div>
            <div class="status-row">
              <span>Parent/guardian arrival</span>
              <span><span class="status-pill" id="pill-parent-arrival">Pending</span> <span class="status-timestamp" id="ts-parent-arrival"></span></span>
            </div>
            <div class="status-row">
              <span>Babysitter departure</span>
              <span><span class="status-pill" id="pill-sitter-departure">Pending</span> <span class="status-timestamp" id="ts-sitter-departure"></span></span>
            </div>
            <div class="status-row">
              <span>Parent/guardian departure</span>
              <span><span class="status-pill" id="pill-parent-departure">Pending</span> <span class="status-timestamp" id="ts-parent-departure"></span></span>
            </div>
            <div class="worked-hours-banner" id="worked-hours-banner" hidden>
              <span>Confirmed worked hours</span>
              <strong id="worked-hours-value">&ndash;</strong>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
'''


POLICIES_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Policies</span></div>
      <span class="eyebrow">Contract terms &amp; policies</span>
      <h1>Rates, refunds, and the rules that protect everyone.</h1>
      <p>This page summarises the key clauses of the Elite Traders Lounge Babysitter Contract that apply to every booking &mdash; minimum wage compliance, commission, cancellations, conduct, disputes, and data protection.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <div class="policy-toc">
        <a href="#minimum-wage">3.2 Minimum wage compliance</a>
        <a href="#rate-bands">Appendix C &middot; rate bands</a>
        <a href="#booking-hours">Minimum booking hours</a>
        <a href="#commission">5.3 Commission structure</a>
        <a href="#refund-policy">6. Refund &amp; cancellation policy</a>
        <a href="#conduct">Code of conduct</a>
        <a href="#disputes">Dispute resolution</a>
        <a href="#termination">Termination &amp; suspension</a>
        <a href="#popia">Data protection (POPIA)</a>
        <a href="#tax">Tax obligations</a>
      </div>

      <div class="policy-section" id="minimum-wage">
        <h2>3.2 Minimum Wage Compliance</h2>
        <p>The Babysitter acknowledges that:</p>
        <ul>
          <li>Elite Traders Lounge uses experience-based, fixed rates (Level 1&ndash;4) as set out in <a href="#rate-bands">Appendix C: Rates &amp; Minimum Wage Check</a> &mdash; there is no negotiation of rate; the level determines the price.</li>
          <li>Every Level's fixed rate is set above the current National Minimum Wage &mdash; <strong>R30.23 per hour, effective 1 March 2026</strong> (Government Gazette No. 54075, published 3 February 2026, a 5.0% increase on the 2025 rate) &mdash; or the applicable rate at the time of service.</li>
          <li>If the National Minimum Wage is ever updated above a Level's fixed rate, that rate is automatically corrected up to the compliant minimum until Appendix C is revised.</li>
          <li>The Family and Babysitter select the appropriate level (1&ndash;4) and booking type as described in Appendix C before booking confirmation; the rate and commission split are applied automatically.</li>
        </ul>
        <div class="policy-callout"><strong>2026/2027 rate note:</strong> The National Minimum Wage increased from R28.79/hour (2025) to R30.23/hour effective 1 March 2026. Elite Traders Lounge reviews and updates this figure whenever the Department of Employment and Labour publishes a new Government Gazette rate, and the platform's booking system automatically enforces the current rate at the time of service.</div>
      </div>

      <div class="policy-section" id="rate-bands">
        <h2>Appendix C &middot; Rates &amp; Minimum Wage Check</h2>
        <p>Every Level has one fixed rate &mdash; there is no negotiation. Elite Traders Lounge's total commission is always <strong>20%</strong> of the babysitter's fee, split between what's added to the Family's bill and what's deducted from the Babysitter's payout; the split differs by Level but always adds up to 20%.</p>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Level</th><th>Experience</th><th>Booking type</th><th>Fixed rate</th><th>Minimum booking</th><th>Family commission</th><th>Sitter commission</th><th>Total</th></tr></thead>
            <tbody>
              <tr><td><span class="rate-badge">Level 1</span></td><td>Entry &middot; 0&ndash;1 year</td><td>Day</td><td><strong>R45</strong>/hr</td><td>5 hours</td><td>10%</td><td>10%</td><td>20%</td></tr>
              <tr><td><span class="rate-badge">Level 2</span></td><td>Standard &middot; 1&ndash;3 years, references</td><td>Day</td><td><strong>R55</strong>/hr</td><td>5 hours</td><td>8%</td><td>12%</td><td>20%</td></tr>
              <tr><td><span class="rate-badge">Level 3</span></td><td>Advanced &middot; 3+ years, First Aid/CPR</td><td>Day</td><td><strong>R65</strong>/hr</td><td>4 hours</td><td>7.5%</td><td>12.5%</td><td>20%</td></tr>
              <tr><td><span class="rate-badge">Level 3</span></td><td>Advanced &middot; night rate</td><td>Overnight</td><td><strong>R70</strong>/hr</td><td>10 hours</td><td>10%</td><td>10%</td><td>20%</td></tr>
              <tr><td><span class="rate-badge">Level 4</span></td><td>Specialist &middot; overnight / special needs</td><td>Overnight</td><td><strong>R85</strong>/hr</td><td>10 hours</td><td>10%</td><td>10%</td><td>20%</td></tr>
            </tbody>
          </table>
        </div>
        <p class="form-section__hint">If the National Minimum Wage is ever raised above a Level's fixed rate, the booking system automatically corrects that rate up to the legal minimum.</p>
      </div>

      <div class="policy-section" id="full-day-rates">
        <h2>Full-Day Flat Rate Options</h2>
        <p>As an alternative to hourly billing, Families booking a Day booking (Levels 1&ndash;3) may instead select the flat full-day rate for a 7-hour day. Multi-day bookings are billed in 7-hour blocks (2 days = 14 hours, and so on). The same commission split above applies to full-day bookings.</p>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Level</th><th>Flat day rate (7 hours)</th></tr></thead>
            <tbody>
              <tr><td><span class="rate-badge">Level 1</span></td><td><strong>R315</strong>/day</td></tr>
              <tr><td><span class="rate-badge">Level 2</span></td><td><strong>R385</strong>/day</td></tr>
              <tr><td><span class="rate-badge">Level 3</span></td><td><strong>R450</strong>/day</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="policy-section" id="booking-hours">
        <h2>Minimum Booking Hours</h2>
        <ul>
          <li><strong>Level 1 &amp; 2 day bookings:</strong> minimum 5 consecutive hours.</li>
          <li><strong>Level 3 day bookings:</strong> minimum 4 consecutive hours.</li>
          <li><strong>Full-day flat rate bookings:</strong> billed in 7-hour blocks (1 day = 7 hours, 2 days = 14 hours, etc).</li>
          <li><strong>Overnight bookings (Level 3 &amp; 4):</strong> minimum 10 consecutive hours, billed at the applicable overnight rate for the babysitter's level.</li>
        </ul>
        <p>Bookings submitted below the applicable minimum are rejected by the booking system and must be resubmitted at or above the minimum duration.</p>
      </div>

      <div class="policy-section" id="commission">
        <h2>5.3 Commission Structure</h2>
        <p>Elite Traders Lounge's total commission is always <strong>20%</strong> of the babysitter's fee, charged on <strong>both sides</strong> of every booking: the Family pays the babysitter's booking fee <em>plus</em> a commission percentage as an added charge, and the babysitter's payout has a commission percentage deducted from their fee &mdash; the two percentages differ by Level but always add up to 20%. Every booking is paid once, through Paystack Split Payment, at the Family's total amount (fee + family-side commission). Paystack automatically splits that single payment and pays the babysitter's net share (fee minus sitter-side commission) directly into the babysitter's own Paystack account, while Elite Traders Lounge's combined commission share is paid directly into Elite Traders Lounge's Paystack account &mdash; on the same transaction, with no wallet held by Elite Traders Lounge at any point. Worked examples, at each Level's minimum booking:</p>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Service component</th><th>Level</th><th>Babysitter fee</th><th>+ Family commission</th><th>= Family pays</th><th>&ndash; Sitter commission</th><th>Net to babysitter</th></tr></thead>
            <tbody>
              <tr><td>5-hour day @ R45/hour</td><td>Level 1 &ndash; Entry</td><td><strong>R225</strong></td><td>R22.50 (10%)</td><td><strong>R247.50</strong></td><td>R22.50 (10%)</td><td><strong>R202.50</strong></td></tr>
              <tr><td>5-hour day @ R55/hour</td><td>Level 2 &ndash; Standard</td><td><strong>R275</strong></td><td>R22 (8%)</td><td><strong>R297</strong></td><td>R33 (12%)</td><td><strong>R242</strong></td></tr>
              <tr><td>4-hour day @ R65/hour</td><td>Level 3 &ndash; Advanced</td><td><strong>R260</strong></td><td>R19.50 (7.5%)</td><td><strong>R279.50</strong></td><td>R32.50 (12.5%)</td><td><strong>R227.50</strong></td></tr>
              <tr><td>10-hour overnight @ R70/hour</td><td>Level 3 &ndash; Night</td><td><strong>R700</strong></td><td>R70 (10%)</td><td><strong>R770</strong></td><td>R70 (10%)</td><td><strong>R630</strong></td></tr>
              <tr><td>10-hour overnight @ R85/hour</td><td>Level 4 &ndash; Specialist</td><td><strong>R850</strong></td><td>R85 (10%)</td><td><strong>R935</strong></td><td>R85 (10%)</td><td><strong>R765</strong></td></tr>
            </tbody>
          </table>
        </div>
        <p class="form-section__hint">Elite Traders Lounge's total revenue per booking is the sum of both commission amounts (family-side + sitter-side) &mdash; always 20% of the babysitter's fee, e.g. R45 total on the Level 1 example above.</p>
      </div>

      <div class="policy-section" id="refund-policy">
        <h2>6. Cancellation Policy</h2>

        <h3>6.1 Family Cancellation (Before Service Rendered)</h3>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Cancellation timing</th><th>Babysitter compensation</th><th>Family refund</th></tr></thead>
            <tbody>
              <tr><td>&ge;48 hours before booking</td><td>R0 (no charge)</td><td>100% refund via Paystack to the original payment method</td></tr>
              <tr><td>24&ndash;48 hours before booking</td><td>50% of the agreed net amount</td><td>50% refund via Paystack to the original payment method</td></tr>
              <tr><td>&lt;24 hours before booking</td><td>75% of the agreed net amount</td><td>25% refund via Paystack to the original payment method</td></tr>
              <tr><td>No-show (Family absent)</td><td>100% of the agreed net amount</td><td>R0 refund (full charge)</td></tr>
            </tbody>
          </table>
        </div>
        <p><strong>Process:</strong> Family must cancel through the Elite Traders Lounge app or email <a href="mailto:lemo.masethe@elitetraders.co.za">lemo.masethe@elitetraders.co.za</a>. Include the booking reference number and reason for cancellation. Refund is processed via Paystack back to the Family's original payment method within 3&ndash;5 business days.</p>

        <h3>6.2 Babysitter Cancellation (Before Service Rendered)</h3>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Cancellation timing</th><th>Babysitter compensation</th><th>Family refund</th></tr></thead>
            <tbody>
              <tr><td>&ge;48 hours before booking</td><td>R0 (no charge)</td><td>100% refund via Paystack to the original payment method</td></tr>
              <tr><td>24&ndash;48 hours before booking</td><td>25% net amount (Babysitter forfeits 75%)</td><td>75% refund via Paystack to the original payment method</td></tr>
              <tr><td>&lt;24 hours before booking</td><td>50% net amount (Babysitter forfeits 50%)</td><td>50% refund via Paystack to the original payment method</td></tr>
              <tr><td>No-show (Babysitter absent)</td><td>R0 (forfeits 100%)</td><td>100% refund via Paystack to the Family's original payment method; profile suspended pending review</td></tr>
            </tbody>
          </table>
        </div>
        <p><strong>Process:</strong> Babysitter must cancel through the Elite Traders Lounge app or email. Include the booking reference number and reason. Notification MUST be given at least 5 hours before the agreed start time.</p>

        <h3>6.3 Cancellation After Service Commenced</h3>
        <ul>
          <li>If either party cancels after the Babysitter arrives: full payment is due for hours already worked (minimum 1 hour).</li>
          <li>If Family requests Babysitter to leave early: payment due for actual hours worked at the agreed hourly rate.</li>
          <li>No refunds for early departure initiated by Family.</li>
        </ul>
      </div>

      <div class="policy-section" id="conduct">
        <h2>Code of Conduct</h2>
        <ul>
          <li>Babysitters must arrive on time, follow the Family's written care instructions, and never leave a child unsupervised.</li>
          <li>No smoking, alcohol, or unauthorised guests are permitted while a Babysitter is on duty.</li>
          <li>Families and Babysitters must treat each other with respect &mdash; discriminatory, abusive, or unsafe behaviour by either party is grounds for immediate suspension.</li>
          <li>Any injury, incident, or safety concern must be reported to Elite Traders Lounge and, where relevant, emergency services, as soon as possible.</li>
          <li>Photos or personal information about a Family or child may not be shared publicly by a Babysitter without written consent.</li>
        </ul>
      </div>

      <div class="policy-section" id="disputes">
        <h2>Dispute Resolution</h2>
        <ul>
          <li>Parties should first attempt to resolve any disagreement directly, within 24 hours of it arising.</li>
          <li>If unresolved, either party may submit a formal complaint to Elite Traders Lounge with the booking reference number and supporting evidence (e.g. check-in/check-out timestamps, messages, photos).</li>
          <li>Elite Traders Lounge investigates within 5 business days and issues a written decision within 10 business days.</li>
          <li>Dual-party check-in/check-out timestamps recorded through the <a href="./checkin.html">check-in tool</a> are treated as the primary evidence of worked hours in any dispute.</li>
          <li>Either party may escalate an unresolved dispute to independent arbitration or the CCMA/relevant regulator after the internal process concludes.</li>
        </ul>
      </div>

      <div class="policy-section" id="termination">
        <h2>Termination &amp; Suspension</h2>
        <ul>
          <li>Either party may deactivate their account at any time; bookings already confirmed remain subject to the Cancellation Policy above.</li>
          <li>Elite Traders Lounge may suspend or terminate an account for a no-show, safety violation, fraudulent information, harassment, or repeated policy breaches.</li>
          <li>A suspended Babysitter's pending payouts are held pending the outcome of any related investigation or dispute.</li>
          <li>Elite Traders Lounge reserves the right to refuse service or booking access to any party found to have provided false identity, banking, or reference information.</li>
        </ul>
      </div>

      <div class="policy-section" id="popia">
        <h2>Data Protection (POPIA)</h2>
        <ul>
          <li>Elite Traders Lounge processes personal information (identity, contact, banking, and location details) strictly to verify identity, facilitate bookings, process payments, and maintain safety records, in line with the Protection of Personal Information Act (POPIA).</li>
          <li>Identity verification data (e.g. Smile ID checks) is stored securely and is not shared with third parties beyond what is required for verification and legal compliance.</li>
          <li>Check-in/check-out timestamps and booking records are retained to resolve disputes and support labour-law compliance, and are only accessible to the parties involved and Elite Traders Lounge administrators.</li>
          <li>Users may request access to, correction of, or deletion of their personal information (subject to legal retention requirements) by emailing <a href="mailto:lemo.masethe@elitetraders.co.za">lemo.masethe@elitetraders.co.za</a>.</li>
        </ul>
      </div>

      <div class="policy-section" id="tax">
        <h2>Tax Obligations</h2>
        <ul>
          <li>Babysitters engage as independent contractors, not employees of Elite Traders Lounge or of the Family.</li>
          <li>Net income received after commission is taxable under South African law and should be declared to SARS by the Babysitter.</li>
          <li>Elite Traders Lounge does not withhold PAYE and does not provide tax advice; Babysitters should keep their own transaction records and consult a registered tax practitioner as needed.</li>
        </ul>
      </div>

      <p style="margin-top: var(--space-10); color: var(--color-text-faint); font-size: var(--text-xs);">This page summarises key clauses of the Elite Traders Lounge Babysitter Contract for reference. In the event of any conflict, the signed contract between the parties and Elite Traders Lounge governs.</p>
    </div>
  </section>
'''


TERMS_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Terms &amp; Conditions</span></div>
      <span class="eyebrow">Legal</span>
      <h1>Terms &amp; Conditions</h1>
      <p>These Terms &amp; Conditions govern use of the Elite Traders Lounge platform by babysitters ("Babysitters") and parents/guardians ("Families"). By registering, booking, or accepting a booking, you agree to these terms, the Elite Traders Lounge Babysitter Contract or Family Service Agreement issued to you on registration, and the <a href="./policies.html">Rates &amp; Policies</a> page. Where these terms and your signed contract conflict, the signed contract governs.</p>
      <p class="form-section__hint">Last updated: 31 August 2026.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">
      <div class="policy-toc">
        <a href="#acceptance">1. Acceptance &amp; digital signature</a>
        <a href="#eligibility">2. Eligibility &amp; identity verification</a>
        <a href="#proof-of-address">3. Proof of address</a>
        <a href="#reference-affidavit">4. Reference &amp; affidavit</a>
        <a href="#service-area-terms">5. Local service area (40km radius)</a>
        <a href="#payments">6. Payments (Paystack)</a>
        <a href="#contracts">7. Individual contracts &amp; delivery</a>
        <a href="#conduct-terms">8. Platform role &amp; conduct</a>
        <a href="#suspension">9. Right to refuse or cancel service</a>
        <a href="#liability">10. Limitation of liability</a>
        <a href="#changes">11. Changes to these terms</a>
        <a href="#governing-law">12. Governing law</a>
        <a href="#contact-terms">13. Contact</a>
      </div>

      <div class="policy-section" id="acceptance">
        <h2>1. Acceptance &amp; Digital Signature</h2>
        <ul>
          <li>Creating a profile, submitting a registration form, or ticking the agreement checkbox on the Elite Traders Lounge website constitutes a binding digital signature and acceptance of these Terms &amp; Conditions and the accompanying contract emailed to you.</li>
          <li>You must be at least 18 years old and legally capable of entering into a binding contract to register as a Babysitter or as a Family representative.</li>
          <li>If you register on behalf of a household, you confirm you are authorised to bind that household to these terms.</li>
        </ul>
      </div>

      <div class="policy-section" id="eligibility">
        <h2>2. Eligibility &amp; Identity Verification</h2>
        <ul>
          <li><strong>South African citizens and permanent residents</strong> register using a valid South African ID number.</li>
          <li><strong>Foreign nationals</strong> may register as freelance Babysitters using a valid passport, provided they hold a valid work permit or other legal authorisation to perform paid work in South Africa under the Immigration Act 13 of 2002. Elite Traders Lounge does not place or pay any Babysitter who cannot demonstrate the legal right to work in South Africa, and reserves the right to request the physical work permit document at any time.</li>
          <li>All Families and Babysitters must complete identity verification through <strong>Smile ID</strong> (document authentication and facial liveness check) before a Babysitter is placed in, or a Family may book care at, a household. Bookings and placements are provisional until Smile ID verification is complete.</li>
          <li>Providing false, forged, or expired identity documents is grounds for immediate account suspension and may be reported to the relevant authorities.</li>
          <li><strong>Every Babysitter must hold a valid SAPS Police Clearance Certificate and a Child Protection Register (Part B) clearance letter</strong> confirming they are not listed as unsuitable to work with children, submitted at registration and reviewed by Elite Traders Lounge before verified status is granted.</li>
          <li><strong>Foreign national Babysitters must additionally provide a police clearance certificate from any country they resided in for 12 or more months as an adult within the preceding 5 years</strong>, in line with the definition used under the Immigration Act 13 of 2002, each dated within 6 months of submission.</li>
          <li><strong>Annual re-verification.</strong> To remain eligible for placement, every Babysitter &mdash; South African or foreign national &mdash; must renew their Police Clearance Certificate and Child Protection Register (Part B) clearance every 12 months from the date the current documents were accepted, submitted via the Babysitter's dashboard. Elite Traders Lounge may suspend or withdraw a Babysitter's verified status, and remove them from public search results, if renewal documents are not submitted by the due date.</li>
        </ul>
      </div>

      <div class="policy-section" id="proof-of-address">
        <h2>3. Proof of Address</h2>
        <ul>
          <li>Both Babysitters and Families must provide proof of address &mdash; a utility bill, bank statement, lease agreement, or a sworn affidavit confirming residential address &mdash; dated within the last three (3) months.</li>
          <li>Proof of address is used to confirm the Babysitter's home address for safety and background checks, and the Family's address as the verified location where care will be provided.</li>
          <li>Elite Traders Lounge may request an updated proof of address at any time, including where an address on file appears out of date.</li>
        </ul>
      </div>

      <div class="policy-section" id="reference-affidavit">
        <h2>4. Reference &amp; Affidavit</h2>
        <ul>
          <li>Every Babysitter must supply at least one contactable reference (name, relationship, phone number, and email address) at the time of registration.</li>
          <li>The nominated reference will be asked to complete the standard Elite Traders Lounge Reference Affidavit (Appendix A of the Babysitter Contract), sworn before a Commissioner of Oaths, confirming their relationship to the Babysitter and their honest assessment of the Babysitter's character and childcare experience.</li>
          <li>Elite Traders Lounge may contact the reference directly by phone or email to verify the information supplied and confirm the affidavit's authenticity.</li>
          <li>A Babysitter profile is marked "Reference Verified" only once a completed, signed affidavit has been received and checked.</li>
        </ul>
        <div class="policy-callout"><strong>Appendix A &mdash; Standard Reference Affidavit (template):</strong>
          <p style="margin-top: var(--space-3);">I, the undersigned, ____________________ (full name), holder of South African ID / Passport number ____________________, residing at ____________________, do hereby state under oath that:</p>
          <ol>
            <li>I have known ____________________ (Babysitter's full name) in the capacity of ____________________ (relationship, e.g. employer, colleague, family friend) for a period of ____________________.</li>
            <li>To the best of my knowledge, the above-named person is of good character, trustworthy, and has not, to my knowledge, engaged in any conduct that would render them unsuitable to care for children.</li>
            <li>I am aware that this statement may be relied upon by Elite Traders Lounge and by Families booking childcare services through Elite Traders Lounge, and I make this statement freely and voluntarily without undue influence.</li>
            <li>I can be contacted at the phone number and email address I have supplied to confirm this statement if required.</li>
          </ol>
          <p>Signed at ____________________ on this ____ day of ____________________ 20____.</p>
          <p>Signature of Deponent: ____________________&nbsp;&nbsp;&nbsp;&nbsp;Signature &amp; stamp of Commissioner of Oaths: ____________________</p>
          <p style="margin-bottom:0;">This template is provided by Elite Traders Lounge to protect Babysitters, Families, and Elite Traders Lounge itself, and does not constitute legal advice. Parties may consult an attorney regarding its use.</p>
        </div>
      </div>

      <div class="policy-section" id="service-area-terms">
        <h2>5. Local Service Area (40km Radius)</h2>
        <ul>
          <li>Elite Traders Lounge can only confirm a booking where a verified, active Babysitter is located within a <strong>40km travel radius</strong> of the Family's registered town or suburb ("local service area") &mdash; this is considered the practical distance a Babysitter can reasonably and safely travel to reach a booking.</li>
          <li>Both Babysitters and Families must supply their town/suburb and province at registration or booking, so Elite Traders Lounge can calculate this distance. This is a mandatory condition of registration and booking, not an optional field.</li>
          <li>Families are encouraged to check whether a verified Babysitter currently covers their area &mdash; using the "Check if we cover your area" tool on the website or the sitter list shown when booking &mdash; before completing registration or a booking request.</li>
          <li>Where no verified Babysitter is within 40km of a Family's location, Elite Traders Lounge will decline the booking request and will contact the Family to discuss options, including the possibility of onboarding a Babysitter closer to them.</li>
          <li>The list of towns currently covered by a verified Babysitter is shown on the website and updates automatically as new Babysitters register and complete verification &mdash; it is not a fixed or guaranteed list, and coverage may change over time as Babysitters join, leave, or update their status.</li>
          <li>This policy exists solely to ensure a Babysitter can realistically and safely attend a booking; it does not limit a Babysitter's or Family's right to independently arrange care outside of the Elite Traders Lounge platform.</li>
        </ul>
      </div>

      <div class="policy-section" id="payments">
        <h2>6. Payments (Paystack)</h2>
        <ul>
          <li>All booking payments are processed through <strong>Paystack</strong> using Paystack's Split Payment functionality. A Family's payment for a booking is made once, and Paystack automatically splits and pays the Babysitter's net share directly to the Babysitter's own Paystack account and Elite Traders Lounge's commission share directly to Elite Traders Lounge's own Paystack account, on the same transaction.</li>
          <li>Both Babysitters and Families must hold their own active Paystack account and supply the email address linked to that account at registration, so Elite Traders Lounge can confirm the account exists before enabling payouts or bookings.</li>
          <li><strong>Elite Traders Lounge does not hold, custody, or accept responsibility for any wallet balance.</strong> Funds in transit are held and disbursed by Paystack as the payment processor, subject to Paystack's own terms of service; Elite Traders Lounge's role is limited to configuring the commission split and facilitating bookings.</li>
          <li>Total commission is always 20% of the babysitter's fee, split between the Family and the Babysitter at a ratio that depends on level and booking type (per Appendix C) and deducted automatically as part of the Paystack split &mdash; no additional platform or service fee is charged on top of this commission.</li>
          <li>Refunds for eligible cancellations (see <a href="./policies.html#refund-policy">Refund &amp; Cancellation Policy</a>) are issued via Paystack back to the Family's original payment method.</li>
          <li><strong>Annual registration &amp; verification fee &mdash; R99.</strong> Every Babysitter and every Family pays an R99 fee to cover identity and document verification, payable via the Paystack payment link provided on the registration and booking forms. This fee is completely separate from, and in addition to, the booking commission described above, and is not refundable once verification has begun. Because Babysitters must renew their Police Clearance Certificate and Child Protection Register clearance every 12 months, and Families' identity details are re-confirmed on the same cycle, this fee is charged annually rather than once &mdash; it is due again 12 months after it was last confirmed paid.</li>
        </ul>
      </div>

      <div class="policy-section" id="contracts">
        <h2>7. Individual Contracts &amp; Delivery</h2>
        <ul>
          <li>On successful registration, Elite Traders Lounge issues each Babysitter the current Babysitter Agreement and each Family the current Family Service Agreement by email to the address supplied, and makes a downloadable copy available from the confirmation screen.</li>
          <li>These individual contracts set out the specific rate band, commission, minimum-wage compliance, and cancellation terms that apply to that party, and incorporate these Terms &amp; Conditions and the <a href="./policies.html">Rates &amp; Policies</a> page by reference.</li>
          <li>It is each party's responsibility to read the emailed contract and raise any queries with Elite Traders Lounge before accepting or confirming a booking.</li>
        </ul>
      </div>

      <div class="policy-section" id="conduct-terms">
        <h2>8. Platform Role &amp; Conduct</h2>
        <ul>
          <li>Elite Traders Lounge operates as a booking and verification platform connecting independent Babysitters with Families. Babysitters engage as independent contractors and are not employees of Elite Traders Lounge.</li>
          <li>Both parties must use the <a href="./checkin.html">dual-party check-in tool</a> to confirm arrival and departure at every booking; timestamps recorded there are treated as the primary evidence of hours worked in any dispute.</li>
          <li>The full Code of Conduct, Dispute Resolution process, and Termination &amp; Suspension terms are set out on the <a href="./policies.html#conduct">Policies page</a> and form part of these Terms.</li>
        </ul>
        <div class="policy-callout"><strong>Scope of duties &mdash; strictly limited to childcare:</strong>
          <ul style="margin-top: var(--space-3); margin-bottom: 0;">
            <li><strong>No administration of medicine.</strong> A Babysitter may never administer any medicine, supplement, or medical treatment of any kind to a child in their care, under any circumstances, regardless of any instruction given by the Family. If a Family or Babysitter breaches this rule, Elite Traders Lounge accepts no liability whatsoever for any resulting harm, loss, or damage, and the breaching party or parties bear full responsibility.</li>
            <li><strong>No cleaning or general household duties.</strong> A Babysitter's duties are limited strictly to the direct care and supervision of the child or children being minded &mdash; including only those specific tasks (such as bathing or feeding) that the Family has indicated when making the booking. Babysitters are not required, and must not be asked, to perform housecleaning, laundry, cooking for the household, or any other duty unrelated to childcare.</li>
            <li><strong>Pet disclosure.</strong> Families must disclose at the time of booking whether there are pets in the home and, if so, what type, so that Elite Traders Lounge and the Babysitter can take appropriate precautions for the safety of the children and the Babysitter. Failure to disclose pets is a breach of these Terms.</li>
          </ul>
        </div>
      </div>

      <div class="policy-section" id="suspension">
        <h2>9. Right to Refuse or Cancel Service</h2>
        <div class="policy-callout"><strong>Disclaimer:</strong> Elite Traders Lounge reserves the right, at its sole discretion, to refuse, suspend, or cancel service to, and to decline to onboard or continue working with, any Babysitter or Family who:
          <ul style="margin-top: var(--space-3); margin-bottom: 0;">
            <li>provides false, forged, incomplete, or misleading identity, address, reference, work-permit, or Paystack account information;</li>
            <li>fails Smile ID verification or refuses to complete it;</li>
            <li>breaches the Code of Conduct, engages in unsafe, abusive, discriminatory, or fraudulent behaviour, or endangers a child's safety;</li>
            <li>has an unresolved dispute, repeated cancellations, or repeated no-shows; or</li>
            <li>otherwise breaches these Terms, the Policies, or their individual contract.</li>
          </ul>
        </div>
        <p>This right may be exercised without prior notice where safety is at risk, and with reasonable notice in all other cases. Exercising this right does not entitle the affected party to compensation beyond amounts already earned for services actually rendered.</p>
      </div>

      <div class="policy-section" id="liability">
        <h2>10. Limitation of Liability</h2>
        <ul>
          <li>Elite Traders Lounge verifies identity, proof of address, and references on a best-efforts basis but does not guarantee the conduct, performance, or suitability of any Babysitter or Family, and is not liable for any loss, injury, or damage arising from a booking arranged through the platform.</li>
          <li>As set out in Section 8 above, Elite Traders Lounge is not liable for any harm, loss, or damage arising from a Babysitter administering medicine to a child, or from either party breaching the duties, pet-disclosure, or no-cleaning rules described there.</li>
          <li>Elite Traders Lounge is not a party to, and is not liable for, the processing, custody, or timing of payments handled by Paystack; any payment dispute involving Paystack is subject to Paystack's own terms and support channels.</li>
          <li>Nothing in these Terms excludes any liability that cannot lawfully be excluded under South African law.</li>
        </ul>
      </div>

      <div class="policy-section" id="changes">
        <h2>11. Changes to These Terms</h2>
        <p>Elite Traders Lounge may update these Terms &amp; Conditions, the Policies page, or Appendix C rate bands from time to time, including to reflect changes in the National Minimum Wage. Material changes will be posted on this page with an updated "last updated" date; continued use of the platform after changes take effect constitutes acceptance of the revised terms.</p>
      </div>

      <div class="policy-section" id="governing-law">
        <h2>12. Governing Law</h2>
        <p>These Terms are governed by the laws of the Republic of South Africa, including the Protection of Personal Information Act (POPIA), the Basic Conditions of Employment Act, and the Immigration Act 13 of 2002. The courts of South Africa have jurisdiction over any dispute not resolved through the process described on the <a href="./policies.html#disputes">Policies page</a>.</p>
      </div>

      <div class="policy-section" id="contact-terms">
        <h2>13. Contact</h2>
        <p>Questions about these Terms &amp; Conditions can be sent to <a href="mailto:lemo.masethe@elitetraders.co.za">lemo.masethe@elitetraders.co.za</a> or <a href="tel:+27814270419">+27 81 427 0419</a>. Elite Traders Lounge, registration number K2017318876, 4017 Alek Mampana Street, Extension 7, Kwa-Guqa, Mpumalanga, 1039.</p>
      </div>

      <p style="margin-top: var(--space-10); color: var(--color-text-faint); font-size: var(--text-xs);">This page summarises the platform-wide Terms &amp; Conditions. Your individual Babysitter Agreement or Family Service Agreement, emailed to you on registration, governs the specific rates, commission, and obligations that apply to you.</p>
    </div>
  </section>
'''

ADMIN_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <span class="eyebrow">Private staff area</span>
      <h1>Admin dashboard</h1>
      <p>Verify babysitters and families, assign sitters to bookings, and check for schedule clashes. This page is not linked from the public site &mdash; keep the link private.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">

      <div class="dash-login" id="admin-login">
        <h2>Admin sign in</h2>
        <p>Enter the admin password to continue.</p>
        <div class="field">
          <label for="admin-password">Admin password</label>
          <input type="password" id="admin-password" autocomplete="current-password" />
        </div>
        <button type="button" class="btn btn--primary" id="admin-login-btn">Sign in</button>
        <div class="alert alert--error" id="admin-login-error" hidden style="margin-top: var(--space-4);">
          <span id="admin-login-error-text">Incorrect password.</span>
        </div>
      </div>

      <div class="dash-panel" id="admin-panel" hidden>
        <div class="dash-toolbar">
          <span class="dash-toolbar__who">Signed in as admin</span>
          <button type="button" class="btn btn--ghost btn--sm" id="admin-logout-btn">Sign out</button>
        </div>

        <div class="dash-tabs" role="tablist">
          <button type="button" class="dash-tab is-active" data-tab="sitters" role="tab">Babysitters</button>
          <button type="button" class="dash-tab" data-tab="bookings" role="tab">Bookings &amp; scheduling</button>
          <button type="button" class="dash-tab" data-tab="calendar" role="tab">Calendar</button>
        </div>

        <div class="dash-tabpanel" data-tabpanel="sitters">
          <div class="alert alert--info" style="margin-bottom: var(--space-5);">
            <span>Sitters and families now upload their ID and proof of address directly on the form &mdash; use the &ldquo;View&rdquo; links below each application to open the files, then tick each item once you've personally checked it. This is a manual review checklist, not automated verification.</span>
          </div>
          <div class="dash-card-list" id="sitters-list">
            <div class="dash-empty">Loading babysitters&hellip;</div>
          </div>
        </div>

        <div class="dash-tabpanel" data-tabpanel="bookings" hidden>
          <div class="dash-toolbar" style="margin-bottom: var(--space-5);">
            <span></span>
            <button type="button" class="btn btn--primary btn--sm" id="open-manual-booking-btn">+ New manual booking</button>
          </div>
          <div class="dash-card-list" id="bookings-list">
            <div class="dash-empty">Loading bookings&hellip;</div>
          </div>
        </div>

        <div class="dash-tabpanel" data-tabpanel="calendar" hidden>
          <div class="mini-cal mini-cal--admin" id="admin-calendar">
            <div class="mini-cal__head">
              <button type="button" class="mini-cal__nav" id="admin-cal-prev" aria-label="Previous month">&larr;</button>
              <h3 id="admin-cal-title">This month</h3>
              <button type="button" class="mini-cal__nav" id="admin-cal-next" aria-label="Next month">&rarr;</button>
            </div>
            <div class="mini-cal__grid" id="admin-cal-grid"></div>
            <div class="mini-cal__legend">
              <span><span class="mini-cal__swatch" style="background:var(--color-secondary-highlight);"></span>Has bookings (click a day for details)</span>
              <span><span class="mini-cal__swatch" style="background:var(--color-warning-highlight);"></span>Pending assignment</span>
            </div>
          </div>
          <div id="admin-cal-day-detail" class="admin-cal-day-detail" hidden></div>
        </div>
      </div>

      <div class="modal-overlay" id="manual-booking-modal" hidden>
        <div class="modal-box">
          <div class="modal-box__head">
            <h2>New manual booking</h2>
            <button type="button" class="btn btn--ghost btn--sm" id="close-manual-booking-btn">Close</button>
          </div>
          <p class="form-section__hint">Use this to capture a booking over the phone or in case of a system error. No family document upload or Smile ID check is required here &mdash; you're vouching for this booking as admin.</p>
          <form id="manual-booking-form" novalidate>
            <div class="field-grid">
              <div class="field">
                <label for="mb_parent_name">Parent / guardian full name</label>
                <input type="text" id="mb_parent_name" name="parent_name" required />
              </div>
              <div class="field">
                <label for="mb_phone">Phone number</label>
                <input type="tel" id="mb_phone" name="phone" required />
              </div>
            </div>
            <div class="field-grid">
              <div class="field">
                <label for="mb_email">Email address <span class="field__hint">(optional)</span></label>
                <input type="email" id="mb_email" name="email" />
              </div>
              <div class="field">
                <label for="mb_address">Home address</label>
                <input type="text" id="mb_address" name="address" required />
              </div>
            </div>
            <div class="field">
              <label for="mb_children_count">Number and ages of children</label>
              <input type="text" id="mb_children_count" name="children_count" required placeholder="e.g. 2 children, ages 3 and 6" />
            </div>
            <div class="field-grid field-grid--3">
              <div class="field">
                <label for="mb_rate_type">Booking type</label>
                <select id="mb_rate_type" name="rate_type" required>
                  <option value="day">Day</option>
                  <option value="overnight">Overnight</option>
                </select>
              </div>
              <div class="field">
                <label for="mb_level">Level</label>
                <select id="mb_level" name="level" required>
                  <option value="1">Level 1</option>
                  <option value="2">Level 2</option>
                  <option value="3">Level 3</option>
                  <option value="4">Level 4</option>
                </select>
              </div>
              <div class="field">
                <label for="mb_hourly_rate">Hourly rate (R)</label>
                <input type="number" id="mb_hourly_rate" name="hourly_rate" min="1" step="0.01" required />
              </div>
            </div>
            <div class="field-grid">
              <div class="field">
                <label for="mb_duration_hours">Duration (hours)</label>
                <input type="number" id="mb_duration_hours" name="duration_hours" min="1" step="0.5" required />
              </div>
              <div class="field">
                <label for="mb_booking_date">Booking date</label>
                <input type="date" id="mb_booking_date" name="booking_date" required />
              </div>
              <div class="field">
                <label for="mb_start_time">Start time</label>
                <input type="time" id="mb_start_time" name="start_time" required />
              </div>
            </div>
            <div class="field-grid">
              <div class="checkbox-field">
                <input type="checkbox" id="mb_has_pets" name="has_pets" />
                <label for="mb_has_pets">Family has pets</label>
              </div>
              <div class="field">
                <label for="mb_pet_type">Pet type <span class="field__hint">(if any)</span></label>
                <input type="text" id="mb_pet_type" name="pet_type" />
              </div>
            </div>
            <div class="field-grid">
              <div class="checkbox-field">
                <input type="checkbox" id="mb_special_bath_baby" name="special_bath_baby" />
                <label for="mb_special_bath_baby">Bath the baby/child</label>
              </div>
              <div class="checkbox-field">
                <input type="checkbox" id="mb_special_feed_baby" name="special_feed_baby" />
                <label for="mb_special_feed_baby">Feed the baby/child</label>
              </div>
            </div>
            <div class="field">
              <label for="mb_special_instructions">Care instructions / precautions <span class="field__hint">(optional)</span></label>
              <textarea id="mb_special_instructions" name="special_instructions"></textarea>
            </div>
            <div class="field">
              <label for="mb_assign_sitter_id">Assign a babysitter now <span class="field__hint">(optional)</span></label>
              <select id="mb_assign_sitter_id" name="assign_sitter_id"></select>
            </div>
            <div class="field">
              <label for="mb_admin_notes">Admin notes <span class="field__hint">(optional)</span></label>
              <textarea id="mb_admin_notes" name="admin_notes" placeholder="e.g. captured over the phone, system was down"></textarea>
            </div>
            <div class="alert alert--error" id="manual-booking-error" hidden>
              <span id="manual-booking-error-text">Something went wrong.</span>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn--primary" id="manual-booking-submit">Create booking</button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </section>
'''

SITTER_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <span class="eyebrow">Babysitter dashboard</span>
      <h1>Your bookings &amp; availability</h1>
      <p>Log in with the email you registered with and the access code you were given when you applied. Use this page to accept or decline bookings we've assigned to you and to mark dates you're unavailable.</p>
    </div>
  </section>

  <section class="section-pad section-pad--tight">
    <div class="container container--narrow">

      <div class="dash-login" id="sitter-login">
        <h2>Babysitter sign in</h2>
        <p>Don't have your access code? It was shown once when you registered, and your admin contact can look it up for you.</p>
        <div class="field">
          <label for="sitter-login-email">Email address</label>
          <input type="email" id="sitter-login-email" autocomplete="email" />
        </div>
        <div class="field">
          <label for="sitter-login-code">Access code</label>
          <input type="text" id="sitter-login-code" autocomplete="off" maxlength="8" style="text-transform:uppercase;" />
        </div>
        <button type="button" class="btn btn--primary" id="sitter-login-btn">Sign in</button>
        <div class="alert alert--error" id="sitter-login-error" hidden style="margin-top: var(--space-4);">
          <span id="sitter-login-error-text">That email and access code don't match.</span>
        </div>
      </div>

      <div class="dash-panel" id="sitter-panel" hidden>
        <div class="dash-toolbar">
          <span class="dash-toolbar__who" id="sitter-who">Signed in</span>
          <button type="button" class="btn btn--ghost btn--sm" id="sitter-logout-btn">Sign out</button>
        </div>

        <div class="dash-card" id="sitter-verification-panel" style="margin-bottom: var(--space-6);">
          <h2 style="font-size: var(--text-lg); margin-bottom: var(--space-3);">Verification &amp; annual fee</h2>
          <div id="sitter-verification-status">
            <div class="dash-empty">Loading verification status&hellip;</div>
          </div>
          <div id="sitter-renewal-box" hidden style="margin-top: var(--space-5);">
            <button type="button" class="btn btn--ghost btn--sm" id="sitter-renewal-toggle">Submit renewal documents</button>
            <form id="sitter-renewal-form" novalidate hidden style="margin-top: var(--space-4);">
              <div class="field">
                <label for="renew_police_clearance_document">New AFIS check or police clearance certificate <span class="field__hint">(required)</span></label>
                <input type="file" id="renew_police_clearance_document" name="renew_police_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
                <span class="file-status" id="renew_police_clearance_document-status"></span>
              </div>
              <div class="field">
                <label for="renew_child_protection_clearance_document">New Child Protection Register (Part B) clearance letter <span class="field__hint">(required)</span></label>
                <input type="file" id="renew_child_protection_clearance_document" name="renew_child_protection_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" required />
                <span class="file-status" id="renew_child_protection_clearance_document-status"></span>
              </div>
              <div class="field" id="sitter-renewal-foreign-field" hidden>
                <label for="renew_foreign_police_clearance_document">New foreign police clearance certificate <span class="field__hint">(required for non-SA sitters)</span></label>
                <input type="file" id="renew_foreign_police_clearance_document" name="renew_foreign_police_clearance_document" accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf" />
                <span class="file-status" id="renew_foreign_police_clearance_document-status"></span>
              </div>
              <div class="alert alert--error" id="sitter-renewal-error" hidden style="margin-top: var(--space-3);">
                <span id="sitter-renewal-error-text"></span>
              </div>
              <div class="alert alert--info" id="sitter-renewal-success" hidden style="margin-top: var(--space-3);">
                <span>Thanks &mdash; your renewal documents have been received. Our team will review them and confirm your verified status. You'll also need to pay the R99 annual fee again via the Paystack link below once you submit.</span>
              </div>
              <button type="submit" class="btn btn--primary" id="sitter-renewal-submit" style="margin-top: var(--space-3);">Submit renewal documents</button>
              <a href="https://paystack.shop/pay/-c63v2905q" target="_blank" rel="noopener" class="btn btn--ghost" id="sitter-renewal-pay-link" hidden style="margin-top: var(--space-3);">Pay R99 annual fee via Paystack</a>
            </form>
          </div>
        </div>

        <div class="mini-cal" id="sitter-calendar">
          <div class="mini-cal__head">
            <button type="button" class="mini-cal__nav" id="mini-cal-prev" aria-label="Previous month">&larr;</button>
            <h3 id="mini-cal-title">This month</h3>
            <button type="button" class="mini-cal__nav" id="mini-cal-next" aria-label="Next month">&rarr;</button>
          </div>
          <div class="mini-cal__grid" id="mini-cal-grid"></div>
          <div class="mini-cal__legend">
            <span><span class="mini-cal__swatch" style="background:var(--color-secondary-highlight);"></span>Booked</span>
            <span><span class="mini-cal__swatch" style="background:var(--color-warning-highlight);"></span>Marked unavailable (click to clear)</span>
            <span><span class="mini-cal__swatch" style="background:var(--color-surface-2);"></span>Available (click to mark unavailable)</span>
          </div>
        </div>

        <h2 style="font-size: var(--text-lg); margin-bottom: var(--space-4);">Assigned bookings</h2>
        <div class="dash-card-list" id="sitter-bookings-list">
          <div class="dash-empty">Loading your bookings&hellip;</div>
        </div>
      </div>

    </div>
  </section>
'''


(ROOT / "guide.html").write_text(
    page(
        "Getting Started Guide — Elite Traders Lounge",
        "A simple, step-by-step guide to creating a Paystack account and signing up as a babysitter or family on Elite Traders Lounge, with audio narration.",
        "guide",
        GUIDE_BODY,
    )
)

(ROOT / "register-sitter.html").write_text(
    page(
        "Register as a Babysitter — Elite Traders Lounge",
        "Sign up as a verified babysitter with Elite Traders Lounge. Select your experience level, get placed in the right Appendix C rate band, and get paid at or above the National Minimum Wage.",
        "register",
        REGISTER_BODY,
        extra_js=["selfie-capture.js", "register.js"],
    )
)

(ROOT / "book.html").write_text(
    page(
        "Book a Sitter — Elite Traders Lounge",
        "Register as a parent or guardian and book a verified babysitter. Live quote checked against Appendix C rate bands and the National Minimum Wage.",
        "book",
        BOOK_BODY,
        extra_js=["selfie-capture.js", "book.js"],
    )
)

(ROOT / "checkin.html").write_text(
    page(
        "Confirm Arrival & Departure — Elite Traders Lounge",
        "Dual-party check-in and check-out confirmation for babysitters and parents/guardians, so worked hours are protected for everyone.",
        "checkin",
        CHECKIN_BODY,
        extra_js="checkin.js",
    )
)

(ROOT / "policies.html").write_text(
    page(
        "Policies — Elite Traders Lounge",
        "Minimum wage compliance, rate bands, commission structure, and the full refund and cancellation policy for Elite Traders Lounge bookings.",
        "policies",
        POLICIES_BODY,
    )
)

(ROOT / "terms.html").write_text(
    page(
        "Terms & Conditions — Elite Traders Lounge",
        "Terms and conditions covering identity verification, proof of address, reference affidavits, Paystack payments, and the right to refuse or cancel service on Elite Traders Lounge.",
        "terms",
        TERMS_BODY,
    )
)

(ROOT / "admin.html").write_text(
    page(
        "Admin Dashboard — Elite Traders Lounge",
        "Private staff dashboard for verifying babysitters and families and assigning bookings.",
        "",
        ADMIN_BODY,
        extra_js="admin.js",
    )
)

(ROOT / "sitter-dashboard.html").write_text(
    page(
        "Babysitter Dashboard — Elite Traders Lounge",
        "Babysitter dashboard to accept or decline assigned bookings and manage availability.",
        "",
        SITTER_BODY,
        extra_js="sitter-dashboard.js",
    )
)

print("Pages written.")
