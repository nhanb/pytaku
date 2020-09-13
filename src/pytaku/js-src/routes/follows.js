import { Auth } from "../models.js";
import { LoadingMessage, fullChapterName, Chapter } from "../utils.js";

const Title = {
  view: (vnode) => {
    const title = vnode.attrs.title;
    const numChaptersToDisplay = 3;

    return m(
      "div.follows--title" +
        (title.chapters.length === 0 ? ".empty" : ".non-empty"),
      [
        m("div", [
          m(
            m.route.Link,
            {
              href: `/m/${title.site}/${title.id}`,
              title: `${title.name} - ${title.site}`,
            },
            [m("img.follows--cover", { src: title.thumbnail, alt: title.name })]
          ),
        ]),
        m("div.follows--chapters", [
          title.chapters.length > numChaptersToDisplay
            ? m(
                m.route.Link,
                {
                  href: `/m/${title.site}/${title.id}`,
                  class: "follows--chapter follows--more",
                },
                `and ${title.chapters.length - numChaptersToDisplay} more...`
              )
            : "",
          title.chapters
            .slice(-numChaptersToDisplay)
            .map((chapter) =>
              m(Chapter, { site: title.site, titleId: title.id, chapter })
            ),
        ]),
      ]
    );
  },
};

function Follows(initialVNode) {
  let titles = [];
  let isLoading = false;

  return {
    oninit: () => {
      isLoading = true;
      Auth.request({
        method: "GET",
        url: "/api/follows",
      })
        .then((resp) => {
          titles = resp.titles;
        })
        .catch((err) => {
          console.log(err);
        })
        .finally(() => {
          isLoading = false;
        });
    },

    oncreate: (vnode) => {
      document.title = "Stuff I follow - Pytaku";
    },

    view: (vnode) => {
      let content = "";

      if (isLoading) {
        return m("div.content", m(LoadingMessage));
      }

      if (titles.length === 0) {
        return m("div.content", [
          m("p", "You're not following any title yet. Try searching for some."),
          m("p", [
            "Migrating from Tachiyomi? ",
            m(m.route.Link, { href: "/i" }, "Use the importer"),
            "!",
          ]),
        ]);
      }

      return m("div.follows.content", [
        titles.map((title) => m(Title, { title })),
      ]);
    },
  };
}

export default Follows;
