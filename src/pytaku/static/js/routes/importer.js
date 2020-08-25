import { Auth } from "../models.js";
import { Button } from "../utils.js";

function Importer(initialVNode) {
  let resultMessage = null;
  let isSuccess = null;
  let isUploading = false;

  return {
    oninit: (vnode) => {
      document.title = "Import from Tachiyomi";
    },
    view: (vnode) => {
      return m("div.content", [
        m("h1", "Importing from Tachiyomi"),
        m(
          "form[enctype=multipart/form-data]",
          {
            onsubmit: (ev) => {
              ev.preventDefault();
              // prepare multipart form body
              const file = document.getElementById("tachiyomi").files[0];
              const body = new FormData();
              body.append("tachiyomi", file);

              isUploading = true;
              resultMessage = null;
              m.redraw();
              Auth.request({
                method: "POST",
                url: "/api/import",
                body,
              })
                .then((resp) => {
                  resultMessage = resp.message;
                  isSuccess = true;
                })
                .catch((err) => {
                  resultMessage = err.response.message;
                  isSuccess = false;
                })
                .finally(() => {
                  isUploading = false;
                });
            },
          },
          [
            m("p", [
              "Go to ",
              m("b", "Settings > Backup > Create backup"),
              ", then upload the generated json file here:",
            ]),
            m("input[type=file][id=tachiyomi].importer--filepicker"),
            m("br"),
            m(Button, {
              type: "submit",
              text: isUploading ? "uploading..." : "upload",
              color: "green",
              icon: "upload",
              disabled: isUploading ? "disabled" : null,
            }),
          ]
        ),
        m(
          "p",
          { class: `importer--${isSuccess ? "success" : "failure"}` },
          resultMessage
        ),
        isSuccess
          ? m(m.route.Link, { href: "/f" }, "See your following list here.")
          : null,
      ]);
    },
  };
}

export default Importer;
