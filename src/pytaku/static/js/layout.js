import { Auth, SearchModel } from "./models.js";
import { Button } from "./utils.js";

function Navbar(initialVNode) {
  let isLoggingOut = false;

  return {
    view: (vnode) => {
      let userLink;
      if (Auth.isLoggedIn()) {
        userLink = m("span.nav--greeting", [
          m("span", ["Welcome, ", m("b", Auth.username)]),
          m(Button, {
            text: isLoggingOut ? " logging out" : " logout",
            icon: "log-out",
            color: "red",
            title: "Log out",
            onclick: (ev) => {
              isLoggingOut = true;
              m.redraw();
              Auth.logout()
                .then(() => {
                  m.route.set("/");
                })
                .finally(() => {
                  isLoggingOut = false;
                });
            },
            disabled: isLoggingOut ? "disabled" : null,
          }),
        ]);
      } else {
        userLink = m(m.route.Link, { class: "nav--link", href: "/a" }, [
          m("i.icon.icon-log-in"),
          "login / register",
        ]);
      }

      return m("nav", [
        m(
          m.route.Link,
          { class: "nav--logo", href: Auth.isLoggedIn() ? "/f" : "/" },
          [
            m("img.nav--logo--favicon", {
              src: "/static/favicon.svg",
              alt: "home",
            }),
            m("img.nav--logo--img", {
              src: "/static/pytaku.svg",
              alt: "home",
            }),
          ]
        ),
        m(
          "form.nav--search-form",
          {
            onsubmit: (ev) => {
              ev.preventDefault();
              m.route.set("/s/:query", { query: SearchModel.query });
            },
          },
          [
            m("input[placeholder=search manga title]", {
              onchange: (ev) => {
                SearchModel.query = ev.target.value;
              },
              value: SearchModel.query,
            }),
            m(Button, { color: "red", icon: "search", type: "submit" }),
          ]
        ),
        userLink,
      ]);
    },
  };
}

const Layout = {
  view: (vnode) => {
    return [m(Navbar), vnode.children];
  },
};

export default Layout;
