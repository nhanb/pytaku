import { Auth } from "../models.js";

function Follows(initialVNode) {
  let titles = [];
  return {
    oninit: () => {
      Auth.request({
        method: "GET",
        url: "/api/follows",
      });
    },
    oncreate: (vnode) => {
      document.title = "Stuff I follow - Pytaku";
    },
    view: (vnode) => {
      return m("div.content", [
        titles.map((title) =>
          m("div.title", [
            m("div", [
              m("a", { href: "TODO" }, [
                m("img.cover", { src: title.thumbnail, alt: title.name }),
              ]),
            ]),
          ])
        ),
      ]);
    },
  };
}

export default Follows;
