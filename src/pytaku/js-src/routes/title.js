import { Auth } from "../models.js";
import { LoadingMessage, Button, fullChapterName, Chapter } from "../utils.js";

function Title(initialVNode) {
  let isLoading = false;
  let isTogglingFollow = false;
  let isMarkingAllAsRead = false;
  let isMarkingAllAsUnread = false;
  let isMarkingAsReadStartingFrom = null;
  let title = {};
  let allAreRead;
  let allAreUnread;
  let readUpTo;

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
      if (!isLoading && Auth.isLoggedIn()) {
        allAreRead = true;
        allAreUnread = true;
        readUpTo = title.chapters.length; // biggest index + 1

        for (var i = title.chapters.length - 1; i >= 0; i--) {
          const chap = title.chapters[i];
          if (chap.is_read) {
            if (readUpTo === i + 1) readUpTo = i;
            allAreUnread = false;
          } else {
            allAreRead = false;
          }
        }
      }
      return m(
        "div.content",
        isLoading
          ? m(LoadingMessage)
          : [
              m("h1", title.name),
              m("div.title--details", [
                Auth.isLoggedIn()
                  ? [
                      m(Button, {
                        icon: "bookmark",
                        disabled: isTogglingFollow ? "disabled" : null,
                        text: isTogglingFollow
                          ? "submitting..."
                          : title.is_following
                          ? "following"
                          : "follow",
                        color: title.is_following ? "red" : "green",
                        title: title.is_following
                          ? "Click to unfollow"
                          : "Click to follow",
                        onclick: (ev) => {
                          isTogglingFollow = true;
                          m.redraw();
                          Auth.request({
                            method: "POST",
                            url: "/api/follow",
                            body: {
                              site: title.site,
                              title_id: title.id,
                              follow: !title.is_following,
                            },
                          })
                            .then((resp) => {
                              title.is_following = resp.follow;
                            })
                            .finally(() => {
                              isTogglingFollow = false;
                            });
                        },
                      }),
                      m(Button, {
                        icon: "check-square",
                        disabled:
                          isMarkingAllAsRead || allAreRead ? "disabled" : null,
                        text: isMarkingAllAsRead
                          ? "submitting..."
                          : allAreRead
                          ? "all read!"
                          : "read all",
                        color: "green",
                        title: allAreRead
                          ? null
                          : "Click to mark all chapters as read",
                        onclick: (ev) => {
                          const confirmed = window.confirm(
                            "Are you sure you want to read all chapters?"
                          );
                          if (!confirmed) {
                            return;
                          }
                          isMarkingAllAsRead = true;
                          m.redraw();
                          Auth.request({
                            method: "POST",
                            url: "/api/read",
                            body: {
                              read: title.chapters
                                .filter((ch) => !ch.is_read)
                                .map((ch) => {
                                  return {
                                    site: title.site,
                                    title_id: title.id,
                                    chapter_id: ch.id,
                                  };
                                }),
                            },
                          })
                            .then((resp) => {
                              title.chapters.forEach((chap) => {
                                chap.is_read = true;
                              });
                            })
                            .finally(() => {
                              isMarkingAllAsRead = false;
                            });
                        },
                      }),
                      m(Button, {
                        icon: "x-square",
                        disabled:
                          isMarkingAllAsUnread || allAreUnread
                            ? "disabled"
                            : null,
                        text: isMarkingAllAsUnread
                          ? "submitting..."
                          : allAreUnread
                          ? "all unread!"
                          : "unread all",
                        color: "white",
                        title: allAreUnread
                          ? null
                          : "Click to mark all chapters as unread",
                        onclick: (ev) => {
                          const confirmed = window.confirm(
                            "Are you sure you want to unread all chapters?"
                          );
                          if (!confirmed) {
                            return;
                          }
                          isMarkingAllAsUnread = true;
                          m.redraw();
                          Auth.request({
                            method: "POST",
                            url: "/api/read",
                            body: {
                              unread: title.chapters
                                .filter((ch) => ch.is_read)
                                .map((ch) => {
                                  return {
                                    site: title.site,
                                    title_id: title.id,
                                    chapter_id: ch.id,
                                  };
                                }),
                            },
                          })
                            .then((resp) => {
                              title.chapters.forEach((chap) => {
                                chap.is_read = false;
                              });
                            })
                            .finally(() => {
                              isMarkingAllAsUnread = false;
                            });
                        },
                      }),
                    ]
                  : null,
                m(
                  "a.touch-friendly[title=Go to source site][target=_blank]",
                  { href: title.source_url },
                  [title.site, m("i.icon.icon-arrow-up-right")]
                ),
              ]),
              m("img.title--cover[alt=cover]", { src: title.cover }),
              m(".title--descriptions", {}, [
                title.descriptions.map((desc) =>
                  m(
                    "p",
                    title.descriptions_format === "html" ? m.trust(desc) : desc
                  )
                ),
              ]),
              title.chapters
                ? title.chapters.map((chapter, index) =>
                    m(".title--chapter-row", [
                      index < readUpTo
                        ? m(Button, {
                            icon:
                              isMarkingAsReadStartingFrom !== null &&
                              index >= isMarkingAsReadStartingFrom
                                ? "loader"
                                : "chevrons-down",
                            color: "green",
                            title: "Mark all read up to this chapter",
                            disabled:
                              isMarkingAsReadStartingFrom !== null &&
                              index >= isMarkingAsReadStartingFrom
                                ? "disabled"
                                : null,
                            onclick: (ev) => {
                              const confirmed = window.confirm(
                                "Are you sure you want to mark all chapters up to this point as read?"
                              );
                              if (!confirmed) return;

                              isMarkingAsReadStartingFrom = index;
                              m.redraw();

                              const chaptersToMark = title.chapters
                                .slice(index)
                                .filter((ch) => !ch.is_read);

                              if (chaptersToMark.length == 0) {
                                isMarkingAsReadStartingFrom = null;
                                m.redraw();
                                return;
                              }

                              Auth.request({
                                method: "POST",
                                url: "/api/read",
                                body: {
                                  read: chaptersToMark.map((ch) => {
                                    return {
                                      site: title.site,
                                      title_id: title.id,
                                      chapter_id: ch.id,
                                    };
                                  }),
                                },
                              })
                                .then((resp) => {
                                  chaptersToMark.forEach((chap) => {
                                    chap.is_read = true;
                                  });
                                })
                                .finally(() => {
                                  isMarkingAsReadStartingFrom = null;
                                });
                            },
                          })
                        : null,
                      m(Chapter, {
                        site: title.site,
                        titleId: title.id,
                        chapter,
                      }),
                    ])
                  )
                : m("p", "This one has no chapters."),
            ]
      );
    },
  };
}

export default Title;
