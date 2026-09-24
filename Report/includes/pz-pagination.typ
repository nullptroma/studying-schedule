// Номера внизу: скрыты до первой страницы после «Содержания»; счётчик page не сбрасывается.
#let pz_pagination_from_page = state("pz-pagination-from-page", 0)

#let pz_enable_pagination() = context {
  pz_pagination_from_page.update(here().page())
}

#let pz_page_footer = context {
  let from-page = pz_pagination_from_page.at(here())
  if from-page == 0 or here().page() < from-page {
    []
  } else {
    align(center)[#counter(page).display()]
  }
}
