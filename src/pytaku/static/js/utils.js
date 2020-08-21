const LoadingMessage = {
  view: (vnode) => m("h2.blink", [m("i.icon.icon-loader.spin"), " loading..."]),
};

const truncate = (input, size) =>
  input.length > size ? `${input.substring(0, size)}...` : input;

export { LoadingMessage, truncate };
