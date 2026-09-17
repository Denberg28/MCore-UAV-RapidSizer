from app.rapid_cli import build_parser


def test_rapid_cli_exposes_agent_friendly_analyze_command():
    args = build_parser().parse_args(["analyze", "project.json", "--json"])
    assert args.command == "analyze"
    assert args.project == "project.json"
    assert args.as_json is True
