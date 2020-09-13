const LoadingMessage = {
  view: (vnode) => m("h2.blink", [m("i.icon.icon-loader.spin"), " loading..."]),
};

const Button = {
  view: (vnode) =>
    m(
      "button",
      Object.assign({ class: vnode.attrs.color || "" }, vnode.attrs),
      [
        vnode.attrs.icon ? m(`i.icon.icon-${vnode.attrs.icon}`) : null,
        vnode.attrs.text ? m("span", vnode.attrs.text) : null,
      ]
    ),
};

const Chapter = {
  view: (vnode) =>
    m("div.utils--chapter", [
      m(
        m.route.Link,
        {
          href: `/m/${vnode.attrs.site}/${vnode.attrs.titleId}/${vnode.attrs.chapter.id}`,
          class: "touch-friendly",
        },
        [
          vnode.attrs.chapter.is_read
            ? m("i.icon.icon-check-square.utils--chapter--read-icon")
            : null,
          m("span", fullChapterName(vnode.attrs.chapter)),
          vnode.attrs.chapter.groups.map((group) =>
            m("span.utils--chapter--group", truncate(group, 20))
          ),
        ]
      ),
    ]),
};

function truncate(input, size) {
  return input.length > size ? `${input.substring(0, size)}...` : input;
}

function fullChapterName(chapter) {
  let result = "";
  if (typeof chapter.num_major !== "undefined") {
    result += (chapter.volume ? "Ch." : "Chapter ") + chapter.num_major;
  }
  if (chapter.num_minor) {
    result += "." + chapter.num_minor;
  }
  if (chapter.volume) {
    result += " Vol. " + chapter.volume;
  }
  if (chapter.name) {
    result += " - " + chapter.name;
  }
  return result;
}

export { LoadingMessage, Button, Chapter, truncate, fullChapterName };
