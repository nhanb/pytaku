import { Auth, ChapterModel } from "../models.js";
import { LoadingMessage, fullChapterName, Button } from "../utils.js";

const KEYCODE_PLUS = 43;
const KEYCODE_MINUS = 45;
const KEYCODE_ZERO = 48;
const KEYCODE_QUESTION_MARK = 63;
const KEYCODE_J = 106;
const KEYCODE_K = 107;
const KEYCODE_H = 104;
const KEYCODE_L = 108;

const LoadingPlaceholder = {
  view: () => m("h2", [m("i.icon.icon-loader.spin")]),
};

const PendingPlaceholder = {
  view: () => m("h2", [m("i.icon.icon-loader")]),
};

const RetryImgButton = {
  view: (vnode) => {
    return m(Button, {
      text: "Errored. Try again?",
      color: "red",
      onclick: (ev) => {
        const { page } = vnode.attrs;
        page.status = ImgStatus.LOADING;
        // Cheat: append to src so the element's key is
        // different, forcing mithril to redraw.
        // Chose `?` here because it will just be stripped by
        // flask's path parser.
        page.src = page.src.endsWith("?")
          ? page.src.slice(0, -1)
          : page.src + "?";
      },
    });
  },
};

const ImgStatus = {
  LOADING: "loading",
  SUCCEEDED: "succeeded",
  FAILED: "failed",
};

function FallbackableImg(initialVNode) {
  let currentSrc;
  return {
    oninit: (vnode) => {
      currentSrc = vnode.attrs.src;
    },
    view: (vnode) => {
      return m("img", {
        src: currentSrc,
        style: vnode.attrs.style,
        onload: vnode.attrs.onload,
        onerror: (ev) => {
          if (currentSrc === vnode.attrs.src && vnode.attrs.altsrc !== null) {
            currentSrc = vnode.attrs.altsrc;
          } else {
            vnode.attrs.onerror(ev);
          }
        },
      });
    },
  };
}

function Chapter(initialVNode) {
  let isLoading = false;
  let isMarkingLastChapterAsRead = false;
  let chapter = {};
  let loadedPages = [];
  let pendingPages = [];

  let site, titleId; // these are written on init
  let nextChapterPromise = null;
  let nextChapterPendingPages = null;
  let nextChapterLoadedPages = [];

  let pageMaxWidth = 100; // in percent

  function onKeyPress(event) {
    if (event.target.tagName === "INPUT") return;

    switch (event.keyCode) {
      case KEYCODE_PLUS:
        if (pageMaxWidth <= 85) pageMaxWidth += 15;
        break;
      case KEYCODE_MINUS:
        if (pageMaxWidth > 15) pageMaxWidth -= 15;
        break;
      case KEYCODE_ZERO:
        pageMaxWidth = 100;
        break;
      case KEYCODE_QUESTION_MARK:
        window.alert(`Keyboard shortcuts:
    - to decrease page size
    + to increase page size (max 100%)
    0 (zero) to reset page size
    j to scroll down
    k to scroll up
    h to go to previous chapter
    l to go to next chapter`);
        break;
      case KEYCODE_J:
        window.scrollBy({ top: 350, behavior: "smooth" });
        break;
      case KEYCODE_K:
        window.scrollBy({ top: -350, behavior: "smooth" });
        break;
      case KEYCODE_H:
        document.querySelector(".chapter--prev-button").click();
        break;
      case KEYCODE_L:
        document.querySelector(".chapter--next-button").click();
        break;
      /*
      default:
        console.log("Keycode:", event.keyCode);
      */
    }
    m.redraw();
  }

  function loadNextPage() {
    if (pendingPages.length > 0) {
      let [src, altsrc] = pendingPages.splice(0, 1)[0];
      loadedPages.push({
        status: ImgStatus.LOADING,
        src,
        altsrc,
      });
    } else if (chapter.next_chapter && nextChapterPromise === null) {
      /* Once all pages of this chapter have been loaded,
       * preload the next chapter
       */
      nextChapterPromise = ChapterModel.get({
        site,
        titleId,
        chapterId: chapter.next_chapter.id,
      }).then((nextChapter) => {
        console.log("Preloading next chapter:", fullChapterName(nextChapter));
        if (nextChapter.pages_alt.length > 0) {
          nextChapterPendingPages = nextChapter.pages.map((page, i) => {
            return [page, nextChapter.pages_alt[i]];
          });
        } else {
          nextChapterPendingPages = nextChapter.pages.map((page) => {
            return [page, null];
          });
        }
        // Apparently preloading one at a time was too slow so let's go with 2.
        preloadNextChapterPage();
        preloadNextChapterPage();
      });
    }
  }

  function preloadNextChapterPage() {
    if (nextChapterPendingPages !== null) {
      if (nextChapterPendingPages.length > 0) {
        const [src, altsrc] = nextChapterPendingPages.splice(0, 1)[0];
        nextChapterLoadedPages.push({ src, altsrc });
      }
    }
  }

  function markChapterAsRead(site, titleId, chapterId) {
    return Auth.request({
      method: "POST",
      url: "/api/read",
      body: {
        read: [
          {
            site,
            title_id: titleId,
            chapter_id: chapterId,
          },
        ],
      },
    });
  }

  function buttonsView(site, prev, next) {
    const nextRoute = next
      ? `/m/${site}/${titleId}/${next.id}`
      : `/m/${site}/${titleId}`;

    return m("div.chapter--buttons", [
      prev
        ? m(
            m.route.Link,
            {
              class: "touch-friendly chapter--prev-button",
              href: `/m/${site}/${titleId}/${prev.id}`,
            },
            [m("i.icon.icon-chevrons-left"), m("span", "prev")]
          )
        : m(Button, {
            class: "chapter--prev-button",
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
      m(
        m.route.Link,
        {
          class:
            "touch-friendly chapter--next-button" +
            (isMarkingLastChapterAsRead ? " disabled" : ""),
          href: nextRoute,
          disabled: isMarkingLastChapterAsRead,
          onclick: (ev) => {
            if (Auth.isLoggedIn()) {
              if (next) {
                markChapterAsRead(site, titleId, chapter.id);
              } else {
                // If this is the last chapter, make sure to only transition
                // to next route (title details) after the "mark chapter as
                // read" request is done, so that we don't end up showing the
                // last chapter as still unread in the title details route.
                ev.preventDefault();
                isMarkingLastChapterAsRead = true;
                m.redraw();
                markChapterAsRead(site, titleId, chapter.id).finally(() => {
                  isMarkingLastChapterAsRead = false; // proly unnecessary
                  m.route.set(nextRoute);
                });
              }
            }
          },
        },
        [
          m(
            "span",
            next
              ? "next"
              : isMarkingLastChapterAsRead
              ? "finishing..."
              : "finish"
          ),
          isMarkingLastChapterAsRead
            ? null
            : m("i.icon.icon-" + (next ? "chevrons-right" : "check-circle")),
        ]
      ),
    ]);
  }

  return {
    oncreate: (vnode) => {
      document.addEventListener("keypress", onKeyPress);
    },
    onremove: (vnode) => {
      document.removeEventListener("keypress", onKeyPress);
    },
    oninit: (vnode) => {
      document.title = "Manga chapter";
      site = vnode.attrs.site;
      titleId = vnode.attrs.titleId;

      isLoading = true;
      m.redraw();

      ChapterModel.get({
        site: vnode.attrs.site,
        titleId: vnode.attrs.titleId,
        chapterId: vnode.attrs.chapterId,
      })
        .then((resp) => {
          chapter = resp;
          document.title = fullChapterName(chapter);

          // "zip" pages & pages_alt into pendingPages
          if (chapter.pages_alt.length > 0) {
            pendingPages = chapter.pages.map((page, i) => {
              return [page, chapter.pages_alt[i]];
            });
          } else {
            pendingPages = chapter.pages.map((page) => {
              return [page, null];
            });
          }

          // start loading pages, 3 at a time:
          loadNextPage();
          loadNextPage();
          loadNextPage();
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

      return m("div.chapter.content", [
        m("h1", fullChapterName(chapter)),
        buttonsView(site, prev, next),
        m(
          "div",
          {
            class:
              "chapter--pages" +
              (chapter.is_webtoon ? " chapter--webtoon" : ""),
          },
          [
            loadedPages.map((page, pageIndex) =>
              m(
                "div.chapter--page-container",
                {
                  key: page.src,
                  style: {
                    width: `${pageMaxWidth}%`,
                    backgroundColor:
                      pageMaxWidth === 100 ? "transparent" : "#333",
                  },
                },
                [
                  m(FallbackableImg, {
                    src: page.src,
                    altsrc: page.altsrc,
                    style: {
                      display:
                        page.status === ImgStatus.SUCCEEDED ? "inline" : "none",
                    },
                    onload: (ev) => {
                      page.status = ImgStatus.SUCCEEDED;
                      loadNextPage();
                    },
                    onerror: (ev) => {
                      page.status = ImgStatus.FAILED;
                      loadNextPage();
                    },
                  }),
                  page.status === ImgStatus.LOADING
                    ? m(LoadingPlaceholder)
                    : null,
                  page.status === ImgStatus.FAILED
                    ? m(
                        "div",
                        { style: { "margin-bottom": ".5rem" } },
                        m(RetryImgButton, { page })
                      )
                    : null,
                ]
              )
            ),
            pendingPages.map(() => m(PendingPlaceholder)),
          ]
        ),
        buttonsView(site, prev, next),
        nextChapterLoadedPages.map((page) =>
          m(FallbackableImg, {
            style: { display: "none" },
            onload: preloadNextChapterPage,
            onerror: preloadNextChapterPage,
            src: page.src,
            altsrc: page.altsrc,
          })
        ),
      ]);
    },
  };
}

export default Chapter;
