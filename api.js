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

  async function getAuth(path, headers) {
    var res = await fetch(API + path, { headers: headers || {} });
    var data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) {
      var msg = (data && data.detail) || ('Request failed (' + res.status + ')');
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return data;
  }

  async function postAuth(path, body, headers) {
    var res = await fetch(API + path, {
      method: 'POST',
      headers: Object.assign({ 'Content-Type': 'application/json' }, headers || {}),
      body: JSON.stringify(body),
    });
    var data = null;
    try { data = await res.json(); } catch (e) { /* no body */ }
    if (!res.ok) {
      var msg = (data && (data.detail || data.message)) || ('Request failed (' + res.status + ')');
      if (Array.isArray(data && data.detail)) {
        msg = data.detail.map(function (d) { return d.msg || JSON.stringify(d); }).join(' ');
      }
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return data;
  }

  async function getBlobAuth(path, headers) {
    var res = await fetch(API + path, { headers: headers || {} });
    if (!res.ok) {
      var msg = 'Request failed (' + res.status + ')';
      try {
        var data = await res.json();
        msg = (data && data.detail) || msg;
      } catch (e) { /* no json body */ }
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return await res.blob();
  }

  return { post: post, get: get, getAuth: getAuth, postAuth: postAuth, getBlobAuth: getBlobAuth, base: API };
})();
