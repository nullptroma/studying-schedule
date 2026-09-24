// Число страниц PDF титула, склеиваемого перед телом (merge_front_matter.sh).
// Совпадает с FRONT_PAGES. Не подключайте этот файл, если титул рисует Typst.
#let pz-vkr-front-page-count = 3
#counter(page).update(pz-vkr-front-page-count + 1)
