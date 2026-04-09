"""Tests for env_guardian.templates module."""

import pytest
from env_guardian.templates import generate_template, render_template, DEFAULT_PLACEHOLDER


SAMPLE_ENV = {"APP_ENV": "production", "DB_HOST": "db.local", "SECRET_KEY": "s3cr3t"}


def test_generate_template_blanks_values():
    result = generate_template(SAMPLE_ENV)
    assert "APP_ENV=" in result
    assert "production" not in result


def test_generate_template_includes_values():
    result = generate_template(SAMPLE_ENV, include_values=True)
    assert "APP_ENV=production" in result


def test_generate_template_marks_required_keys():
    result = generate_template(SAMPLE_ENV, required_keys=["SECRET_KEY"])
    assert f"SECRET_KEY={DEFAULT_PLACEHOLDER}" in result


def test_generate_template_sorted_keys():
    result = generate_template(SAMPLE_ENV)
    keys = [line.split("=")[0] for line in result.strip().splitlines()]
    assert keys == sorted(keys)


def test_generate_template_empty_env():
    result = generate_template({})
    assert result == ""


def test_render_template_fills_values():
    template = "DB_HOST=\nSECRET_KEY=\n"
    rendered, unfilled = render_template(template, {"DB_HOST": "newhost", "SECRET_KEY": "xyz"})
    assert "DB_HOST=newhost" in rendered
    assert "SECRET_KEY=xyz" in rendered
    assert unfilled == []


def test_render_template_leaves_unmatched_keys():
    template = "DB_HOST=\n"
    rendered, unfilled = render_template(template, {})
    assert "DB_HOST=" in rendered
    assert unfilled == []


def test_render_template_tracks_unfilled_required():
    template = f"SECRET_KEY={DEFAULT_PLACEHOLDER}\n"
    rendered, unfilled = render_template(template, {})
    assert "SECRET_KEY" in unfilled


def test_render_template_strict_raises_on_unfilled():
    template = f"SECRET_KEY={DEFAULT_PLACEHOLDER}\n"
    with pytest.raises(ValueError, match="SECRET_KEY"):
        render_template(template, {}, strict=True)


def test_render_template_strict_passes_when_filled():
    template = f"SECRET_KEY={DEFAULT_PLACEHOLDER}\n"
    rendered, unfilled = render_template(template, {"SECRET_KEY": "safe"}, strict=True)
    assert "SECRET_KEY=safe" in rendered
    assert unfilled == []


def test_render_template_ignores_comment_lines():
    template = "# This is a comment\nAPP_ENV=\n"
    rendered, _ = render_template(template, {"APP_ENV": "test"})
    assert "# This is a comment" in rendered
    assert "APP_ENV=test" in rendered
