"""Namaste Great Finds (namastegreatfinds.com): a gift and finds shop across the whole Namaste Bookshop catalog, everything $60 and under,
organized by price and by the kind of person you are buying for. Copy written for this site only."""
import re, types
E = __import__('html').escape
ICON = 'tag'
FAM_LABEL, FAM_ALL, STYLE_LABEL, STYLE_ALL = 'Good for', 'Anyone', 'Kind', 'All kinds'
NO_FAMILY = ()
MAX_PRICE = 60
READINGS = 'https://namastebookshop.com/pages/book-a-reading'
_T = {
 'crystal': ['Crystal Carving', 'crystal Heart', 'Crystal Sphere', 'Spirit Animals', 'Crystal Gem Tree', 'Crystal Tower Obeliak', 'Crystal Tower Obeliak Generator', 'Crystal Points', 'Crystal Tumbled',
             'Crystal Palmstone Gallet', 'Crystal Gallet', 'Worry Stones Crystals', 'Worry Stone', 'Palm Stone', 'Clusters Crystal', 'Crystal Geode', 'Free Form Crystals', 'Aura Quartz Points, Cluster, Tower',
             'Aura Quartz Points, Cluster, Tower, Heart', 'Crystal Skulls', 'Crystal Eggs', 'Pyramid', 'Orgone Pyramids', 'Merkaba Crystal', 'Cube Crystal', 'Crystal Wand', 'Crystal Rough Raw', 'Crystals Specimens', 'Crystal'],
 'jewelry': ['Crystal Bead Bracelets', 'Ring', 'Adjustable Base Metal Ring', 'Pendant', 'Plated Stone Pendant', 'Necklace', 'Sterling Silver Pendant', 'Wire Wrapped Pendant', 'Crystal Pendant', 'Sterling Silver RIngs',
             'Domed Band Rings', 'Plated Stone Earrings', 'Copper Bracelet /Cuff', 'Plated Stone Ring', 'Plated Pendant', 'Crystal Jewelry', 'SS Wire Wrap Pendant', 'Adjustable String Bracelet', 'Black Cord Stone Necklace',
             'Charm', 'Anklet', 'Beads Ring', 'Crystal Bracelet', 'Crystal Beads Mala', 'Brass Earrings', 'Earrings', 'Crystal Necklace', 'Adjustable Sterling Silver Bracelet', 'Shawls , Scarves, Sarong', 'Copper Pendant',
             'Pendant Carded', 'Stainless Steel Rings', 'Adjustable Chain Bracelet', 'Steel/Leather Bracelet', 'Sterling Silver Necklace', 'Crystal Mala', 'Plated Stone Necklace', 'Stainless Steel Bracelet',
             'Vegan Leather Bracelet', 'Copper Ring', 'Bangle', 'Cuff Crystal Bracelets', 'Bracelet', 'Keychains', 'Keychain', 'Mood Ring', 'Crystal Heart Pendant', 'Waist Beads'],
 'decor': ['Statue', 'Wall Hanging', 'Dreamcatchers', 'Suncatchers', 'Incense Holder', 'Incense Burner', 'Oil Burner', 'Diya', 'Wood Storage Box', 'Jewelry Decor Box', 'Offering Bowls', 'Chalice Cup', 'Goblet',
           'Mirror', 'Ornament', 'Wall Poster', 'Decorative Glassware', 'Crystal Bowl', 'Mortar & Pestle'],
 'selfcare': ['Essential Oils', 'Roll On Fragrance Oil', 'Aroma Oil', 'Fragrance Oil', 'Soaps', 'Soap', 'Room Spray', 'Aromatherapy Inhaler', 'Smudge Sprays Fine Mists', 'Flower Essence', 'Bath Salt',
              'Therapy Ball', 'Massager Crystal Gua Sha', 'Gua Sha', 'Henna', 'Meditation & Wellness', 'Spiritual Spray'],
 'cards': ['Tarot Deck', 'Oracle Cards', 'Oracle Deck', 'Lenormand Deck', 'Mini Deck', 'Affirmation Deck', 'Affirmation Cards', 'Inspirational Cards', 'Inspiration Cards', 'Tarot Set', 'Tarot Kit', 'Playing Cards',
           'Pendulum', 'Pendulum Board', 'Scrying Mirror', 'Dowsing Rod', 'Tarot Talisman', 'Celtic Oracle Deck', 'Dream Oracle Deck', 'Astrology Oracle Deck'],
 'ritual': ['Candle', 'Candles', 'Reiki Herbal Pillar Candle', 'Soy Herbal Votive Candle', 'Ritual Candle', 'Candle Holder', 'Resin Incense', 'Sage', 'Smudging', 'Palo Santo', 'Incense Chips',
            'Spiritual Kit & Bundle', 'Energy Cleansing Kit', 'chakra Stone Kit Set', 'Chakra Kit', 'Sacred Geometry Set', 'Cleansing Water'],
 'paper': ['Journals', 'Greeting Cards', 'Almanacs & Calendars', 'Notebooks/ Blank/ Hand Made', 'calligraphy kit', 'Info Charts', 'Pins', 'Magnets', 'Tokens'],
 'sound': ['Hand Bells', 'Brass Singing Bowl', 'Chimes', 'Musical instruments', 'Instruments', 'Tuning Fork', 'Singing Bowl Mallet'],
}
_T2 = {t: k for k, ts in _T.items() for t in ts}
def category(p):
    c = _T2.get(p.get('product_type', ''))
    if not c: return None
    pr = [float(v['price']) for v in p['variants'] if v['available'] and float(v['price']) > 0]
    if not pr or min(pr) > MAX_PRICE: return None
    if re.search(r'\b(wholesale|bulk|lot of|\d{2,} ?pcs|display box|refill)\b', p['title'], re.I): return None
    return c
def assign(x): return x['base']
FAMILIES = [
 ('crystal-lover', 'The crystal lover', r'crystal|quartz|amethyst|stone|gem|selenite|agate|jasper|obsidian|tourmaline|citrine'),
 ('tarot-reader', 'The tarot reader', r'tarot|oracle|lenormand|pendulum|scrying|divination|rune'),
 ('stargazer', 'The stargazer', r'moon|star|zodiac|celestial|astrolog|sun\b|cosmic|galaxy|planet|aries|taurus|gemini|cancer|leo\b|virgo|libra|scorpio|sagittar|capricorn|aquarius|pisces'),
 ('meditator', 'The meditator', r'buddha|meditat|om\b|mala|singing bowl|zen|lotus|yoga|chakra|bell|ganesh|tibet'),
 ('self-care', 'Self-care', r'lavender|bath|soap|oil|spray|mist|aroma|massag|gua sha|sleep|relax|calm|rose water'),
 ('luck-love', 'Luck & love', r'luck|money|evil eye|hamsa|elephant|fortune|prosper|abundance|love|heart|rose'),
 ('witchy', 'The witchy one', r'witch|spell|ritual|altar|sage|smudge|pentacle|pentagram|chalice|athame|cauldron|hex|wicca'),
]
def style_of(t, b, base): return ''
BR = types.SimpleNamespace(NAME={}, brand_of=lambda t, v='': '', FACTS={})
NAV_BRANDS = False
AISLES = {
 'crystal':  ('Crystal Gifts', 'Crystals', 'crystal-gifts', 'Hearts, spheres, spirit animals, gem trees, towers and pocket stones.', '#7b5cff'),
 'jewelry':  ('Jewelry & Accessories', 'Jewelry', 'jewelry-gifts', 'Bracelets, rings, pendants, earrings, malas, keychains and scarves.', '#d6457a'),
 'decor':    ('Home & Altar Decor', 'Home', 'home-altar-decor', 'Statues, wall hangings, dreamcatchers, burners, bowls and boxes.', '#2e86ab'),
 'selfcare': ('Self-Care & Aromatherapy', 'Self-care', 'self-care-gifts', 'Essential oils, roll-ons, soaps, mists, inhalers and gua sha.', '#2a9d8f'),
 'cards':    ('Tarot, Oracle & Divination', 'Decks', 'tarot-oracle-gifts', 'Tarot and oracle decks, mini decks, pendulums and boards.', '#5a3e8a'),
 'ritual':   ('Candles, Sage & Ritual Kits', 'Ritual', 'candles-sage-ritual-kits', 'Candles and holders, sage, palo santo, resin and ready-made ritual kits.', '#e07a1f'),
 'paper':    ('Cards, Journals & Little Things', 'Paper', 'journals-cards-little-things', 'Journals, greeting cards, calendars, magnets, pins and charts.', '#8a6d3b'),
 'sound':    ('Bells, Bowls & Chimes', 'Sound', 'singing-bowls-bells-chimes', 'Brass singing bowls, hand bells, chimes and tuning forks.', '#b08900'),
}
VISIT_EYEBROW = 'Shopping for a gift in Manhattan?'
def STORE_DESC(S): return f'Gift and finds shop with about {S.ABOUT_N:,} gifts $60 and under, sorted by price and recipient, picked up inside Namaste Bookshop near Union Square or shipped from NYC.'
REVIEW_TITLE = 'Found a great gift?'
REVIEW_TEXT = 'A quick Google review helps other gift hunters find us.'
LOGO_SVG = '<svg viewBox="0 0 40 40"><rect x="7" y="16" width="26" height="19" rx="2" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M5 11h30v6H5zM20 11v24" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M20 11c-3-6-10-6-8-1 1 2 8 1 8 1zm0 0c3-6 10-6 8-1-1 2-8 1-8 1z" fill="#ff6b6b"/></svg>'
WORDMARK = 'Namaste <b>Great Finds</b>'
BAR_TEXT = 'Gifts & finds'
SEARCH_PLACEHOLDER = 'Search gifts: evil eye, buddha, journal'
QUIZ = {
 'slug': 'gift-finder', 'nav': 'Gift finder', 'cta': 'Find a gift',
 'title': 'Gift Finder: 3 Questions to the Right Gift', 'desc': 'Tell us who it is for, what kind of thing and your budget, and see gifts in stock today.',
 'h1': 'Find the right gift', 'lead': 'Three taps: who is it for, what kind of thing, and how much you want to spend. Your answers stay on this page.', 'submit': 'Show gifts',
 'questions': [
  {'q': 'Who is it for?', 'options': [{'label': k[1], 'filter': {'fam': [k[0]]}} for k in FAMILIES] + [{'label': 'Not sure yet', 'filter': {}}]},
  {'q': 'What kind of thing?', 'options': [{'label': 'Something to wear', 'filter': {'aisle': ['jewelry']}}, {'label': 'Something for their home', 'filter': {'aisle': ['decor', 'crystal', 'sound']}},
    {'label': 'Something to use', 'filter': {'aisle': ['selfcare', 'ritual', 'cards', 'paper']}}, {'label': 'Surprise me', 'filter': {}}]},
  {'q': 'Budget?', 'options': [{'label': 'Under $10', 'filter': {'maxp': 10}}, {'label': 'Under $25', 'filter': {'maxp': 25}}, {'label': 'Under $50', 'filter': {'maxp': 50}}]},
 ]}
def FOOTER_EXPLORE(S):
    return [('Gifts under $10', '/gifts-under-10/'), ('Gifts under $25', '/gifts-under-25/'), ('Gifts under $50', '/gifts-under-50/'), ('Markdowns', '/markdowns/'),
            ('Gift finder', '/gift-finder/'), ('Gift guide', '/guide/spiritual-gift-ideas/'), ('Book a reading', READINGS)]
FOOT_BLURB = 'Small, surprising gifts from a Manhattan spiritual shop, every one $60 or less, sorted so you can find one fast.'
HERO_BASES = ('jewelry', 'crystal', 'decor', 'selfcare')
def HERO(S):
    return {'eyebrow': 'Gifts $60 and under &middot; Sorted by price and person',
            'h1': 'Great finds, <em>small prices.</em>',
            'lede': f'About {S.ABOUT_N:,} gifts and little treasures from {S.money(S.MIN_PRICE)}, from crystal hearts and evil-eye bracelets to tarot decks, singing bowls and soaps. Pick a price, pick a person, done.',
            'shop_cta': 'Browse all finds'}
def _band(S, lo, hi, aisles=None):
    xs = [x for x in S.by_rank(S.leaders) if lo <= x['price'] < hi and not x['noimg'] and len(x['group']) == 1]
    out, seen = [], {}
    for x in xs:
        if seen.get(x['aisle'], 0) >= 2: continue
        seen[x['aisle']] = seen.get(x['aisle'], 0) + 1; out.append(x)
        if len(out) == 8: break
    return out
def _u10(S): return _band(S, 0, 10)
def _u25(S): return _band(S, 10, 25)
def _u50(S): return _band(S, 25, 50.01)
def _deals(S): return [x for x in S.products if x['compare'] and not x['noimg']][:8]
def _whys(S):
    return [('Everything $60 or less', 'No hunting through big-ticket items. Every find here is gift-priced.'),
            ('Sorted by person', 'The crystal lover, the tarot reader, the meditator: start with who it is for.'),
            (('Same-day pickup in Manhattan', f'Order online, collect inside Namaste Bookshop at 2 W 14th St. {S.READY}.') if S.PICKUP_ON else ('', '')),
            ('Mix and match in one cart', 'Add from any aisle and check out once on Shopify.'),
            ('Real photos and live stock', 'Every find has a photo and is in stock today.'),
            ('Ships from NYC', 'Packed and shipped from New York City.')]
HOME_SECTIONS = [
 {'type': 'collections', 'title': 'Shop by budget', 'items': [
   {'title': 'Under $10', 'blurb': 'Stocking stuffers, pocket stones, little extras.', 'href': '/gifts-under-10/', 'filter': {'maxp': 10}},
   {'title': 'Under $25', 'blurb': 'The sweet spot for a thoughtful gift.', 'href': '/gifts-under-25/', 'filter': {'maxp': 25}},
   {'title': 'Under $50', 'blurb': 'Decks, bowls, bigger crystals and statues.', 'href': '/gifts-under-50/', 'filter': {'maxp': 50}},
   {'title': 'Markdowns', 'blurb': 'Items currently below their usual price.', 'href': '/markdowns/', 'filter': None}]},
 {'type': 'grid', 'title': 'Finds under $10', 'select': _u10, 'href': '/gifts-under-10/', 'link': 'All under $10'},
 {'type': 'collections', 'title': 'Shop by who it is for', 'items': [{'title': n, 'blurb': '', 'href': f'/gifts-for/{k}/', 'filter': {'fam': [k]}} for k, n, _ in FAMILIES[:6]]},
 {'type': 'grid', 'title': 'Finds from $10 to $25', 'select': _u25, 'href': '/gifts-under-25/', 'link': 'All under $25'},
 {'type': 'quiz', 'title': 'Stuck? Try the gift finder', 'text': 'Who it is for, what kind of thing, what budget. Three taps.'},
 {'type': 'grid', 'title': 'Worth the splurge, under $50', 'select': _u50, 'href': '/gifts-under-50/', 'link': 'All under $50'},
 {'type': 'grid', 'title': 'Marked down right now', 'select': _deals, 'href': '/markdowns/', 'link': 'All markdowns'},
 {'type': 'whys', 'title': 'Why gift from here', 'items': _whys},
 {'type': 'visit'},
 {'type': 'review'},
]
def HOME_TITLE(S): return 'Namaste Great Finds | Spiritual Gifts Under $10, $25 & $50'
def HOME_DESC(S): return f'About {S.ABOUT_N:,} gifts $60 and under: crystals, jewelry, tarot decks, singing bowls, candles and self-care, sorted by price and recipient. Ships from NYC or pick up at 2 W 14th St.'
def SHOP_TITLE(S): return 'All Gifts & Finds | Namaste Great Finds'
def SHOP_DESC(S): return f'{S.N:,} gifts from {S.money(S.MIN_PRICE)} to $60. Filter by who it is for, kind and price.'
SHOP_H1 = 'All finds'
def SHOP_SUB(S): return f'{S.N:,} gifts in stock, all $60 or less.'
def AISLE_TITLE(S, k): return f'{AISLES[k][0]} Gifts Under $60 | Namaste Great Finds'
def AISLE_DESC(S, k): return f'{AISLES[k][3]} {S.cat_count[k]} gifts, all $60 or less. Ships from NYC or pick up at 2 W 14th St.'
_FINTRO = {
 'crystal-lover': 'For someone who already has a windowsill of stones: hearts, spheres, carved animals and crystal jewelry.',
 'tarot-reader': 'For the friend who pulls a card every morning: decks, mini decks, pendulums, talismans and cloths.',
 'stargazer': 'For the one who knows everyone\'s sign: moon, star and zodiac pieces.',
 'meditator': 'For a calm corner: Buddhas, malas, singing bowls, bells and chakra pieces.',
 'self-care': 'For a slow evening: oils, soaps, mists, roll-ons and face tools.',
 'luck-love': 'For a new job, a new home or a new love: evil eyes, elephants, hearts and luck charms.',
 'witchy': 'For the practitioner: candles, chalices, altar pieces, sage and spell kits.'}
def LANDINGS(S):
    L = [{'path': f'/gifts-for/{k}/', 'title': f'Gifts for {n.replace("The ", "the ")} Under $60 | Namaste Great Finds', 'desc': f'{S.fam_count[k]} gift ideas for {n.lower().replace("the ", "")}, all $60 or less. {_FINTRO[k]}',
          'h1': f'Gifts for {n.lower().replace("the ", "the ")}' if n.startswith('The') else f'{n} gifts', 'sub': _FINTRO[k], 'filter': {'fam': [k]}} for k, n, _ in FAMILIES if S.fam_count[k] >= 4]
    for p in (10, 25, 50):
        L.append({'path': f'/gifts-under-{p}/', 'title': f'Spiritual Gifts Under ${p} | Namaste Great Finds', 'desc': f'Gifts under ${p}: crystals, jewelry, decks, candles and more, in stock today.',
                  'h1': f'Gifts under ${p}', 'sub': {10: 'Small gifts, stocking stuffers and add-ons.', 25: 'Thoughtful gifts that do not break the bank.', 50: 'Bigger gifts: decks, bowls, statues and display crystals.'}[p], 'filter': {'maxp': p}})
    return L
def GUIDES(S):
    dl = [x for x in S.products if x['compare'] and not x['noimg']]
    md = (S.grid(dl) if dl else '<p>Nothing is marked down today. Check back, or browse <a href="/gifts-under-10/">gifts under $10</a>.</p>')
    return [
     {'path': '/markdowns/', 'title': 'Markdowns: Gifts Below Their Usual Price', 'desc': 'Items currently priced below their regular price, updated daily from live store prices.', 'h1': 'Markdowns', 'wide': True,
      'html': f'<p class="lead">These items are priced below their usual compare-at price today. The list updates every day from live prices.</p>{md}'},
     {'path': '/guide/spiritual-gift-ideas/', 'title': 'Spiritual Gift Ideas for Every Kind of Person', 'desc': 'Gift ideas for crystal lovers, tarot readers, meditators and more, with tips on choosing and price ranges that work.', 'h1': 'Spiritual gift ideas, by person',
      'html': '''<p class="lead">The best spiritual gift matches what the person already does. Start there, not with what is trending.</p>
<h2>For the crystal lover</h2><p>Skip the basic tumbled quartz they already own. Try a carved spirit animal, a crystal heart in an unusual stone, or a gem tree. <a href="/gifts-for/crystal-lover/">See crystal-lover gifts</a>.</p>
<h2>For the tarot reader</h2><p>Readers love a second deck with different art. A mini deck or a pendulum is a safe add-on. <a href="/gifts-for/tarot-reader/">See tarot gifts</a>.</p>
<h2>For the meditator</h2><p>A small brass singing bowl, a mala or a bell for the start of a sit. <a href="/gifts-for/meditator/">See meditator gifts</a>.</p>
<h2>For someone who needs rest</h2><p>An essential oil roll-on, a mist or a gua sha tool. <a href="/gifts-for/self-care/">See self-care gifts</a>.</p>
<h2>When you are not sure</h2><p>Pair a small crystal with a candle, or let them choose: send them to a <a href="https://namastebookshop.com/pages/book-a-reading" rel="noopener">tarot reading</a> at Namaste Bookshop. Or try the <a href="/gift-finder/">gift finder</a>.</p>'''},
    ]
PAIR = {'crystal': ['jewelry', 'ritual'], 'jewelry': ['crystal', 'paper'], 'decor': ['ritual', 'crystal'], 'selfcare': ['ritual', 'crystal'], 'cards': ['ritual', 'crystal'], 'ritual': ['crystal', 'decor'], 'paper': ['crystal', 'selfcare'], 'sound': ['decor', 'ritual']}
CART_PAIR_TITLE = 'Make it a bundle'
REL_BRAND = 'More from {brand}'
REL_SCENT = 'More gifts for {scent}'
REL_PAIR = 'Goes well with'
REL_MORE = 'More {aisle}'
def brand_intro(S, k, st): return ''
def brand_faq(S, k, st): return []
def BRAND_H1(S, k): return S.BRAND_NAME.get(k, k)
def BRAND_TITLE(S, k, st): return f'{S.BRAND_NAME.get(k, k)} | Namaste Great Finds'
def BRAND_DESC(S, k, st): return ''
def BRANDS_TITLE(S): return 'Brands | Namaste Great Finds'
def BRANDS_DESC(S): return 'Brands we carry.'
BRANDS_H1 = 'Brands'
def BRANDS_LEAD(S, n): return ''
def describe(S, x):
    a = AISLES[x['aisle']][0].lower()
    fam = S.FAM_NAME.get(x['family'], '')
    s = [f"{E(x['title'])}, from our {E(a)} aisle at Namaste Great Finds."]
    s.append(f'At {S.money(x["price"])} it sits in our ' + ('under-$10' if x['price'] < 10 else 'under-$25' if x['price'] < 25 else 'under-$50' if x['price'] < 50 else 'under-$60') + ' gift range.')
    if fam: s.append(f'A good pick for {E(fam.lower().replace("the ", "")) if fam.startswith("The") else E(fam.lower()) + " lovers"}. <a href="/gifts-for/{x["family"]}/">More gifts like this</a>.')
    s.append('Wrap it yourself, or pick it up the same day inside Namaste Bookshop, 2 West 14th Street. Ships from New York City; checkout is on Shopify.')
    return s
def PRODUCT_DESC(S, x, v0): return f"{x['title']}, {S.money(v0['price'])}. A gift-priced find. Ships from NYC or pick up at 2 W 14th St."
def ABOUT_DESC(S): return 'About Namaste Great Finds: gift-priced finds from Namaste Bookshop, run by Wealth Edge Ventures Inc.'
ABOUT_H1 = 'About Namaste Great Finds'
def ABOUT(S):
    return f'''<p class="lead">Namaste Great Finds is the gift table of a Manhattan spiritual shop, online.</p>
<p>We pulled every photographed item priced $60 or less from the Namaste Bookshop shelves, about {S.ABOUT_N:,} of them, and sorted them by price and by the kind of person you are shopping for. Crystals, jewelry, tarot decks, candles, singing bowls, soaps and small things you did not know you needed.</p>
<h2>Who runs it</h2><p>{S.LEGAL} Wealth Edge Ventures also owns Namaste Bookshop, which holds the stock. Checkout runs on Shopify at <a href="{S.SHOP}" rel="noopener">namastebookshop.com</a>.</p>
<h2>Pick up today</h2><p>Every find can be collected inside Namaste Bookshop at {S.STORE_ADDR}. Call <a href="tel:{S.TEL}">{S.PHONE}</a>.</p>{S.hours_html()}{S.visit_buttons()}'''
def FAQ_DESC(S): return 'Questions about Namaste Great Finds: prices, markdowns, gift pickup, shipping and returns.'
FAQ_H1 = 'Gift shop FAQ'
def FAQ(S):
    return [('Why is everything $60 or less?', 'That is the idea: a gift shop where every item is gift-priced, so you never scroll past expensive pieces.'),
            ('Are the markdowns real?', 'Markdowns show items whose live store price is below their usual compare-at price. If none are on sale, the page says so.'),
            ('Can I pick up a gift today?', f'Yes, choose Pickup at checkout and collect inside Namaste Bookshop, {S.STORE_ADDR}.' + (f' {S.READY}.' if S.READY else '')),
            ('Do you gift wrap?', 'Ask at the counter when you pick up; we will help if we can.'),
            ('How does checkout work?', 'Your cart checks out on Shopify through namastebookshop.com, where shipping and pickup options are shown before you pay.')]
NOT_FOUND = 'That find got snapped up'
