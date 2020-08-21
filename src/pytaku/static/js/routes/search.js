import { Auth, SearchModel } from "../models.js";
import { LoadingMessage, truncate } from "../utils.js";

const Search = {
  oninit: (vnode) => {
    document.title = `"${vnode.attrs.query}" search results`;
    SearchModel.performSearch(vnode.attrs.query);
  },
  view: (vnode) => {
    return m(
      "div.content",
      SearchModel.isLoading
        ? m(LoadingMessage)
        : Object.entries(SearchModel.result).map(([site, titles]) =>
            m("div", [
              m("h1.search--site-heading", site),
              titles
                ? m("p.search--result-text", [
                    "Showing ",
                    m("strong", titles.length),
                    ` result${titles.length > 1 ? "s" : ""} for `,
                    SearchModel.query,
                  ])
                : m(
                    "p.search--result-text",
                    `No results for "${SearchModel.query}"`
                  ),
              m(
                "div.search--results",
                titles.map((title) =>
                  m(
                    m.route.Link,
                    {
                      class: "search--result",
                      href: `/m/${site}/${title.id}`,
                      title: title.name,
                    },
                    [
                      m("img", { src: title.thumbnail, alt: title.name }),
                      m("span", truncate(title.name, 50)),
                    ]
                  )
                )
              ),
            ])
          )
    );
  },
};

export default Search;
