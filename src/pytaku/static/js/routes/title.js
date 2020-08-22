import { Auth } from "../models.js";
import { LoadingMessage, Button, fullChapterName, Chapter } from "../utils.js";

function Title(initialVNode) {
  let isLoading = false;
  let title = {};

  return {
    oninit: (vnode) => {
      document.title = "Manga";
      isLoading = true;
      m.redraw();

      Auth.request({
        method: "GET",
        url: "/api/title/:site/:titleId",
        params: {
          site: vnode.attrs.site,
          titleId: vnode.attrs.titleId,
        },
      })
        .then((resp) => {
          title = resp;
          document.title = title.name;
        })
        .finally(() => {
          isLoading = false;
        });
    },
    view: (vnode) => {
      return m(
        "div.content",
        isLoading
          ? m(LoadingMessage)
          : [
              m("h1", title.name),
              m("div.title--details", [
                Auth.isLoggedIn()
                  ? m(Button, {
                      text: "Follow",
                      icon: "bookmark",
                      color: "green",
                    })
                  : null,
                " ",
                m(
                  "a.touch-friendly[title=Go to source site][target=_blank]",
                  { href: title.source_url },
                  [title.site, m("i.icon.icon-arrow-up-right")]
                ),
              ]),
              m("img.title--cover[alt=cover]", { src: title.cover }),
              title.descriptions.map((desc) => m("p", desc)),
              title.chapters
                ? title.chapters.map((chapter) =>
                    m(Chapter, { site: title.site, titleId: title.id, chapter })
                  )
                : m("p", "This one has no chapters."),
            ]
      );
    },
  };
}

export default Title;
