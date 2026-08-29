from scripts.validate_citations import normalize, extract_cards, check_card

CHAPTER_MD = """# 第 1 章 投资与投机：聪明投资者的预期收益

<!-- page: pdf=30 book=12 -->

投资操作是指经过透彻分析，能够保证本金安全并获得满意回报的操作。
"""

GOOD_CARD = """---
id: P-01-01
type: principle
chapter: 1
pages: [12, 14]
importance: core
modernity: timeless
---
# 投资三要素

**原文引证**（书页 p.12）：“投资操作是指经过透彻分析，能够保证本金安全并获得满意回报的操作。”
"""

BAD_CARD = """---
id: P-01-02
type: principle
chapter: 1
pages: [12, 14]
importance: core
modernity: timeless
---
# 伪造引证

**原文引证**（书页 p.12）：“格雷厄姆从未说过这句话。”
"""


def test_normalize():
    assert normalize("a b　c\nd") == "abcd"


def test_extract_cards():
    cards = extract_cards(GOOD_CARD + "\n" + BAD_CARD)
    assert len(cards) == 2


def test_check_card_pass():
    assert check_card(extract_cards(GOOD_CARD)[0], {1: CHAPTER_MD}) is None


def test_check_card_fail():
    err = check_card(extract_cards(BAD_CARD)[0], {1: CHAPTER_MD})
    assert err is not None and "P-01-02" in err


def test_extract_cards_crlf():
    crlf = GOOD_CARD.replace("\n", "\r\n")
    cards = extract_cards(crlf)
    assert len(cards) == 1
    assert check_card(cards[0], {1: CHAPTER_MD}) is None
