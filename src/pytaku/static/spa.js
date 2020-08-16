/* Top-level Components */

const Home = {
  view: (vnode) => {
    return m("div.main", [
      m(Navbar),
      m("div.content", [
        m("p", "Try searching for some manga title using the box above."),
        m("p", "Logging in allows you to follow manga titles."),
      ]),
    ]);
  },
};

function Authentication(initialVNode) {
  let loginUsername = "admin";
  let loginPassword = "admin";
  let rememberMe = false;
  let loginErrorMessage = "";

  let registerUsername = "admin";
  let registerPassword = "admin";
  let confirmPassword = "admin";
  let registerMessage = "";
  let registerSuccess = false;

  let registering = false;
  let loggingIn = false;

  return {
    view: (vnode) => {
      return m("div.main", [
        m(Navbar),
        m("div.content.auth", [
          m(
            "form.auth--form",
            {
              onsubmit: (e) => {
                e.preventDefault();
                loginErrorMessage = "";
                loggingIn = true;
                m.redraw();

                m.request({
                  method: "POST",
                  url: "/api/login",
                  body: {
                    username: loginUsername,
                    password: loginPassword,
                    remember: rememberMe,
                  },
                })
                  .then((result) => {
                    loggingIn = false;
                    console.log("Success:", result);
                    alert("TODO");
                  })
                  .catch((e) => {
                    loggingIn = false;
                    loginErrorMessage = e.response.message;
                  });
              },
            },
            [
              m("h1", "Login"),
              m("input[placeholder=username][name=username][required]", {
                value: loginUsername,
                oninput: (e) => {
                  loginUsername = e.target.value;
                },
              }),
              m(
                "input[placeholder=password][name=password][type=password][required]",
                {
                  value: loginPassword,
                  oninput: (e) => {
                    loginPassword = e.target.value;
                  },
                }
              ),
              m("label[for=auth--remember].auth--checkbox-label", [
                m("input[type=checkbox][name=remember][id=auth--remember]", {
                  checked: rememberMe,
                  onchange: (e) => {
                    rememberMe = e.target.checked;
                  },
                }),
                " Remember me",
              ]),
              m(
                "button[type=submit]",
                {
                  disabled: loggingIn ? "disabled" : null,
                },
                [
                  m("i.icon.icon-log-in"),
                  loggingIn ? " Logging in..." : " Log in",
                ]
              ),
              m("p.auth--form--error-message", loginErrorMessage),
            ]
          ),
          m(
            "form.auth--form",
            {
              onsubmit: (e) => {
                e.preventDefault();
                registerMessage = "";
                m.redraw();

                if (registerPassword !== confirmPassword) {
                  registerMessage = "Password confirmation didn't match!";
                  registerSuccess = false;
                  return;
                }

                registering = true;
                m.redraw();
                m.request({
                  method: "POST",
                  url: "/api/register",
                  body: {
                    username: registerUsername,
                    password: registerPassword,
                  },
                })
                  .then((result) => {
                    registering = false;
                    registerSuccess = true;
                    registerMessage = result.message;
                    loginUsername = registerUsername;
                    loginPassword = registerPassword;
                  })
                  .catch((e) => {
                    registering = false;
                    registerMessage = e.response.message;
                    registerSuccess = false;
                  });
              },
            },
            [
              m("h1", "Register"),
              m("input[placeholder=username][name=username][required]", {
                value: registerUsername,
                oninput: (e) => {
                  registerUsername = e.target.value;
                },
              }),
              m(
                "input[placeholder=password][name=password][type=password][required]",
                {
                  value: registerPassword,
                  oninput: (e) => {
                    registerPassword = e.target.value;
                  },
                }
              ),
              m(
                "input[placeholder=confirm password][name=confirm][type=password][required]",
                {
                  value: confirmPassword,
                  oninput: (e) => {
                    confirmPassword = e.target.value;
                  },
                }
              ),
              m(
                "button[type=submit]",
                {
                  disabled: registering ? "disabled" : null,
                },
                [
                  m("i.icon.icon-user-plus"),
                  registering ? " Registering..." : " Register",
                ]
              ),
              m(
                "p",
                {
                  class:
                    "auth--form--message-" +
                    (registerSuccess ? "success" : "error"),
                },
                registerMessage
              ),
            ]
          ),
        ]),
      ]);
    },
  };
}

const Navbar = {
  view: (vnode) => {
    return m("nav", [
      m(m.route.Link, { class: "nav--logo", href: "/" }, [
        m("img.nav--logo--img", {
          src: "/static/pytaku.svg",
          alt: "home",
        }),
      ]),
      m("form.nav--search-form", [
        m("input", { placeholder: "search title name" }),
        m("button", { type: "submit" }, [m("i.icon.icon-search")]),
      ]),
      m(m.route.Link, { class: "nav--link", href: "/a" }, [
        m("i.icon.icon-log-in"),
        "login / register",
      ]),
    ]);
  },
};

/* Entry point */

root = document.getElementById("spa-root");
m.route.prefix = "";
m.route(root, "/h", {
  "/h": Home,
  "/a": Authentication,
});
