/* Shared API helper for Elite Traders Lounge forms and check-in tool. */
window.ETL_API = (function () {
  var API = '__PORT_8000__'.startsWith('__') ? 'http://localhost:8000' : '__PORT_8000__';

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
