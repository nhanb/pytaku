import { Auth } from "../models.js";

const truncate = (input) =>
  input.length > 20 ? `${input.substring(0, 20)}...` : input;

function fullChapterName(chapter) {
  let result = "Chapter " + chapter.num_major;
  if (chapter.num_minor) {
    result += "." + chapter.num_minor;
  }
  if (chapter.volume) {
    result += " Volume " + chapter.volume;
  }
  if (chapter.name) {
    result += " - " + chapter.name;
  }
  return result;
}

const Title = {
  view: (vnode) => {
    const title = vnode.attrs.title;
    const numChaptersToDisplay = 4;

    return m(
      "div.follows--title" + (title.chapters.length === 0 ? ".empty" : ""),
      [
        m("div", [
          m(m.route.Link, { href: `/m/${title.site}/${title.id}` }, [
            m("img.follows--cover", { src: title.thumbnail, alt: title.name }),
          ]),
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
          title.chapters.slice(-numChaptersToDisplay).map((chapter) =>
            m(
              m.route.Link,
              {
                href: `/m/${title.site}/${title.id}/${chapter.id}`,
                class: "follows--chapter",
              },
              [
                fullChapterName(chapter),
                chapter.groups.map((group) => {
                  m("span.follows--group", truncate(group));
                }),
              ]
            )
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
          alert("TODO");
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
        return m(
          "div.content",
          m("h2.blink", [m("i.icon.icon-loader.spin"), " loading..."])
        );
      }

      if (titles.length === 0) {
        return m(
          "div.content",
          "You're not following any title yet. Try searching for some."
        );
      }

      return m("div.content", [titles.map((title) => m(Title, { title }))]);
    },
  };
}

export default Follows;
