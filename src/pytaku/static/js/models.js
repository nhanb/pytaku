function readCookie(cookieString) {
  // This is terrible and wrong but it's enough for what we need i.e. just get
  // the damn token.
  const result = {};
  cookieString.split(";").forEach((pair) => {
    const [key, val] = pair.split("=");
    result[key] = val;
  });
  return result;
}

const Auth = {
  username: sessionStorage.getItem("username"),
  userId: sessionStorage.getItem("userId"),
  token: readCookie(document.cookie).token || null,
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
    sessionStorage.setItem("userId", userId);
    sessionStorage.setItem("username", username);
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
    sessionStorage.clear();
  },

  request: (options) => {
    return m.request(options).catch((err) => {
      if (err.code == 401) {
        Auth.clearCredentials();
      } else if (err.code == 500) {
        alert(err.response.message);
      }
      throw err;
    });
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

const ChapterModel = {
  cache: {},

  cacheGet: (site, titleId, chapterId) => {
    const key = [site, titleId, chapterId].join(",");
    return ChapterModel.cache[key] || null;
  },
  cacheSet: (site, titleId, chapterId, value) => {
    const key = [site, titleId, chapterId].join(",");
    ChapterModel.cache[key] = value;
  },

  get: ({ site, titleId, chapterId }) => {
    // Returns a promise.
    // Tries to return cached data first, if that fails then send http request
    // and save cache on success.

    const cached = ChapterModel.cacheGet(site, titleId, chapterId);
    if (cached) {
      return Promise.resolve(cached);
    }

    return Auth.request({
      method: "GET",
      url: "/api/chapter/:site/:titleId/:chapterId",
      params: { site, titleId, chapterId },
    }).then((chapter) => {
      ChapterModel.cacheSet(site, titleId, chapterId, chapter);
      return chapter;
    });
  },
};

export { Auth, SearchModel, ChapterModel };
