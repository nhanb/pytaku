import { Auth } from "../models.js";
import { Button } from "../utils.js";

function Authentication(initialVNode) {
  let loginUsername;
  let loginPassword;
  let rememberMe = false;
  let loginErrorMessage;
  let registerUsername;
  let registerPassword;
  let confirmPassword;
  let registerMessage;
  let registerSuccess;

  let registering = false;
  let loggingIn = false;

  return {
    oncreate: (vnode) => {
      document.title = "Authentication - Pytaku";
    },
    view: (vnode) => {
      return m("div.content.auth", [
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
                  let userId = result.user_id;
                  let token = result.token;
                  let username = loginUsername;
                  Auth.saveLoginResults({
                    userId,
                    username,
                    token,
                    remember: rememberMe,
                  });
                  m.route.set("/f");
                })
                .catch((e) => {
                  loginErrorMessage = e.response.message;
                })
                .finally(() => {
                  loggingIn = false;
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
            m(Button, {
              type: "submit",
              disabled: loggingIn ? "disabled" : null,
              text: loggingIn ? " Logging in..." : " Log in",
              icon: "log-in",
              color: "blue",
            }),
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
                  registerSuccess = true;
                  registerMessage = result.message;
                  loginUsername = registerUsername;
                  loginPassword = registerPassword;
                })
                .catch((e) => {
                  registerMessage = e.response.message;
                  registerSuccess = false;
                })
                .finally(() => {
                  registering = false;
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
            m(Button, {
              type: "submit",
              disabled: registering ? "disabled" : null,
              text: registering ? " Registering..." : " Register",
              icon: "user-plus",
              color: "green",
            }),
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
      ]);
    },
  };
}

export default Authentication;
