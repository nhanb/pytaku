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

export {
  LoadingMessage,
  Button,
  Chapter,
  truncate,
  fullChapterName,
  FallbackableImg,
  RetryImgButton,
  ImgStatus,
};
