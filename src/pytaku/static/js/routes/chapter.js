import { Auth } from "../models.js";
import { LoadingMessage, fullChapterName, Button } from "../utils.js";

function Chapter(initialVNode) {
  let isLoading = false;
  let chapter = {};

  return {
    oninit: (vnode) => {
      document.title = "Manga chapter";

      isLoading = true;
      m.redraw();

      Auth.request({
        method: "GET",
        url: "/api/chapter/:site/:titleId/:chapterId",
        params: {
          site: vnode.attrs.site,
          titleId: vnode.attrs.titleId,
          chapterId: vnode.attrs.chapterId,
        },
      })
        .then((resp) => {
          chapter = resp;
          document.title = fullChapterName(chapter);
        })
        .finally(() => {
          isLoading = false;
        });
    },
    view: (vnode) => {
      if (isLoading) {
        return m("div.chapter.content", m(LoadingMessage));
      }

      const { site, titleId } = vnode.attrs;
      const prev = chapter.prev_chapter;
      const next = chapter.next_chapter;
      const buttons = m("div.chapter--buttons", [
        prev
          ? m(
              m.route.Link,
              {
                class: "touch-friendly",
                href: `/m/${site}/${titleId}/${prev.id}`,
              },
              [m("i.icon.icon-chevrons-left"), m("span", "prev")]
            )
          : m(Button, {
              text: "prev",
              icon: "chevrons-left",
              disabled: true,
            }),
        m(
          m.route.Link,
          {
            class: "touch-friendly",
            href: `/m/${site}/${titleId}`,
          },
          [m("i.icon.icon-list"), m("span", " chapter list")]
        ),
        next
          ? m(
              m.route.Link,
              {
                class: "touch-friendly",
                href: `/m/${site}/${titleId}/${next.id}`,
              },
              [m("span", "next"), m("i.icon.icon-chevrons-right")]
            )
          : m(Button, {
              text: "next",
              icon: "chevrons-right",
              disabled: true,
            }),
      ]);
      return m("div.chapter.content", [
        m("h1", fullChapterName(chapter)),
        buttons,
        m(
          "div",
          {
            class:
              "chapter--pages" + chapter.is_webtoon ? " chapter--webtoon" : "",
          },
          [chapter.pages.map((page) => m("img", { src: page }))]
        ),
        buttons,
      ]);
    },
  };
}

export default Chapter;
