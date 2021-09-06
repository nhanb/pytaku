import { Auth, ChapterModel } from "../models.js";
import {
  fullChapterName,
  Button,
  FallbackableImg,
  RetryImgButton,
  ImgStatus,
} from "../utils.js";

const LoadingPlaceholder = {
  view: () => m("h2", [m("i.icon.icon-loader")]),
};

function EInkChapter(initialVNode) {
  let isLoading = false;
  let isMarkingLastChapterAsRead = false;
  let chapter = {};
  let pendingPages = [];
  let loadedPages = [];
  let site, titleId; // these are written on init
  let currentPageIndex = 0;

  let eInkRefreshTimeoutId = null;
  let isInverted = false;

  function loadNextPage() {
    if (pendingPages.length > 0) {
      let [src, altsrc] = pendingPages.splice(0, 1)[0];
      loadedPages.push({
        status: ImgStatus.LOADING,
        src,
        altsrc,
      });
    }
  }

  return {
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
        return m(
          "div.chapter.content",
          m("h2.blink", [m("i.icon.icon-loader.spin"), " loading..."])
        );
      }

      const { site, titleId } = vnode.attrs;
      const prev = chapter.prev_chapter;
      const next = chapter.next_chapter;

      return m(
        ".e-ink-chapter",
        {
          style: {
            position: "absolute",
            backgroundColor: "white",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1,
            textAlign: "center",
          },
        },
        [
          loadedPages.map((page, pageIndex) =>
            m("div", { key: page.src }, [
              m(FallbackableImg, {
                src: page.src,
                altsrc: page.altsrc,
                style: {
                  display:
                    page.status === ImgStatus.SUCCEEDED &&
                    pageIndex === currentPageIndex
                      ? "block"
                      : "none",
                  filter: isInverted ? "invert(1)" : null,
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  margin: "auto",
                  maxHeight: "100%",
                  zIndex: 2,
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
              page.status === ImgStatus.LOADING &&
              pageIndex === currentPageIndex
                ? m(LoadingPlaceholder)
                : null,
              page.status === ImgStatus.FAILED && pageIndex === currentPageIndex
                ? m(
                    "div",
                    { style: { "margin-bottom": ".5rem" } },
                    m(RetryImgButton, { page })
                  )
                : null,
            ])
          ),
          m(".e-ink-chapter--prev-page", {
            onclick: (ev) => {
              if (currentPageIndex > 0) currentPageIndex--;
              if (eInkRefreshTimeoutId !== null) {
                clearTimeout(eInkRefreshTimeoutId);
              }
              isInverted = true;
              eInkRefreshTimeoutId = setTimeout(() => {
                isInverted = false;
                m.redraw();
              }, 450);
            },
          }),
          m(".e-ink-chapter--next-page", {
            onclick: (ev) => {
              if (currentPageIndex < loadedPages.length - 1) currentPageIndex++;
              if (eInkRefreshTimeoutId !== null) {
                clearTimeout(eInkRefreshTimeoutId);
              }
              isInverted = true;
              eInkRefreshTimeoutId = setTimeout(() => {
                isInverted = false;
                m.redraw();
              }, 450);
            },
          }),
        ]
      );
    },
  };
}

export default EInkChapter;
