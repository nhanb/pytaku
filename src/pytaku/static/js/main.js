import { Auth } from "./models.js";
import Layout from "./layout.js";
import Authentication from "./routes/authentication.js";
import Home from "./routes/home.js";
import Follows from "./routes/follows.js";

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
      render: () => m(Layout, m(Home)),
    },
    "/a": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          m.route.set("/f", null, { replace: true });
        } else {
          return Authentication;
        }
      },
      render: () => m(Layout, m(Authentication)),
    },
    "/f": {
      onmatch: () => {
        if (Auth.isLoggedIn()) {
          return Follows;
        } else {
          //m.route.set("/a", null, { replace: true });
          return m("h1", "waiting");
        }
      },
      render: () => m(Layout, m(Follows)),
    },
  });
});
