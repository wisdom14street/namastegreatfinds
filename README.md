# namastegreatfinds.com

Namaste Great Finds: static site built daily from the public namastebookshop.com catalog and deployed to GitHub Pages.
Namaste Great Finds is a brand of Wealth Edge Ventures Inc., which also owns Namaste Bookshop (2 W 14th St, New York).

- `site/config.json`: site settings (`REVIEW_URL`, `GOOGLE_SITE_VERIFICATION` stay hidden while empty).
- `site/sitecopy.py`: product mix rules, pages and all copy for this site.
- `scripts/p2site.py`: find-us, sales and link-preview copy.
- `site/theme.css`, `site/favicon.svg`, `src/static/og.jpg`: design and link preview.
- Checkout: cart permalinks to namastebookshop.com tagged with `attributes[Storefront]=Namaste Great Finds`.

## Attribution and review

See [the 2026-11-04 review](REVIEW-2026-11-04.md) for evidence, changes and reporting limits. `checkout_click` and the contact/booking/directions events measure clicks only. Use confirmed Shopify orders and booking-provider records for paid conversion reporting.

## Offline regression checks

The fixture catalog is synthetic, built in a temporary directory and never published. JavaScript tests intercept network requests and do not contact Shopify or GA4.

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
npm install --prefix /tmp/great-finds-qa --cache /tmp/great-finds-npm-cache --ignore-scripts --no-audit --no-fund jsdom@26.1.0
NODE_PATH=/tmp/great-finds-qa/node_modules node --test tests/storefront.test.cjs
```

The standard build dependencies remain `segno` and `pillow`. No runtime JavaScript dependencies were added.
