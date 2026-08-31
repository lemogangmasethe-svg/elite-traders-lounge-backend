/* Shared API helper for Elite Traders Lounge forms and check-in tool.
   Base URL resolution:
   - Perplexity preview (deploy_website): the __PORT_8000__ placeholder is rewritten
     to a live proxy URL pointing at the sandbox backend.
   - Local dev (served from localhost/127.0.0.1): talk to the local backend directly.
   - Any other host (e.g. Vercel production): use the hosted Render backend. */
window.ETL_API = (function () {
  var PLACEHOLDER = '__PORT_8000__';
  var PRODUCTION_API = 'https://elite-traders-lounge-api.onrender.com';
  var API;
  if (!PLACEHOLDER.startsWith('__')) {
    API = PLACEHOLDER;
  } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    API = 'http://localhost:8000';
  } else {
    API = PRODUCTION_API;
  }

  async function post(path, body) {
    var res = await fetch(API + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    var data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) {
      var msg = (data && (data.detail || data.message)) || ('Request failed (' + res.status + ')');
      if (Array.isArray(data && data.detail)) {
        msg = data.detail.map(function (d) { return d.msg || JSON.stringify(d); }).join(' ');
      }
      throw new Error(msg);
    }
    return data;
  }

  async function get(path) {
    var res = await fetch(API + path);
    var data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) {
      var msg = (data && data.detail) || ('Request failed (' + res.status + ')');
      throw new Error(msg);
    }
    return data;
  }

  return { post: post, get: get, base: API };
})();
