import { Auth } from "./models.js";
import Layout from "./layout.js";
import Authentication from "./routes/authentication.js";
import Home from "./routes/home.js";
import Follows from "./routes/follows.js";
import Search from "./routes/search.js";
import Title from "./routes/title.js";
import Chapter from "./routes/chapter.js";
import Importer from "./routes/importer.js";

Auth.init().then(() => {
  const root = document.getElementById("spa-root");
  m.route.prefix = "";
  m.route(root, "/", {
    "/": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          m.route.set("/f", null, { replace: true });
        } else {
          return Home;
        }
      },
      render: (vnode) => m(Layout, vnode),
    },
    "/a": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          m.route.set("/f", null, { replace: true });
        } else {
          return Authentication;
        }
      },
      render: (vnode) => m(Layout, vnode),
    },
    "/f": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          return Follows;
        } else {
          m.route.set("/a", null, { replace: true });
        }
      },
      render: (vnode) => m(Layout, vnode),
    },
    "/s/:query": {
      render: (vnode) =>
        m(
          Layout,
          m(Search, {
            query: vnode.attrs.query,
            key: vnode.attrs.query,
            // ^ set a key here to reinitialize Search component on route
            // change. Without it, Search.oninit would only trigger once on
            // first full page load.
          })
        ),
    },
    "/m/:site/:titleId": {
      render: (vnode) =>
        m(
          Layout,
          m(Title, {
            site: vnode.attrs.site,
            titleId: vnode.attrs.titleId,
          })
        ),
    },
    "/m/:site/:titleId/:chapterId": {
      render: (vnode) =>
        m(
          Layout,
          m(Chapter, {
            site: vnode.attrs.site,
            titleId: vnode.attrs.titleId,
            chapterId: vnode.attrs.chapterId,
            key: vnode.attrs.chapterId,
          })
        ),
    },
    "/i": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          return Importer;
        } else {
          m.route.set("/a", null, { replace: true });
        }
      },
      render: (vnode) => m(Layout, vnode),
    },
  });
});
