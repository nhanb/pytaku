import { Auth } from "./models.js";

function Navbar(initialVNode) {
  let isLoggingOut = false;
  return {
    view: (vnode) => {
      let userLink;
      if (Auth.isLoggedIn()) {
        userLink = m("span.nav--greeting", [
          "Welcome, ",
          m("b", Auth.username),
          " ",
          m(
            "button",
            {
              onclick: (ev) => {
                isLoggingOut = true;
                m.redraw();
                Auth.logout();
              },
              disabled: isLoggingOut ? "disabled" : null,
            },
            [
              m("i.icon.icon-log-out"),
              isLoggingOut ? " logging out" : " logout",
            ]
          ),
        ]);
      } else {
        userLink = m(m.route.Link, { class: "nav--link", href: "/a" }, [
          m("i.icon.icon-log-in"),
          "login / register",
        ]);
      }

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
        userLink,
      ]);
    },
  };
}
export { Navbar };
