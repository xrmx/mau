from unittest.mock import patch

from mau.parsers.main_parser import MainParser

from tests.helpers import listasdict, init_parser_factory, parser_test_factory, dedent

init_parser = init_parser_factory(MainParser)

_test = parser_test_factory(MainParser)


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            == Header 1.1
            == Header 1.2
            = Header 2
            == Header 2.1
            === Header 2.1.1
            """
        )
    )
    p.parse()

    assert listasdict(p.toc) == [
        {
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                    "value": "Header 1.1",
                },
                {
                    "anchor": "Header 1.2-XXXXXX",
                    "children": [],
                    "value": "Header 1.2",
                },
            ],
            "value": "Header 1",
        },
        {
            "anchor": "Header 2-XXXXXX",
            "children": [
                {
                    "anchor": "Header 2.1-XXXXXX",
                    "children": [
                        {
                            "anchor": "Header 2.1.1-XXXXXX",
                            "children": [],
                            "value": "Header 2.1.1",
                        },
                    ],
                    "value": "Header 2.1",
                },
            ],
            "value": "Header 2",
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc_ignore_headers(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            ==! Header 1.1
            ==! Header 1.2
            = Header 2
            ==! Header 2.1
            ===! Header 2.1.1
            """
        )
    )
    p.parse()

    assert listasdict(p.toc) == [
        {
            "anchor": "Header 1-XXXXXX",
            "children": [],
            "value": "Header 1",
        },
        {
            "anchor": "Header 2-XXXXXX",
            "children": [],
            "value": "Header 2",
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_create_toc_orphan_nodes(header_anchor_mock):
    header_anchor_mock.side_effect = lambda text, level: f"{text}-XXXXXX"

    p = init_parser(
        dedent(
            """
            = Header 1
            === Header 1.1
            == Header 1.2
            """
        )
    )
    p.parse()

    assert [i.asdict() for i in p.toc] == [
        {
            "anchor": "Header 1-XXXXXX",
            "children": [
                {
                    "anchor": "Header 1.1-XXXXXX",
                    "children": [],
                    "value": "Header 1.1",
                },
                {
                    "anchor": "Header 1.2-XXXXXX",
                    "children": [],
                    "value": "Header 1.2",
                },
            ],
            "value": "Header 1",
        },
    ]


@patch("mau.parsers.main_parser.header_anchor")
def test_parse_header_not_in_toc(header_anchor_mock):
    header_anchor_mock.return_value = "XXXXXX"

    source = """
    =! Title of the section
    """

    expected = [
        {
            "type": "header",
            "args": [],
            "kwargs": {},
            "value": "Title of the section",
            "level": 1,
            "anchor": "XXXXXX",
        }
    ]

    p = _test(source, expected)

    assert listasdict(p.toc) == []