const Auth = {
  username: sessionStorage.getItem("username"),
  userId: sessionStorage.getItem("userId"),
  token: localStorage.getItem("token"),
  isLoggedIn: () => Auth.username !== null && Auth.userId !== null,
  init: () => {
    // Already logged in, probably from another tab:
    if (Auth.isLoggedIn()) {
      console.log("Already logged in");
      return Promise.resolve();
    }

    // No previous login session:
    if (Auth.token === null) {
      console.log("No saved token found");
      return Promise.resolve();
    }

    // Verify token saved from previous login session:
    return m
      .request({
        method: "GET",
        url: "/api/verify-token",
        headers: { Authorization: `Bearer ${Auth.token}` },
      })
      .then((result) => {
        // Success! Set user info for this session now
        sessionStorage.setItem("username", result.username);
        sessionStorage.setItem("userId", result.user_id);
        Auth.username = result.username;
        Auth.userId = result.user_id;
      })
      .catch((err) => {
        // If server responded with 401 Unauthorized, clear any local trace of
        // these invalid credentials.
        if (err.code == 401) {
          Auth.clearCredentials();
        }
      })
      .finally(m.redraw);
  },

  saveLoginResults: ({ userId, username, token, remember }) => {
    // FIXME: currently, even when remember=false we're still storing the token
    // in localStorage, simply because sessionStorage isn't shared across tabs.
    // Unfortunately this means when user logs in without checking "remember
    // me", the token will still linger in localstorage after browser is
    // closed, and if an adversary reopens browser within the token's
    // server-enforced lifespan (1 day), then user is pwned.
    //
    // Either that or we stick to sessionStorage and forget multitab support.
    // _OR_ we do a convoluted song and dance with storage events:
    // > https://stackoverflow.com/a/32766809
    //
    // 0 days since web APIs last made me sad.
    sessionStorage.setItem("userId", userId);
    sessionStorage.setItem("username", username);
    localStorage.setItem("token", token);
    Auth.userId = userId;
    Auth.username = username;
    Auth.token = token;
  },

  logout: () => {
    return Auth.request({ method: "POST", url: "/api/logout" })
      .then(Auth.clearCredentials)
      .catch((err) => {
        if (err.code == 401) {
          Auth.clearCredentials();
        } else {
          console.log(err);
        }
      });
  },

  clearCredentials: () => {
    Auth.username = null;
    Auth.token = null;
    Auth.userId = null;
    localStorage.clear();
    sessionStorage.clear();
  },

  request: (options) => {
    if (Auth.isLoggedIn()) {
      options.headers = { Authorization: `Bearer ${Auth.token}` };
    }
    return m.request(options);
  },
};

const SearchModel = {
  query: "",
  result: {},
  cache: {},
  isLoading: true,
  performSearch: (query) => {
    SearchModel.query = query;
    if (SearchModel.cache[query]) {
      SearchModel.result = SearchModel.cache[query];
    } else {
      SearchModel.isLoading = true;
      m.redraw();
      m.request({
        method: "GET",
        url: "/api/search/:query",
        params: { query },
      })
        .then((resp) => {
          SearchModel.cache[query] = resp;
          SearchModel.result = resp;
        })
        .catch((err) => {
          console.log("TODO", err);
        })
        .finally(() => {
          SearchModel.isLoading = false;
        });
    }
  },
};

export { Auth, SearchModel };
