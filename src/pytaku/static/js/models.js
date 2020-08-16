const Auth = {
  username: sessionStorage.getItem("username"),
  token: localStorage.getItem("token"),
  userId: localStorage.getItem("user_id"),
  isLoggedIn: () => Auth.username !== null,
  init: () => {
    // Already logged in, probably from another tab:
    if (Auth.username !== null) {
      return;
    }

    // No previous login session:
    if (Auth.token === null || Auth.userId === null) {
      return;
    }

    // Verify token & user_id saved from previous login session:
    return m
      .request({
        method: "POST",
        url: "/api/verify-token",
        body: { token: Auth.token, user_id: Auth.userId },
      })
      .then((result) => {
        // Success! Set username for this session now
        sessionStorage.setItem("username", result.username);
        Auth.username = result.username;
      })
      .catch((err) => {
        // If server responded with 401 Unauthorized, clear any local trace of
        // these invalid credentials.
        if (err.code == 401) {
          Auth.clearCredentials();
        }
      });
  },

  saveLoginResults: ({ userId, username, token }) => {
    sessionStorage.setItem("username", username);
    localStorage.setItem("user_id", userId);
    localStorage.setItem("token", token);
    Auth.userId = userId;
    Auth.username = username;
    Auth.token = token;
  },

  logout: () => {
    return m
      .request({
        method: "POST",
        url: "/api/logout",
        body: { token: Auth.token, user_id: Auth.userId },
      })
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
};

export { Auth };
