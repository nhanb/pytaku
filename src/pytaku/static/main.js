/* Top-level Components */

let Home = {
  view: (vnode) => {
    return m("div", { class: "main" }, [
      m(Navbar),
      m("div.content", [
        m("p", "Try searching for some manga title using the box above."),
        m("p", "Logging in allows you to follow manga titles."),
      ]),
    ]);
  },
};

let Following = {
  view: (vnode) => {
    return "Follows";
  },
};

let Navbar = {
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
      m(m.route.Link, { class: "nav--link", href: "/l" }, [
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
  "/f": Following,
});
