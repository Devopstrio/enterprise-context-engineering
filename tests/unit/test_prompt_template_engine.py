def test_register_and_render_template(template_engine):
    template_engine.register_template("test", "1.0", "Hello {{name}}", ["name"])
    res = template_engine.render_template("test", {"name": "World"})
    assert res.rendered_text == "Hello World"
    assert "name" in res.variables_used


def test_render_with_missing_variables(template_engine):
    res = template_engine.render_template("default_system", {})
    assert res.rendered_text == ""  # Missing is replaced with empty


def test_list_templates(template_engine):
    templates = template_engine.list_templates()
    assert "default_system" in templates
    assert "rag_augmented" in templates


def test_default_templates_registered(template_engine):
    t = template_engine.get_template("default_system")
    assert t["version"] == "1.0"
