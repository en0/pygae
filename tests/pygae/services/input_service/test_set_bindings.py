from pygae.input import IInputService


def test_bind_creates_internal_mapping(input_service: IInputService, make_binding):
    input_binding = make_binding()
    input_service.bind("jump", input_binding)
    assert input_service.get_bindings("jump") == [input_binding]


def test_bind_replaces_internal_mapping(input_service: IInputService, make_binding):
    input_binding = make_binding(id=555)
    input_service.bind("jump", input_binding)
    new_input_bindings = [
        make_binding(id=111),
        make_binding(id=222),
    ]
    input_service.bind("jump", new_input_bindings)
    assert input_service.get_bindings("jump") == new_input_bindings


def test_unbind_removes_internal_mapping(input_service: IInputService, make_binding):
    input_binding = make_binding()
    input_service.bind("jump", input_binding)
    input_service.unbind("jump")
    assert input_service.get_bindings("jump") == []
