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
    extra = f'\n<script src="./{extra_js}" defer></script>' if extra_js else ''
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


REGISTER_BODY = '''
  <section class="page-hero">
    <div class="container container--narrow">
      <div class="breadcrumb"><a href="./index.html">Home</a> <span>/</span> <span>Register as a babysitter</span></div>
      <span class="eyebrow">Babysitter sign-up</span>
      <h1>Join Elite Traders Lounge as a verified babysitter.</h1>
      <p>Tell us about your experience so we can place you in the right rate band. Every applicant completes Smile ID identity verification before receiving bookings, and every booking pays at or above the National Minimum Wage (R30.23/hour, effective 1 March 2026) &mdash; never negotiated down.</p>
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
                <label for="nationality">Nationality</label>
                <input type="text" id="nationality" name="nationality" maxlength="60" />
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
          </div>

          <div class="form-section">
            <div class="form-section__title">Proof of address</div>
            <div class="form-section__hint">Have a document ready to send to our verification team &mdash; a utility bill, bank statement, lease agreement, or affidavit dated within the last 3 months, matching the home address above.</div>
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
            <div class="checkbox-field">
              <input type="checkbox" id="proof_of_address_confirmed" name="proof_of_address_confirmed" required />
              <label for="proof_of_address_confirmed">I confirm this document is dated within the last 3 months, matches the home address above, and I will provide a copy to Elite Traders Lounge on request.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Verify yourself (Smile ID)</div>
            <div class="form-section__hint">Elite Traders Lounge partners with Smile ID to confirm your identity against your ID/passport and run a facial-liveness check before you can accept bookings. Once verified, your profile displays a &ldquo;Verified identity&rdquo; badge that families can see.</div>
            <div class="checkbox-field">
              <input type="checkbox" id="smile_id_consent" name="smile_id_consent" required />
              <label for="smile_id_consent">I consent to Smile ID verifying my identity (document check + facial liveness) as part of registration.</label>
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
                  <span>0&ndash;1 year &middot; R35&ndash;R45/hr day</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="2" />
                  <strong>Level 2 &mdash; Standard</strong>
                  <span>1&ndash;3 years, references &middot; R45&ndash;R65/hr day</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="3" />
                  <strong>Level 3 &mdash; Advanced</strong>
                  <span>3+ yrs, First Aid/CPR &middot; R65&ndash;R85/hr day, R70&ndash;R80/hr overnight</span>
                </label>
                <label class="radio-card">
                  <input type="radio" name="experience_level" value="4" />
                  <strong>Level 4 &mdash; Specialist</strong>
                  <span>Overnight / special needs &middot; R90&ndash;R100/hr overnight</span>
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
      <p>Choose the level and rate you've agreed with your babysitter. Your quote is checked live against Appendix C's rate bands and the National Minimum Wage (R30.23/hour, effective 1 March 2026) &mdash; any rate below the compliant minimum is automatically corrected. Day bookings need a minimum of 4 hours; overnight bookings need a minimum of 10 hours.</p>
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
          </div>

          <div class="form-section">
            <div class="form-section__title">Proof of address</div>
            <div class="form-section__hint">Have a document ready to send to our verification team &mdash; a utility bill, bank statement, lease agreement, or affidavit dated within the last 3 months, matching the home address above.</div>
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
            <div class="checkbox-field">
              <input type="checkbox" id="proof_of_address_confirmed" name="proof_of_address_confirmed" required />
              <label for="proof_of_address_confirmed">I confirm this document is dated within the last 3 months, matches the home address above, and I will provide a copy to Elite Traders Lounge on request.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Verify yourself (Smile ID) &amp; Paystack account</div>
            <div class="form-section__hint">Elite Traders Lounge partners with Smile ID to confirm your identity before a babysitter is placed in your home. Payments run on Paystack Split Payment &mdash; Elite Traders Lounge never holds your funds in a wallet; Paystack pays the babysitter's share and Elite Traders Lounge's commission share directly, on the same transaction.</div>
            <div class="field">
              <label for="paystack_email">Paystack account email</label>
              <input type="email" id="paystack_email" name="paystack_email" required />
              <span class="field__hint">Don't have one yet? Create a free account at <a href="https://paystack.com" target="_blank" rel="noopener">paystack.com</a> before submitting.</span>
            </div>
            <div class="checkbox-field">
              <input type="checkbox" id="smile_id_consent" name="smile_id_consent" required />
              <label for="smile_id_consent">I consent to Smile ID verifying my identity (document check + facial liveness) as part of registration.</label>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section__title">Booking details</div>
            <div class="form-section__hint">Select day or overnight, then the babysitter's level, and confirm the hourly rate you've agreed.</div>

            <div class="field">
              <label>Booking type</label>
              <div class="action-toggle">
                <label><input type="radio" name="rate_type" value="day" checked /> Day booking <span class="field__hint">(min. 4 hours)</span></label>
                <label><input type="radio" name="rate_type" value="overnight" /> Overnight <span class="field__hint">(min. 10 hours)</span></label>
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
              <div class="field">
                <label for="hourly_rate">Agreed hourly rate (R)</label>
                <input type="number" id="hourly_rate" name="hourly_rate" required min="1" step="0.01" placeholder="e.g. 45" />
                <span class="field__hint" id="band-hint">Level 1 day band: R35&ndash;R45/hour</span>
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
              <textarea id="special_instructions" name="special_instructions" maxlength="1000" placeholder="Feeding, naps, medication, emergency contacts, house rules..."></textarea>
            </div>

            <div class="quote-box" id="quote-box" hidden>
              <div class="quote-box__row"><span>Applied hourly rate</span><strong id="q-rate">&ndash;</strong></div>
              <div class="quote-box__row"><span>Duration</span><strong id="q-duration">&ndash;</strong></div>
              <div class="quote-box__row"><span>Commission (<span id="q-comm-pct">&ndash;</span>)</span><strong id="q-comm">&ndash;</strong></div>
              <div class="quote-box__row total"><span>Total booking fee</span><strong id="q-fee">&ndash;</strong></div>
              <div class="quote-box__row"><span>Net to babysitter</span><strong id="q-net">&ndash;</strong></div>
              <p class="quote-box__note" id="q-note" hidden></p>
            </div>
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
          <li>Elite Traders Lounge uses experience-based rate bands (Level 1&ndash;4) as set out in <a href="#rate-bands">Appendix C: Rate Bands &amp; Minimum Wage Check</a>, and all bookings must fall within these ranges.</li>
          <li>The Babysitter's agreed hourly rate must be within the correct level band in Appendix C and never lower than the current National Minimum Wage &mdash; <strong>R30.23 per hour, effective 1 March 2026</strong> (Government Gazette No. 54075, published 3 February 2026, a 5.0% increase on the 2025 rate) &mdash; or the applicable rate at the time of service.</li>
          <li>If a rate is entered below the platform's minimum for that level or below the legal minimum wage, that rate is void, and the minimum compliant rate in Appendix C automatically applies.</li>
          <li>The Family and Babysitter must select the appropriate level (1&ndash;4) and agree on a rate within that band, at or above the legal minimum, as described in Appendix C, before booking confirmation.</li>
        </ul>
        <div class="policy-callout"><strong>2026/2027 rate note:</strong> The National Minimum Wage increased from R28.79/hour (2025) to R30.23/hour effective 1 March 2026. Elite Traders Lounge reviews and updates this figure whenever the Department of Employment and Labour publishes a new Government Gazette rate, and the platform's booking system automatically enforces the current rate at the time of service.</div>
      </div>

      <div class="policy-section" id="rate-bands">
        <h2>Appendix C &middot; Rate Bands &amp; Minimum Wage Check</h2>
        <p>Rates below any band floor, or below the National Minimum Wage, are void and automatically corrected to the compliant minimum shown below.</p>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Level</th><th>Experience</th><th>Booking type</th><th>Hourly rate band</th><th>Minimum booking</th><th>Commission</th></tr></thead>
            <tbody>
              <tr><td><span class="rate-badge">Level 1</span></td><td>Entry &middot; 0&ndash;1 year</td><td>Day</td><td><strong>R35 &ndash; R45</strong>/hr</td><td>4 hours</td><td>10%</td></tr>
              <tr><td><span class="rate-badge">Level 2</span></td><td>Standard &middot; 1&ndash;3 years, references</td><td>Day</td><td><strong>R45 &ndash; R65</strong>/hr</td><td>4 hours</td><td>12.5%</td></tr>
              <tr><td><span class="rate-badge">Level 3</span></td><td>Advanced &middot; 3+ years, First Aid/CPR</td><td>Day</td><td><strong>R65 &ndash; R85</strong>/hr</td><td>4 hours</td><td>12.5% &ndash; 15%</td></tr>
              <tr><td><span class="rate-badge">Level 3</span></td><td>Advanced &middot; night rate</td><td>Overnight</td><td><strong>R70 &ndash; R80</strong>/hr</td><td>10 hours</td><td>12.5%</td></tr>
              <tr><td><span class="rate-badge">Level 4</span></td><td>Specialist &middot; overnight / special needs</td><td>Overnight</td><td><strong>R90 &ndash; R100</strong>/hr</td><td>10 hours</td><td>12.5%</td></tr>
            </tbody>
          </table>
        </div>
        <p class="form-section__hint">Level 3 day commission scales from 12.5% at R65/hour up to 15% at R85/hour. All other bands charge a flat commission rate.</p>
      </div>

      <div class="policy-section" id="booking-hours">
        <h2>Minimum Booking Hours</h2>
        <ul>
          <li><strong>Day bookings:</strong> minimum 4 consecutive hours.</li>
          <li><strong>Overnight bookings:</strong> minimum 10 consecutive hours, billed at the applicable overnight rate for the babysitter's level.</li>
        </ul>
        <p>Bookings submitted below the applicable minimum are rejected by the booking system and must be resubmitted at or above the minimum duration.</p>
      </div>

      <div class="policy-section" id="commission">
        <h2>5.3 Commission Structure</h2>
        <p>Every booking is paid once, through Paystack Split Payment. Paystack automatically splits that single payment and pays the babysitter's net share directly into the babysitter's own Paystack account, while Elite Traders Lounge's commission share is paid directly into Elite Traders Lounge's Paystack account &mdash; on the same transaction, with no wallet held by Elite Traders Lounge at any point. Worked examples:</p>
        <div class="rate-table-wrap">
          <table class="rate-table">
            <thead><tr><th>Service component</th><th>Level</th><th>Babysitter fee</th><th>Elite Traders Lounge commission</th><th>Net to babysitter</th></tr></thead>
            <tbody>
              <tr><td>4-hour booking @ R45/hour</td><td>Level 1 &ndash; Entry</td><td><strong>R180</strong></td><td>R18 (10%)</td><td><strong>R162</strong></td></tr>
              <tr><td>4-hour booking @ R65/hour</td><td>Level 2 &ndash; Standard</td><td><strong>R260</strong></td><td>R32.50 (12.5%)</td><td><strong>R227.50</strong></td></tr>
              <tr><td>4-hour booking @ R85/hour</td><td>Level 3 &ndash; Advanced</td><td><strong>R340</strong></td><td>R51 (15%)</td><td><strong>R289</strong></td></tr>
              <tr><td>10-hour overnight @ R80/hour</td><td>Level 3 &ndash; Night</td><td><strong>R800</strong></td><td>R100 (12.5%)</td><td><strong>R700</strong></td></tr>
              <tr><td>12-hour overnight @ R100/hour</td><td>Level 4 &ndash; Specialist</td><td><strong>R1 200</strong></td><td>R150 (12.5%)</td><td><strong>R1 050</strong></td></tr>
            </tbody>
          </table>
        </div>
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
        <a href="#payments">5. Payments (Paystack)</a>
        <a href="#contracts">6. Individual contracts &amp; delivery</a>
        <a href="#conduct-terms">7. Platform role &amp; conduct</a>
        <a href="#suspension">8. Right to refuse or cancel service</a>
        <a href="#liability">9. Limitation of liability</a>
        <a href="#changes">10. Changes to these terms</a>
        <a href="#governing-law">11. Governing law</a>
        <a href="#contact-terms">12. Contact</a>
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

      <div class="policy-section" id="payments">
        <h2>5. Payments (Paystack)</h2>
        <ul>
          <li>All booking payments are processed through <strong>Paystack</strong> using Paystack's Split Payment functionality. A Family's payment for a booking is made once, and Paystack automatically splits and pays the Babysitter's net share directly to the Babysitter's own Paystack account and Elite Traders Lounge's commission share directly to Elite Traders Lounge's own Paystack account, on the same transaction.</li>
          <li>Both Babysitters and Families must hold their own active Paystack account and supply the email address linked to that account at registration, so Elite Traders Lounge can confirm the account exists before enabling payouts or bookings.</li>
          <li><strong>Elite Traders Lounge does not hold, custody, or accept responsibility for any wallet balance.</strong> Funds in transit are held and disbursed by Paystack as the payment processor, subject to Paystack's own terms of service; Elite Traders Lounge's role is limited to configuring the commission split and facilitating bookings.</li>
          <li>Commission rates (10%&ndash;15% depending on level and booking type, per Appendix C) are unchanged and are deducted automatically as part of the Paystack split &mdash; no additional platform or service fee is charged on top of this commission.</li>
          <li>Refunds for eligible cancellations (see <a href="./policies.html#refund-policy">Refund &amp; Cancellation Policy</a>) are issued via Paystack back to the Family's original payment method.</li>
        </ul>
      </div>

      <div class="policy-section" id="contracts">
        <h2>6. Individual Contracts &amp; Delivery</h2>
        <ul>
          <li>On successful registration, Elite Traders Lounge issues each Babysitter the current Babysitter Agreement and each Family the current Family Service Agreement by email to the address supplied, and makes a downloadable copy available from the confirmation screen.</li>
          <li>These individual contracts set out the specific rate band, commission, minimum-wage compliance, and cancellation terms that apply to that party, and incorporate these Terms &amp; Conditions and the <a href="./policies.html">Rates &amp; Policies</a> page by reference.</li>
          <li>It is each party's responsibility to read the emailed contract and raise any queries with Elite Traders Lounge before accepting or confirming a booking.</li>
        </ul>
      </div>

      <div class="policy-section" id="conduct-terms">
        <h2>7. Platform Role &amp; Conduct</h2>
        <ul>
          <li>Elite Traders Lounge operates as a booking and verification platform connecting independent Babysitters with Families. Babysitters engage as independent contractors and are not employees of Elite Traders Lounge.</li>
          <li>Both parties must use the <a href="./checkin.html">dual-party check-in tool</a> to confirm arrival and departure at every booking; timestamps recorded there are treated as the primary evidence of hours worked in any dispute.</li>
          <li>The full Code of Conduct, Dispute Resolution process, and Termination &amp; Suspension terms are set out on the <a href="./policies.html#conduct">Policies page</a> and form part of these Terms.</li>
        </ul>
      </div>

      <div class="policy-section" id="suspension">
        <h2>8. Right to Refuse or Cancel Service</h2>
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
        <h2>9. Limitation of Liability</h2>
        <ul>
          <li>Elite Traders Lounge verifies identity, proof of address, and references on a best-efforts basis but does not guarantee the conduct, performance, or suitability of any Babysitter or Family, and is not liable for any loss, injury, or damage arising from a booking arranged through the platform.</li>
          <li>Elite Traders Lounge is not a party to, and is not liable for, the processing, custody, or timing of payments handled by Paystack; any payment dispute involving Paystack is subject to Paystack's own terms and support channels.</li>
          <li>Nothing in these Terms excludes any liability that cannot lawfully be excluded under South African law.</li>
        </ul>
      </div>

      <div class="policy-section" id="changes">
        <h2>10. Changes to These Terms</h2>
        <p>Elite Traders Lounge may update these Terms &amp; Conditions, the Policies page, or Appendix C rate bands from time to time, including to reflect changes in the National Minimum Wage. Material changes will be posted on this page with an updated "last updated" date; continued use of the platform after changes take effect constitutes acceptance of the revised terms.</p>
      </div>

      <div class="policy-section" id="governing-law">
        <h2>11. Governing Law</h2>
        <p>These Terms are governed by the laws of the Republic of South Africa, including the Protection of Personal Information Act (POPIA), the Basic Conditions of Employment Act, and the Immigration Act 13 of 2002. The courts of South Africa have jurisdiction over any dispute not resolved through the process described on the <a href="./policies.html#disputes">Policies page</a>.</p>
      </div>

      <div class="policy-section" id="contact-terms">
        <h2>12. Contact</h2>
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
        </div>

        <div class="dash-tabpanel" data-tabpanel="sitters">
          <div class="alert alert--info" style="margin-bottom: var(--space-5);">
            <span>Tick each item once you've personally checked it (over email/WhatsApp/in person). There is no automatic document upload yet &mdash; this is a manual checklist, not automated verification.</span>
          </div>
          <div class="dash-card-list" id="sitters-list">
            <div class="dash-empty">Loading babysitters&hellip;</div>
          </div>
        </div>

        <div class="dash-tabpanel" data-tabpanel="bookings" hidden>
          <div class="dash-card-list" id="bookings-list">
            <div class="dash-empty">Loading bookings&hellip;</div>
          </div>
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

        <div class="mini-cal" id="sitter-calendar">
          <div class="mini-cal__head">
            <h3 id="mini-cal-title">This month</h3>
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


(ROOT / "register-sitter.html").write_text(
    page(
        "Register as a Babysitter — Elite Traders Lounge",
        "Sign up as a verified babysitter with Elite Traders Lounge. Select your experience level, get placed in the right Appendix C rate band, and get paid at or above the National Minimum Wage.",
        "register",
        REGISTER_BODY,
        extra_js="register.js",
    )
)

(ROOT / "book.html").write_text(
    page(
        "Book a Sitter — Elite Traders Lounge",
        "Register as a parent or guardian and book a verified babysitter. Live quote checked against Appendix C rate bands and the National Minimum Wage.",
        "book",
        BOOK_BODY,
        extra_js="book.js",
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
