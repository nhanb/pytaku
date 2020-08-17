import { Auth } from "./models.js";
import Authentication from "./routes/authentication.js";
import Home from "./routes/home.js";

const root = document.getElementById("spa-root");
m.route.prefix = "";
m.route(root, "/h", {
  "/h": Home,
  "/a": Authentication,
});
Auth.init();
