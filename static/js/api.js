const API = (() => {
  const BASE = '';

  function getToken() {
    return localStorage.getItem('access_token');
  }

  function authHeaders() {
    return { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' };
  }

  async function request(method, path, body = null, isForm = false) {
    const opts = { method, headers: isForm ? { 'Authorization': `Bearer ${getToken()}` } : authHeaders() };
    if (body) opts.body = isForm ? body : JSON.stringify(body);
    const res = await fetch(BASE + path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || res.statusText);
    }
    return res.json();
  }

  return {
    login: (email, password) =>
      request('POST', '/auth/login', { email, password }),

    logout: () =>
      request('POST', '/auth/logout'),

    updateLang: (lang) =>
      request('PATCH', '/auth/profile', { preferred_language: lang }),

    deleteAllData: () =>
      request('DELETE', '/auth/data'),

    uploadDocument: (file) => {
      const form = new FormData();
      form.append('file', file);
      return request('POST', '/documents/upload', form, true);
    },

    getDocument: (id) =>
      request('GET', `/documents/${id}`),

    getDocumentText: (id) =>
      request('GET', `/documents/${id}/text`),

    listDocuments: () =>
      request('GET', '/documents/'),

    getPassport: (docId) =>
      request('GET', `/passport/${docId}`),

    getRisk: (docId) =>
      request('GET', `/passport/${docId}/risk`),

    confirmPassport: (docId, confirmed, editedFields = null) =>
      request('POST', '/passport/confirm', { document_id: docId, confirmed, edited_fields: editedFields }),

    validateEdit: (docId, editedFields) =>
      request('POST', `/passport/${docId}/validate-edit`, { edited_fields: editedFields }),

    getMergedPassport: () =>
      request('GET', '/passport/merged'),

    navigatorAsk: (question) =>
      request('POST', '/navigator/ask', { question }),

    navigatorHelp: (message) =>
      request('POST', '/navigator/help', { message }),
  };
})();
