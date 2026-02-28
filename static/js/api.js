/**
 * Frontend API client — points to the same-origin backend (Flask).
 * When the app is served from Flask, /api/* and /health are on the same host.
 */
(function (global) {
  var API_BASE = ""; // same origin when served by Flask

  function getToken() {
    try {
      return localStorage.getItem("linglong_token") || null;
    } catch (e) {
      return null;
    }
  }

  function setToken(token) {
    try {
      if (token) localStorage.setItem("linglong_token", token);
      else localStorage.removeItem("linglong_token");
    } catch (e) {}
  }

  function headers(includeAuth) {
    var h = { "Content-Type": "application/json" };
    if (includeAuth) {
      var t = getToken();
      if (t) h["Authorization"] = "Bearer " + t;
    }
    return h;
  }

  function request(method, path, body, auth) {
    var url = (API_BASE || "") + path;
    var opts = { method: method, headers: headers(!!auth) };
    if (body && (method === "POST" || method === "PATCH")) opts.body = JSON.stringify(body);
    return fetch(url, opts).then(function (res) {
      var next = res.json ? res.json() : res.text();
      return next.then(function (data) {
        if (!res.ok) {
          var err = new Error(data.error || data.message || "Request failed");
          err.status = res.status;
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  var api = {
    getToken: getToken,
    setToken: setToken,

    health: function () {
      return request("GET", "/health");
    },
    register: function (payload) {
      return request("POST", "/api/auth/register", payload, false).then(function (data) {
        if (data.token) setToken(data.token);
        return data;
      });
    },
    login: function (payload) {
      return request("POST", "/api/auth/login", payload, false).then(function (data) {
        if (data.token) setToken(data.token);
        return data;
      });
    },
    getMe: function () {
      return request("GET", "/api/auth/me", null, true);
    },
    getCategories: function () {
      return request("GET", "/api/categories", null, true);
    },
    getReels: function () {
      return request("GET", "/api/reels");
    },
    getReelBatches: function () {
      return request("GET", "/api/reels/batches");
    },
  };

  global.LinglongAPI = api;
})(typeof window !== "undefined" ? window : this);
